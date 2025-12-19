from pydantic import BaseModel, Field
from typing import Dict, List

class Interaction(BaseModel):
  role: str = Field(..., description="The role of the participant in the interaction, e.g., 'user' or 'agent'.")
  content: str = Field(..., description="The content of the interaction.")
  
class Memory:
  """Abstract memory interface"""
  
  def add(self, interaction: Interaction) -> None:
    """Add an interaction to memory"""
    raise NotImplementedError
  
  def recent(self, n: int = 10) -> List[Interaction]:
    """Retrieve the most recent n interactions from memory"""
    raise NotImplementedError
  
  def to_dict(self, n: int = 10) -> Dict[str, List[Dict[str, str]]]:
    """Retrieve the most recent n interactions as a dictionary"""
    interactions = self.recent(n)
    return {"interactions": [i.model_dump() for i in interactions]}
  
  def as_text(self, n: int = 10) -> str:
    """Retrieve the most recent n interactions as formatted text"""
    interactions = self.recent(n)
    return "\n".join(f"{i.role}: {i.content}" for i in interactions)
  

class InMemoryMemory(Memory):
  """In-memory implementation of the Memory interface"""
  
  def __init__(self):
    self._interactions: List[Interaction] = []
  
  def add(self, interaction: Interaction) -> None:
    self._interactions.append(interaction)
  
  def recent(self, n: int = 10) -> List[Interaction]:
    return self._interactions[-n:]
  
  def to_dict(self) -> Dict[str, List[Dict[str, str]]]:
    return super().to_dict(len(self._interactions))