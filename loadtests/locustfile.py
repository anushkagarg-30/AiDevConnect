"""Load test the pgvector matching endpoint.

Run (after seeding):
    locust -f loadtests/locustfile.py --headless -u 50 -r 10 -t 30s \\
        --host http://localhost:8000 --csv=loadtests/results/locust
"""

from __future__ import annotations

import json
from pathlib import Path

from locust import HttpUser, between, task

ENV_PATH = Path(__file__).resolve().parent / ".locust-env.json"


def _load_env() -> dict:
    if not ENV_PATH.exists():
        raise FileNotFoundError(
            f"Missing {ENV_PATH}. Run: python backend/scripts/seed_load_test.py"
        )
    return json.loads(ENV_PATH.read_text())


_ENV = _load_env()


class MatchingUser(HttpUser):
    wait_time = between(0.05, 0.2)

    def on_start(self) -> None:
        self.headers = {"Authorization": f"Bearer {_ENV['token']}"}
        self.project_id = _ENV["project_id"]

    @task
    def find_matches(self) -> None:
        self.client.get(
            f"/api/v1/projects/{self.project_id}/matches",
            headers=self.headers,
            name="/api/v1/projects/[id]/matches",
        )
