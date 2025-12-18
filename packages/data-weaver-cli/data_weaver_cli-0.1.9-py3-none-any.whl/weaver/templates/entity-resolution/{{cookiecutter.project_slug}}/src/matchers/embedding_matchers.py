from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SentenceTransformerMatcher(BaseMatcher):
  def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
      self.model = SentenceTransformer(model_name)

  def match(self, text1: str, text2: str) -> float:
      embeddings = self.model.encode([text1, text2])
      return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

  def batch_match(self, pairs: List[Tuple[str, str]]) -> List[float]:
      texts = [t for pair in pairs for t in pair]
      embeddings = self.model.encode(texts)
      scores = []
      for i in range(0, len(embeddings), 2):
          sim = cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0]
          scores.append(sim)
      return scores