from __future__ import annotations
from typing import Any, Dict, List, Annotated
from pydantic import BaseModel, Field
from mergedeep import merge

from hzclient.models import *
from hzclient.models.base import _Base


def merge_to_state(model: GameState, data: Dict) -> None:
  """
  Merge data into the game state.
  """
  patch_model = model.__class__.model_validate(data)
  payload = patch_model.model_dump(exclude_unset=True, by_alias=False, include=patch_model.model_fields_set)

  field_names = model.__class__.model_fields.keys()
  current = model.model_dump(by_alias=False, include={name: True for name in field_names})
  merged = merge(current, payload)

  updated = model.__class__.model_validate(merged)
  model.__dict__.update(updated.__dict__)


class GameState(_Base):
  """
  Static game state with explicit blocks.
  """
  debug_field: str = ""

  user: User = User()
  character: Character = Character()

  # Quests
  quest: Quest = Quest()
  quests: List[Quest] = []

  # Trainings
  training: Training = Field(default_factory=Training)
  training_quests: list[TrainingQuest] = []
  trainings: list[Training] = []

  # Resources
  sync_states: Dict[str, Any] = Field(default_factory=dict)


  # Functions
  def update(self, data: Dict) -> None:
    """
    Update the game state with new data.
    """
    merge_to_state(self, data)

  def reset(self, key: str) -> None:
    """
    Reset a specific part of the game state to its default value.
    """
    if key in self.__class__.model_fields:
      default_value = self.__class__.model_fields[key].default
      if default_value is None and self.__class__.model_fields[key].default_factory is not None:
        default_value = self.__class__.model_fields[key].default_factory()
      setattr(self, key, default_value)
    else:
      raise KeyError(f"Key '{key}' not found in GameState")