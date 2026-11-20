import json

import pytest
from fastapi.testclient import TestClient

import ai
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """Tests run without a real key and with a clean rate limiter."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    ai._hits.clear()


def compose(message, history=None):
    return client.post("/ai/compose", json={"message": message, "history": history or []})


# ---------- website + menu ----------

def test_home_and_assets_are_served():
    assert "Dollop" in client.get("/").text
    assert client.get("/static/css/style.css").status_code == 200
    assert client.get("/static/js/app.js").status_code == 200


def test_full_menu():
    body = client.get("/menu").json()
    assert body["count"] == len(body["items"]) == 18


def test_filter_by_category_and_vegan():
    assert client.get("/menu", params={"category": "SORBET"}).json()["count"] == 5
    vegan = client.get("/menu", params={"vegan": True}).json()["items"]
    assert vegan and all(i["vegan"] for i in vegan)


def test_unknown_category_and_item_are_404():
    assert client.get("/menu", params={"category": "pizza"}).status_code == 404
    assert client.get("/menu/999").status_code == 404


# ---------- Flavor Lab ----------

def test_status_and_featured_work_offline():
    assert client.get("/ai/status").json() == {"mode": "local", "model": None}
    cup = client.get("/ai/featured").json()
    assert cup["items"] and cup["source"] == "local"


def test_compose_returns_a_valid_cup():
    cup = compose("rainy evening, something warm").json()
    ids = [i["id"] for i in cup["items"]]
    assert 1 <= len([i for i in cup["items"] if i["category"] != "toppers"]) <= 3
    assert len(ids) == len(set(ids))
    assert cup["total"] == sum(i["price"] for i in cup["items"])


def test_sold_out_flavor_is_never_chosen():
    ids = [i["id"] for i in compose("I only want paan").json()["items"]]
    assert 8 not in ids


def test_dairy_free_request_is_respected():
    items = compose("hot afternoon, I'm dairy-free").json()["items"]
    assert all(ai.BY_ID[i["id"]]["vegan"] for i in items)


def test_budget_is_respected():
    cup = compose("celebrating, budget under ₹150").json()
    assert 0 < cup["total"] <= 150


def test_message_validation():
    assert compose("hi").status_code == 422
    assert compose("   ").status_code == 422
    assert compose("x" * 301).status_code == 422


def test_rate_limit(monkeypatch):
    monkeypatch.setattr(ai, "RATE_LIMIT", 2)
    assert compose("something sweet").status_code == 200
    assert compose("something sweet").status_code == 200
    assert compose("something sweet").status_code == 429


def test_llm_answer_is_checked_against_the_menu(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test")

    async def fake_groq(messages):
        picks = [999, 8, 2, 3, 3, 15, 16]  # unknown, sold out, ok, ok, repeat, ok topper, second topper
        return json.dumps({"name": "Test Cup", "note": "Fine.", "items": [{"id": i, "why": "x"} for i in picks]})

    monkeypatch.setattr(ai, "call_groq", fake_groq)
    cup = compose("anything").json()
    assert cup["source"] == "groq"
    assert [i["id"] for i in cup["items"]] == [2, 3, 15]


def test_falls_back_when_the_llm_fails(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test")

    async def broken(messages):
        return "not json"

    monkeypatch.setattr(ai, "call_groq", broken)
    assert compose("anything sweet").json()["source"] == "local"
