from typing import List, Dict
from .base import BaseMatcher

class EnsembleMatcher(BaseMatcher):
  def __init__(self, matchers: Dict[str, BaseMatcher], weights: Dict[str, float]):
      self.matchers = matchers
      self.weights = weights

  def match(self, text1: str, text2: str) -> float:
      scores = {name: m.match(text1, text2) for name, m in self.matchers.items()}
      return sum(scores[name] * self.weights[name] for name in scores)