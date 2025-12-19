from pydantic import BaseModel
from typing import Dict, Any, Optional, List, Protocol

from .memory import Memory, InMemoryMemory, Interaction
from .skills import SkillRegistry, SkillFn
from .profiles import DEFAULT_PROFILE


class ChatMessage(BaseModel):
  role: str
  content: str
  metadata: Optional[Dict[str, Any]] = None
  
  
class ChatModelCallable(Protocol):
  def __call__(self, messages: List[ChatMessage], **kwargs) -> str:
    ...
    
    
class PersonaAgent:
  """
  A configurable, persona-based LLM agent with memory and skills.
  """
  
  def __init__(
    self,
    name: str,
    model: ChatModelCallable,
    memory: Optional[Memory] = None,
    skills: Optional[SkillRegistry] = None,
    persona: Optional[Dict[str, Any]] = None,
    system_role: str = "system",
  ):
    self.name = name
    self.model = model
    self.memory = memory or InMemoryMemory()
    self.skills = skills or SkillRegistry()
    self.persona = persona or DEFAULT_PROFILE
    self.system_role = system_role
    
  # --- Skills API ---
  
  def add_skill(self, name: str, fn: SkillFn) -> None:
    self.skills.add_skill(name, fn)
    
  def call_skill(self, name: str, *args, **kwargs) -> Any:
    return self.skills.call(name, *args, **kwargs)
    
  # --- Prompt construction ---
  
  def _system_content(self) -> str:
    persona_desc = (
      f"You are {self.name}, a persona-based LLM agent.\n"
      f"Role: {self.persona.get('role', 'an AI agent')}\n"
      f"Personality: {self.persona.get('personality', 'neutral')}\n"
      f"Style: {self.persona.get('style', 'clear and concise')}\n"
      f"Goals: {', '.join(self.persona.get('goals', []))}\n"
      f"Domain: {self.persona.get('domain', 'general')}\n\n"
    )
    guideline = (
      "Always respond according to the persona described above. "
      "Be explicit when you are uncertain. "
      "Do not claim abilities you do not have.\n"
    )
    return persona_desc + guideline
  
  def _build_messages(self, user_input: str, memory_k: int = 12) -> List[ChatMessage]:
    messages: List[ChatMessage] = [
      ChatMessage(role=self.system_role, content=self._system_content()),
    ]
    
    # Replay recent chat history
    for it in self.memory.recent(memory_k):
      # Ensure role is chat-compatible
      role = it.role if it.role in {"user", "assistant", "system"} else "assistant"
      messages.append(ChatMessage(role=role, content=it.content))
      
    # Current user turn
    messages.append(ChatMessage(role="user", content=user_input))
    return messages
    
  # --- Interaction ---
  
  def react(self, user_input: str, memory_k: int = 5, **model_kwargs) -> str:
    """
    Main entry point: takes user input, builds a persona-aware prompt, calls the model, updates memory, and returns the response.
    """
    messages = self._build_messages(user_input, memory_k)
    response = self.model(messages, **model_kwargs)
    self.memory.add(Interaction(role="user", content=user_input))
    self.memory.add(Interaction(role="assistant", content=response))
    return response