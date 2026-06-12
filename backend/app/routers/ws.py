from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.database import async_session
from app.services.auth import decode_access_token, get_user_by_id
from app.services.websocket import manager

router = APIRouter(tags=["websocket"])


async def _authenticate_websocket(websocket: WebSocket, token: str) -> int | None:
    user_id = decode_access_token(token)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return None

    async with async_session() as db:
        user = await get_user_by_id(db, int(user_id))
        if user is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
            return None
        return user.id


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token"),
) -> None:
    """
    Real-time notifications for match requests.

    Connect with: ws://localhost:8000/api/v1/ws?token=<access_token>

    Message types:
    - match_request (sent to recipient)
    - match_accepted (sent to requester)
    - match_rejected (sent to requester)
    """
    user_id = await _authenticate_websocket(websocket, token)
    if user_id is None:
        return

    await manager.connect(user_id, websocket)

    try:
        await websocket.send_json({"type": "connected", "user_id": user_id})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception:
        manager.disconnect(user_id)
        raise
