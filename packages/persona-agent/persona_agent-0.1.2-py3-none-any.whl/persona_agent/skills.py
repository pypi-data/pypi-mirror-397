from typing import Callable, Dict, List, Any

SkillFn = Callable[..., Any]

class SkillRegistry:
  def __init__(self):
    self._skills: Dict[str, SkillFn] = {}
  
  def add_skill(self, name: str, func: SkillFn) -> None:
    self._skills[name] = func
    
  def has_skill(self, name: str) -> bool:
    return name in self._skills
  
  def call(self, name: str, *args, **kwargs) -> Any:
    if name not in self._skills:
      raise KeyError(f"Skill '{name}' not found.")
    return self._skills[name](*args, **kwargs)
  
  def list_skills(self) -> List[str]:
    return list(self._skills.keys())