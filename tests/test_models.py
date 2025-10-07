import json
from unittest.mock import MagicMock

from hzclient.state import GameState, merge_to_state
from hzclient.client import Client
from hzclient.session import Session, Response
from hzclient.models import Config, User
from hzclient import CONSTANTS


def mock_request(action: str, *args, **kwargs) -> Response:
  with open(f"tests/data/{action}.json", "r") as f:
    payload = json.load(f)
  return Response(status_code=200, data=payload)

state = GameState()
session = Session(Config(server_id="pl1"))
client = Client(session=session, state=state)
session.request = MagicMock(side_effect=mock_request)


def test_live_reflects_current_state():
  assert state.user.id == 0
  assert state.user.session_id == "0"

  client.login(email="testuser@example.com", password="testpass")
  assert state.user.id == 288


def test_user_model():
  state.user = User(id=123, session_id="abc", premium_currency=50)
  assert state.user.id == 123
  assert state.user.session_id == "abc"
  assert state.user.premium_currency == 50

  state.user.premium_currency += 50
  assert state.user.premium_currency == 100

  merge_to_state(state, {"user": {"premium_currency": 200}})
  assert state.user.premium_currency == 200
  assert state.user.id == 123 # unchanged
  assert state.user.session_id == "abc" # unchanged


def test_character_model():
  assert state.character.name == "JoyfulShieldbearer"


def test_constants():
  assert "quest_energy_refill_amount" in CONSTANTS


def test_state():
  assert state.debug_field == "HelloWorld!"


def test_quests():
  assert isinstance(state.quests, list)
  assert len(state.quests) > 0
  assert state.quests[0].id == 260403


def test_trainings():
  assert isinstance(state.trainings, list)
  assert len(state.trainings) > 0
  assert state.trainings[0].id == 50633

  state.update({
    "trainings": []
  })
  assert len(state.trainings) == 0