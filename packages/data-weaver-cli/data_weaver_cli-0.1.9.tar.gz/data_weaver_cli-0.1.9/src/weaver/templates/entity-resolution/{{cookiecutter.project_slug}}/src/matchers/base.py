from abc import ABC, abstractmethod
from typing import List, Tuple

class BaseMatcher(ABC):
  @abstractmethod
  def match(self, text1: str, text2: str) -> float:
      """Return similarity score between 0 and 1"""
      pass

  @abstractmethod
  def batch_match(self, pairs: List[Tuple[str, str]]) -> List[float]:
      """Batch similarity scoring for efficiency"""
      pass