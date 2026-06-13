#!/usr/bin/env python3
"""Seed demo users and semantically clustered projects for portfolio matching."""

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

# Projects are grouped by domain so pgvector matching surfaces meaningful collaborators.
DEMO_USERS = [
    {
        "email": "alice@demo.com",
        "username": "alice",
        "password": "demo1234",
        "projects": [
            {
                "title": "ML Recipe Generator",
                "description": (
                    "An AI-powered recipe app using transformer models to suggest meals "
                    "from pantry ingredients, with a React dashboard and FastAPI backend."
                ),
                "skills_needed": "Python, React, ML",
            },
        ],
    },
    {
        "email": "bob@demo.com",
        "username": "bob",
        "password": "demo1234",
        "projects": [
            {
                "title": "Smart Cooking Assistant",
                "description": (
                    "Semantic search over recipes with embedding-based retrieval, pgvector storage, "
                    "and a collaborative meal-planning web interface."
                ),
                "skills_needed": "TypeScript, FastAPI, PostgreSQL",
            },
        ],
    },
    {
        "email": "carol@demo.com",
        "username": "carol",
        "password": "demo1234",
        "projects": [
            {
                "title": "DevOps Metrics Dashboard",
                "description": (
                    "Real-time CI/CD pipeline monitoring with Grafana, Prometheus, "
                    "and automated deployment health checks."
                ),
                "skills_needed": "Go, Kubernetes, Grafana",
            },
        ],
    },
    {
        "email": "dave@demo.com",
        "username": "dave",
        "password": "demo1234",
        "projects": [
            {
                "title": "GitOps Deployment Platform",
                "description": (
                    "Kubernetes-native GitOps controller for zero-downtime releases, "
                    "canary rollouts, and automated rollback on failed health checks."
                ),
                "skills_needed": "Kubernetes, ArgoCD, Terraform",
            },
        ],
    },
    {
        "email": "emma@demo.com",
        "username": "emma",
        "password": "demo1234",
        "projects": [
            {
                "title": "Juvenile Justice Case Platform",
                "description": (
                    "Case management and resource routing for youth in the juvenile justice system, "
                    "connecting public defenders, social workers, and community programs."
                ),
                "skills_needed": "React, Python, PostgreSQL",
            },
        ],
    },
    {
        "email": "james@demo.com",
        "username": "james",
        "password": "demo1234",
        "projects": [
            {
                "title": "Legal Aid Document Assistant",
                "description": (
                    "NLP pipeline to classify court filings and intake forms for legal aid nonprofits, "
                    "priorizing urgent cases and surfacing relevant precedents."
                ),
                "skills_needed": "Python, NLP, FastAPI",
            },
        ],
    },
    {
        "email": "nina@demo.com",
        "username": "nina",
        "password": "demo1234",
        "projects": [
            {
                "title": "Youth Mentorship Network",
                "description": (
                    "Platform matching at-risk teens with mentors and wraparound services "
                    "after detention or foster care transitions."
                ),
                "skills_needed": "React, Node.js, PostgreSQL",
            },
        ],
    },
]


async def upsert_demo_project(db, user: User, project_data: dict) -> None:
    result = await db.execute(
        select(Project).where(Project.user_id == user.id, Project.title == project_data["title"])
    )
    project = result.scalar_one_or_none()

    text = build_embedding_text(
        project_data["title"],
        project_data["description"],
        project_data["skills_needed"],
    )
    embedding = await generate_embedding(text)

    if project is None:
        db.add(
            Project(
                user_id=user.id,
                title=project_data["title"],
                description=project_data["description"],
                skills_needed=project_data["skills_needed"],
                embedding=embedding,
            )
        )
        return

    project.description = project_data["description"]
    project.skills_needed = project_data["skills_needed"]
    project.embedding = embedding


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

            for project_data in entry["projects"]:
                await upsert_demo_project(db, user, project_data)

        await db.commit()

    print("Demo data ready (password for all: demo1234):")
    print("  Food / ML cluster:     alice@demo.com, bob@demo.com")
    print("  DevOps cluster:          carol@demo.com, dave@demo.com")
    print("  Justice / social impact: emma@demo.com, james@demo.com, nina@demo.com")
    print()
    print("Try: alice → ML Recipe Generator → matches bob's cooking project.")
    print("Try: emma → Juvenile Justice → matches james/nina, not bob/carol.")


if __name__ == "__main__":
    asyncio.run(seed())
