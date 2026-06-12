#!/usr/bin/env python3
"""Seed portfolio demo users and semantically similar projects."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import async_session
from app.models.project import Project
from app.models.user import User
from app.services.auth import hash_password
from app.services.embedding import build_embedding_text, generate_embedding

DEMO_USERS = [
    {
        "email": "alice@demo.com",
        "username": "alice",
        "password": "demo1234",
        "project": {
            "title": "ML Recipe Generator",
            "description": (
                "An AI-powered recipe app using transformer models to suggest meals "
                "from pantry ingredients, with a React dashboard and FastAPI backend."
            ),
            "skills_needed": "Python, React, ML",
        },
    },
    {
        "email": "bob@demo.com",
        "username": "bob",
        "password": "demo1234",
        "project": {
            "title": "Smart Cooking Assistant",
            "description": (
                "Semantic search over recipes with OpenAI embeddings, pgvector storage, "
                "and a collaborative meal-planning web interface."
            ),
            "skills_needed": "TypeScript, FastAPI, PostgreSQL",
        },
    },
    {
        "email": "carol@demo.com",
        "username": "carol",
        "password": "demo1234",
        "project": {
            "title": "DevOps Metrics Dashboard",
            "description": (
                "Real-time CI/CD pipeline monitoring with Grafana, Prometheus, "
                "and automated deployment health checks."
            ),
            "skills_needed": "Go, Kubernetes, Grafana",
        },
    },
]


async def seed() -> None:
    async with async_session() as db:
        for entry in DEMO_USERS:
            result = await db.execute(select(User).where(User.email == entry["email"]))
            user = result.scalar_one_or_none()
            if user is None:
                user = User(
                    email=entry["email"],
                    username=entry["username"],
                    hashed_password=hash_password(entry["password"]),
                )
                db.add(user)
                await db.flush()

            project_data = entry["project"]
            existing = await db.execute(
                select(Project).where(Project.user_id == user.id, Project.title == project_data["title"])
            )
            if existing.scalar_one_or_none():
                continue

            text = build_embedding_text(
                project_data["title"],
                project_data["description"],
                project_data["skills_needed"],
            )
            db.add(
                Project(
                    user_id=user.id,
                    title=project_data["title"],
                    description=project_data["description"],
                    skills_needed=project_data["skills_needed"],
                    embedding=await generate_embedding(text),
                )
            )

        await db.commit()

    print("Demo data ready:")
    print("  alice@demo.com / demo1234  — ML Recipe Generator")
    print("  bob@demo.com   / demo1234  — Smart Cooking Assistant")
    print("  carol@demo.com / demo1234  — DevOps Metrics Dashboard")
    print()
    print("Try: log in as alice → Projects → Find matches on her project → see bob's project ranked high.")


if __name__ == "__main__":
    asyncio.run(seed())
