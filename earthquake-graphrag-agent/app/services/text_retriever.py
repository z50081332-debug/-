from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, Iterable, List, Tuple

from app.schemas import EmergencyCase


class SimpleTextRetriever:
    """
    一个轻量 TF-IDF 检索器。
    作用：在没有向量数据库的情况下，先跑通 GraphRAG 中的文本召回流程。
    后续可替换为 Qdrant + embedding 模型。
    """

    def __init__(self, cases: List[EmergencyCase]):
        self.cases = cases
        self.documents = [case.to_text() for case in cases]
        self.doc_tokens = [self.tokenize(doc) for doc in self.documents]
        self.df = self._build_df(self.doc_tokens)
        self.idf = self._build_idf(self.df, len(self.documents))
        self.doc_vectors = [self._tfidf(tokens) for tokens in self.doc_tokens]

    @staticmethod
    def tokenize(text: str) -> List[str]:
        # 中文场景下，为避免分词依赖，这里混合使用关键词、连续中文片段、英文数字和单字。
        text = text.lower()
        words = re.findall(r"[a-zA-Z0-9_.-]+|[\u4e00-\u9fa5]+", text)
        tokens: List[str] = []
        for word in words:
            if re.fullmatch(r"[\u4e00-\u9fa5]+", word):
                tokens.append(word)
                for i in range(len(word) - 1):
                    tokens.append(word[i:i + 2])
                for ch in word:
                    tokens.append(ch)
            else:
                tokens.append(word)
        return tokens

    @staticmethod
    def _build_df(doc_tokens: List[List[str]]) -> Counter:
        df: Counter = Counter()
        for tokens in doc_tokens:
            df.update(set(tokens))
        return df

    @staticmethod
    def _build_idf(df: Counter, n_docs: int) -> Dict[str, float]:
        return {term: math.log((n_docs + 1) / (freq + 1)) + 1.0 for term, freq in df.items()}

    def _tfidf(self, tokens: Iterable[str]) -> Dict[str, float]:
        tf = Counter(tokens)
        if not tf:
            return {}
        max_tf = max(tf.values())
        return {term: (freq / max_tf) * self.idf.get(term, 1.0) for term, freq in tf.items()}

    @staticmethod
    def cosine(v1: Dict[str, float], v2: Dict[str, float]) -> float:
        if not v1 or not v2:
            return 0.0
        common = set(v1) & set(v2)
        dot = sum(v1[t] * v2[t] for t in common)
        n1 = math.sqrt(sum(x * x for x in v1.values()))
        n2 = math.sqrt(sum(x * x for x in v2.values()))
        if n1 == 0 or n2 == 0:
            return 0.0
        return dot / (n1 * n2)

    def search(self, query: str, top_k: int = 3) -> List[Tuple[EmergencyCase, float]]:
        query_vec = self._tfidf(self.tokenize(query))
        scored = []
        for case, vec in zip(self.cases, self.doc_vectors):
            score = self.cosine(query_vec, vec)
            scored.append((case, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
