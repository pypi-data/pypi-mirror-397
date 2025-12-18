from rapidfuzz import fuzz
from typing import List, Tuple
from .base import BaseMatcher

class FuzzyMatcher(BaseMatcher):
  """Levenshtein, Jaro-Winkler, token-based matching"""

  def __init__(self, method: str = "ratio"):
      self.method = getattr(fuzz, method)

  def match(self, text1: str, text2: str) -> float:
      return self.method(text1, text2) / 100.0

  def batch_match(self, pairs: List[Tuple[str, str]]) -> List[float]:
      return [self.match(a, b) for a, b in pairs]