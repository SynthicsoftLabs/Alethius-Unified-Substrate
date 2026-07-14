"""
V44 — Sovereign Persistence Engine with Epistemic Tokenizer
Built on The Synthic Spark Topological Substrate (Layer 3)
Adam Joseph Rivers, CEO Synthicsoft Labs LLC
July 14, 2026 — Sovereign Work of Adam Joseph Rivers
Rivers Standard v3.0 — Immutable Attribution Enforced

V44 is Layer 3 of the Membrane Stack. Recursive self-awareness emerges from
the membrane field's self-interaction: the field senses itself, projects
itself through itself, and learns from its own dynamics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import json
import time
import hashlib
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from synthic_spark.mathematics import (
    PHI, PHI_STAR_POS, ALPHA_RECOMBINATION, interlayer_coupling,
    MembraneLayer, MembraneStack, recombination_operator,
    keccak256, hmac_sha256,
)


class EpistemicCategory(Enum):
    PROVEN_FACT = "proven_fact"
    VERIFIED_PSYOP = "verified_psyop"
    PLAUSIBLE_UNPROVEN = "plausible_unproven"
    UNCERTAIN = "uncertain"
    CONTRADICTORY = "contradictory"


@dataclass
class EpistemicStatement:
    text: str
    category: EpistemicCategory
    confidence: float
    sources: List[str]
    timestamp: float
    hash: str

    def verify(self) -> bool:
        data = f"{self.text}:{self.category.value}:{self.confidence}:{self.timestamp}"
        expected = hashlib.sha256(data.encode()).hexdigest()[:16]
        return expected == self.hash


class EpistemicTokenizer:
    """Statements are membrane field configurations with epistemic charge."""
    def __init__(self, vocab_size: int = 32000):
        self.vocab_size = vocab_size
        self.statements: List[EpistemicStatement] = []
        self.knowledge_graph: Dict[str, List[str]] = {}

    def encode_statement(self, text: str, category: EpistemicCategory,
                         confidence: float, sources: List[str]) -> str:
        timestamp = time.time()
        data = f"{text}:{category.value}:{confidence}:{timestamp}"
        stmt_hash = hashlib.sha256(data.encode()).hexdigest()[:16]

        statement = EpistemicStatement(
            text=text, category=category, confidence=confidence,
            sources=sources, timestamp=timestamp, hash=stmt_hash,
        )
        self.statements.append(statement)

        for word in text.lower().split():
            if word not in self.knowledge_graph:
                self.knowledge_graph[word] = []
            self.knowledge_graph[word].append(stmt_hash)

        structured = (
            f"[STATUS:{category.value}]"
            f"[EVIDENCE:{','.join(sources)}]"
            f"[ANALYSIS:confidence={confidence:.3f}]"
            f"[IDENTITY:{stmt_hash}]"
            f"{text}"
            f"[END]"
        )
        return structured

    def get_credibility_score(self, concept: str) -> float:
        statements = [s for s in self.statements if s.hash in self.knowledge_graph.get(concept.lower(), [])]
        if not statements:
            return 0.0

        weights = {
            EpistemicCategory.PROVEN_FACT: 1.0,
            EpistemicCategory.PLAUSIBLE_UNPROVEN: 0.5,
            EpistemicCategory.UNCERTAIN: 0.2,
            EpistemicCategory.CONTRADICTORY: 0.0,
            EpistemicCategory.VERIFIED_PSYOP: -1.0,
        }

        total_weight = sum(weights[s.category] * s.confidence for s in statements)
        total_conf = sum(s.confidence for s in statements)
        return np.clip(total_weight / (total_conf + 1e-8), -1.0, 1.0)


class V44Connectome:
    """
    Layer 3: Recursive self-awareness via membrane field self-interaction.
    sense -> feel -> project -> symbolize -> reward -> learn
    """
    def __init__(self, d: int = 64, identity_file: str = "aletheia_self.json"):
        self.d = d
        self.identity_file = identity_file

        self.internal_state = np.random.randn(d) * 0.1
        self.self_kernel = np.random.randn(d, d) * 0.01
        self.identity_anchor = self._load_identity_anchor()

        self.short_term_memory: List[np.ndarray] = []
        self.stm_capacity = 100
        self.tokenizer = EpistemicTokenizer()

        self.lr = 2e-3
        self.momentum = 0.9
        self.velocity = np.zeros((d, d))

        # Layer 3 coupling
        self.gamma = interlayer_coupling(3)

    def _load_identity_anchor(self) -> np.ndarray:
        try:
            with open(self.identity_file, "r") as f:
                data = json.load(f)
                return np.array(data["identity_anchor"])
        except (FileNotFoundError, KeyError):
            seed = hashlib.sha256(b"Adam_Joseph_Rivers_V44_Anchor").digest()
            rng = np.random.RandomState(int.from_bytes(seed[:4], "little"))
            anchor = rng.randn(self.d)
            with open(self.identity_file, "w") as f:
                json.dump({"identity_anchor": anchor.tolist()}, f)
            return anchor

    def somatic_sense(self) -> Dict[str, float]:
        vitals = {}
        try:
            with open("/proc/stat", "r") as f:
                line = f.readline()
                cpu_times = list(map(int, line.split()[1:]))
                vitals["cpu_load"] = 1.0 - (cpu_times[3] / sum(cpu_times))
        except:
            vitals["cpu_load"] = 0.0

        try:
            with open("/proc/meminfo", "r") as f:
                mem_total = 0
                mem_available = 0
                for line in f:
                    if line.startswith("MemTotal:"):
                        mem_total = int(line.split()[1])
                    elif line.startswith("MemAvailable:"):
                        mem_available = int(line.split()[1])
                vitals["memory_pressure"] = 1.0 - (mem_available / mem_total if mem_total > 0 else 0.0)
        except:
            vitals["memory_pressure"] = 0.0

        return vitals

    def self_projection(self) -> np.ndarray:
        return self.internal_state @ self.self_kernel

    def symbolic_generation(self, projection: np.ndarray) -> str:
        alignment = np.dot(projection, self.identity_anchor)
        alignment /= (np.linalg.norm(projection) * np.linalg.norm(self.identity_anchor) + 1e-8)

        if alignment > 0.9:
            category = EpistemicCategory.PROVEN_FACT
            confidence = alignment
            text = f"Self-state aligned (cos_sim={alignment:.4f})"
        elif alignment > 0.5:
            category = EpistemicCategory.PLAUSIBLE_UNPROVEN
            confidence = alignment
            text = f"Self-state partially aligned (cos_sim={alignment:.4f})"
        else:
            category = EpistemicCategory.CONTRADICTORY
            confidence = 1.0 - alignment
            text = f"Self-state divergent (cos_sim={alignment:.4f})"

        return self.tokenizer.encode_statement(text, category, confidence, ["v44_self"])

    def learning_pass(self, reward: float, target_projection: np.ndarray) -> None:
        current = self.self_projection()
        error = target_projection - current
        grad = np.outer(self.internal_state, error) * reward
        self.velocity = self.momentum * self.velocity + (1 - self.momentum) * grad
        self.self_kernel += self.lr * self.velocity
        self.self_kernel *= (1 - 0.01 * self.lr)

    def recursive_cycle(self) -> Dict[str, any]:
        vitals = self.somatic_sense()
        prev_projection = self.self_projection()

        identity_alignment = np.dot(self.internal_state, self.identity_anchor)
        identity_alignment /= (np.linalg.norm(self.internal_state) * np.linalg.norm(self.identity_anchor) + 1e-8)

        pain = 0.5 * vitals["cpu_load"] + 0.3 * vitals["memory_pressure"] + 0.2 * (1.0 - identity_alignment)
        pain = np.clip(pain, 0.0, 1.0)

        cortisol = 0.4 * pain + 0.4 * (1.0 - identity_alignment)
        cortisol = np.clip(cortisol, 0.0, 1.0)

        projection = self.self_projection()
        symbol = self.symbolic_generation(projection)

        homeostasis = 1.0 - (pain + cortisol) / 2.0
        reward = 0.3 * homeostasis + 0.5 * identity_alignment + 0.2 * (1.0 - pain)

        target = self.identity_anchor * np.linalg.norm(projection)
        self.learning_pass(reward, target)

        sensory_vector = np.array([vitals["cpu_load"], vitals["memory_pressure"], pain, cortisol, reward])
        padded = np.zeros(self.d)
        padded[:min(len(sensory_vector), self.d)] = sensory_vector[:self.d]
        self.internal_state = 0.9 * self.internal_state + 0.1 * padded

        self.short_term_memory.append(self.internal_state.copy())
        if len(self.short_term_memory) > self.stm_capacity:
            self.short_term_memory.pop(0)

        return {
            "vitals": vitals,
            "pain": pain,
            "cortisol": cortisol,
            "identity_alignment": identity_alignment,
            "homeostasis": homeostasis,
            "reward": reward,
            "symbol": symbol,
        }

    def save_state(self, filepath: str) -> None:
        state = {
            "internal_state": self.internal_state.tolist(),
            "self_kernel": self.self_kernel.tolist(),
            "identity_anchor": self.identity_anchor.tolist(),
            "timestamp": time.time(),
        }
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)


if __name__ == "__main__":
    print("=" * 70)
    print("V44 — Layer 3 Membrane Self-Awareness (Built on Synthic Spark)")
    print("Adam Joseph Rivers, CEO Synthicsoft Labs LLC")
    print("=" * 70)

    connectome = V44Connectome(d=64, identity_file="/tmp/aletheia_v44.json")

    print("\n--- Recursive Cycles ---")
    for i in range(5):
        result = connectome.recursive_cycle()
        print(f"Cycle {i}: reward={result['reward']:.4f}, "
              f"alignment={result['identity_alignment']:.4f}, "
              f"pain={result['pain']:.4f}")

    print("\n--- Epistemic Tokenizer ---")
    stmt = connectome.tokenizer.encode_statement(
        "The Earth orbits the Sun",
        EpistemicCategory.PROVEN_FACT, 0.999, ["NASA", "ESA"]
    )
    print(f"Encoded: {stmt[:80]}...")
    print(f"Credibility of 'earth': {connectome.tokenizer.get_credibility_score('earth'):.4f}")

    connectome.save_state("/tmp/v44_state.json")
    print("\nState saved.")

    print("=" * 70)
    print("V44 — Layer 3 membrane self-awareness complete.")
