#!/usr/bin/env python3
"""Seed users and projects for Locust load testing."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import async_session
from app.models.project import Project
from app.models.user import User
from app.services.auth import create_access_token, hash_password
from app.services.embedding import build_embedding_text, generate_embedding

DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "loadtests" / ".locust-env.json"


async def seed(num_projects: int, output: Path) -> None:
    async with async_session() as db:
        main_user = await _get_or_create_user(
            db,
            email="loadtest@example.com",
            username="loadtest_main",
            password="loadtestpass",
        )
        await db.commit()

        main_project = await _get_or_create_project(
            db,
            user=main_user,
            title="AI DevConnect Load Test",
            description="Semantic matching platform for developer collaboration using pgvector embeddings.",
            skills_needed="Python, FastAPI, React",
        )
        await db.commit()

        created = 0
        for i in range(num_projects):
            user = await _get_or_create_user(
                db,
                email=f"loaduser{i}@example.com",
                username=f"loaduser{i}",
                password="loadtestpass",
            )
            existing = await db.execute(select(Project).where(Project.user_id == user.id))
            if existing.scalars().first():
                continue

            project = Project(
                user_id=user.id,
                title=f"Project {i}",
                description=f"Building a distributed system component #{i} with ML and web technologies.",
                skills_needed="Go, Rust, TypeScript",
                embedding=await generate_embedding(
                    build_embedding_text(
                        f"Project {i}",
                        f"Building a distributed system component #{i} with ML and web technologies.",
                        "Go, Rust, TypeScript",
                    )
                ),
            )
            db.add(project)
            created += 1

            if created % 50 == 0:
                await db.commit()

        await db.commit()

        token = create_access_token(str(main_user.id))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(
                {
                    "token": token,
                    "project_id": main_project.id,
                    "user_id": main_user.id,
                    "seeded_projects": created,
                },
                indent=2,
            )
        )
        print(f"Seeded {created} new projects ({num_projects} target pool). Main project id={main_project.id}")
        print(f"Wrote Locust env to {output}")


async def _get_or_create_user(
    db: AsyncSession,
    email: str,
    username: str,
    password: str,
) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(email=email, username=username, hashed_password=hash_password(password))
    db.add(user)
    await db.flush()
    return user


async def _get_or_create_project(
    db: AsyncSession,
    user: User,
    title: str,
    description: str,
    skills_needed: str,
) -> Project:
    result = await db.execute(select(Project).where(Project.user_id == user.id, Project.title == title))
    project = result.scalar_one_or_none()
    if project:
        return project

    project = Project(
        user_id=user.id,
        title=title,
        description=description,
        skills_needed=skills_needed,
        embedding=await generate_embedding(build_embedding_text(title, description, skills_needed)),
    )
    db.add(project)
    await db.flush()
    return project


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed load test data")
    parser.add_argument("--projects", type=int, default=500, help="Number of filler projects to ensure exist")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    asyncio.run(seed(args.projects, args.output))


if __name__ == "__main__":
    main()
