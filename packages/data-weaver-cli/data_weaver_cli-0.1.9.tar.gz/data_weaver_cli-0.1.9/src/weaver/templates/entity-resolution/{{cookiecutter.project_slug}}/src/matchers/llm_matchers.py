from transformers import pipeline
import re

class LLMClassifierMatcher(BaseMatcher):
  """Zero-shot or fine-tuned classification for matching"""

  def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
      self.model = pipeline("text-classification", model=model_name)

  def match(self, text1: str, text2: str) -> float:
      result = self.model(f"{text1} [SEP] {text2}")
      return result[0]['score']