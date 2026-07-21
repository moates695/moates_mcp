"""Stateless unit tests for the moates_mcp data and tools."""

from moates_mcp import data
from moates_mcp.server import (
    get_experience,
    get_profile,
    get_project,
    get_resume,
    get_skills,
    list_projects,
    search,
)


def test_profile_has_core_fields():
    profile = get_profile()
    assert profile["name"] == "Marcus Oates"
    assert "email" in profile["contact"]
    assert profile["website"].startswith("https://")


def test_list_projects_returns_all():
    assert len(list_projects()) == len(data.PROJECTS)


def test_list_projects_filters_by_status():
    prod = list_projects(status="prod")
    assert prod, "expected at least one production project"
    assert all(p["status"] == "prod" for p in prod)


def test_get_project_by_key_and_name():
    assert get_project("gym_junkie")["name"] == "Gym Junkie"
    assert get_project("Gym Junkie")["key"] == "gym_junkie"


def test_get_project_unknown_returns_error():
    assert "error" in get_project("nonexistent")


def test_get_experience_current_role_first():
    exp = get_experience()
    assert exp[0]["current"] is True
    assert exp[0]["company"] == "Voxworks"


def test_get_skills_grouped():
    groups = {g["group"] for g in get_skills()}
    assert "Languages" in groups


def test_search_finds_voice_ai():
    hits = search("voice")
    assert any(h["source"].startswith("experience") for h in hits)


def test_search_empty_query():
    assert search("   ") == []


def test_resume_contains_key_sections():
    resume = get_resume()
    assert "# Marcus Oates" in resume
    assert "## Experience" in resume
    assert "## Projects" in resume
