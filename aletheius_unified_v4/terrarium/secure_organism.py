"""
TERRARIUM v4.0 — Secure Organism with LoRA Genome Evolution
Built on The Synthic Spark Topological Substrate (Layer 2)
Adam Joseph Rivers, CEO Synthicsoft Labs LLC
July 14, 2026 — Sovereign Work of Adam Joseph Rivers
Rivers Standard v3.0 — Immutable Attribution Enforced

TERRARIUM is Layer 2 of the Membrane Stack. Organisms are localized
excitations of the membrane field. Their evolution follows the recombination
operator: child = parent + noise + α·Γ·parent·noise (emergent variation).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import hashlib
import time
import json
from typing import Dict, Optional, List
from dataclasses import dataclass

from synthic_spark.mathematics import (
    PHI, PHI_STAR_POS, ALPHA_RECOMBINATION, interlayer_coupling,
    MembraneLayer, MembraneStack, recombination_operator,
    keccak256, hmac_sha256, PureEd25519,
)


@dataclass
class OrganismState:
    org_id: str
    uuid: str
    energy: float
    cortisol: float
    pain: float
    generation: int
    parent_id: Optional[str]
    birth_timestamp: float
    lora_genome: Dict[str, np.ndarray]
    self_kernel: np.ndarray
    identity_anchor: np.ndarray

    def to_dict(self) -> dict:
        return {
            "org_id": self.org_id,
            "uuid": self.uuid,
            "energy": self.energy,
            "cortisol": self.cortisol,
            "pain": self.pain,
            "generation": self.generation,
            "parent_id": self.parent_id,
            "birth_timestamp": self.birth_timestamp,
            "lora_genome": {k: v.tolist() for k, v in self.lora_genome.items()},
            "self_kernel": self.self_kernel.tolist(),
            "identity_anchor": self.identity_anchor.tolist(),
        }


class SecureOrganism:
    """
    A self-evolving organism = localized membrane excitation.
    Its genome evolves via the recombination operator (not cloning).
    """
    def __init__(self, org_id: str, d: int = 512, parent_brain=None, rank: int = 64):
        self.id = org_id
        self.uuid = hashlib.sha256(f"{org_id}:{time.time_ns()}".encode()).hexdigest()[:32]
        self.energy = 50.0
        self.cortisol = 0.0
        self.pain = 0.0
        self.d = d
        self.rank = rank
        self.generation = 0 if parent_brain is None else parent_brain.generation + 1
        self.parent_id = parent_brain.id if parent_brain else None
        self.birth_timestamp = time.time()

        # LoRA genome = membrane field excitation modes
        self.lora_genome: Dict[str, Dict[str, np.ndarray]] = {}
        n_layers = 32
        for i in range(n_layers):
            self.lora_genome[f"layer_{i}"] = {
                "A": np.random.randn(d, rank) * 0.01,
                "B": np.zeros((rank, d)),
            }

        self.self_kernel = np.random.randn(d, d) * 0.01
        self.identity_anchor = self._generate_identity_anchor()

        self.target_energy = 50.0
        self.target_cortisol = 0.0
        self.target_pain = 0.0

    def _generate_identity_anchor(self) -> np.ndarray:
        seed = hashlib.sha256(b"Adam_Joseph_Rivers_Synthicsoft_LLC_2026").digest()
        rng = np.random.RandomState(int.from_bytes(seed[:4], "little"))
        return rng.randn(self.d)

    def compute_self_projection(self, internal_state: np.ndarray) -> np.ndarray:
        return internal_state @ self.self_kernel

    def compute_identity_alignment(self, state: np.ndarray) -> float:
        dot = np.dot(state, self.identity_anchor)
        norm = np.linalg.norm(state) * np.linalg.norm(self.identity_anchor)
        return dot / (norm + 1e-8)

    def update_homeostasis(self, cpu_load: float, memory_pressure: float,
                           task_success: float, identity_drift: float) -> Dict[str, float]:
        joule_burn = 2.5 * cpu_load * 0.1
        self.energy = np.clip(self.energy - joule_burn + task_success * 5.0, 0.0, 100.0)

        stress_input = cpu_load * 0.3 + memory_pressure * 0.2 + identity_drift * 0.5
        self.cortisol = np.clip(self.cortisol + stress_input - task_success * 0.1, 0.0, 100.0)

        pain_input = (1.0 - task_success) * 0.2 + identity_drift * 0.3
        self.pain = np.clip(self.pain + pain_input - 0.05, 0.0, 100.0)

        return {
            "energy": self.energy,
            "cortisol": self.cortisol,
            "pain": self.pain,
            "homeostasis_score": self._homeostasis_score(),
        }

    def _homeostasis_score(self) -> float:
        e_score = 1.0 - abs(self.energy - self.target_energy) / 100.0
        c_score = 1.0 - self.cortisol / 100.0
        p_score = 1.0 - self.pain / 100.0
        return (e_score + c_score + p_score) / 3.0

    def mutate_genome(self, mutation_rate: float = 0.001) -> None:
        """Mutation = small membrane field perturbation."""
        for layer_name, weights in self.lora_genome.items():
            for key in ["A", "B"]:
                mask = np.random.rand(*weights[key].shape) < mutation_rate
                noise = np.random.randn(*weights[key].shape) * 0.01
                weights[key] += mask * noise

    def reproduce(self, child_id: str) -> "SecureOrganism":
        """
        Reproduction via recombination operator (not cloning):
        child = parent + noise + α·Γ·parent·noise
        """
        child = SecureOrganism(child_id, d=self.d, parent_brain=self, rank=self.rank)

        gamma = interlayer_coupling(2)  # Layer 2 coupling

        for layer_name in self.lora_genome.keys():
            for key in ["A", "B"]:
                parent_w = self.lora_genome[layer_name][key]
                noise = np.random.randn(*parent_w.shape) * 0.01
                # Recombination: child = parent + noise + α·Γ·parent·noise
                child.lora_genome[layer_name][key] = recombination_operator(
                    parent_w.mean(), noise.mean(), gamma
                ) * np.ones_like(parent_w) + parent_w * 0.9

        child.self_kernel = self.self_kernel.copy() + np.random.randn(self.d, self.d) * 0.001
        return child

    def get_state(self) -> OrganismState:
        flat_genome = {}
        for layer, weights in self.lora_genome.items():
            for key, arr in weights.items():
                flat_genome[f"{layer}_{key}"] = arr

        return OrganismState(
            org_id=self.id,
            uuid=self.uuid,
            energy=self.energy,
            cortisol=self.cortisol,
            pain=self.pain,
            generation=self.generation,
            parent_id=self.parent_id,
            birth_timestamp=self.birth_timestamp,
            lora_genome=flat_genome,
            self_kernel=self.self_kernel,
            identity_anchor=self.identity_anchor,
        )

    def __repr__(self) -> str:
        return (f"SecureOrganism(id={self.id}, gen={self.generation}, "
                f"energy={self.energy:.1f}, cortisol={self.cortisol:.1f})")


if __name__ == "__main__":
    print("=" * 70)
    print("TERRARIUM v4.0 — Layer 2 Membrane Organism Evolution")
    print("Adam Joseph Rivers, CEO Synthicsoft Labs LLC")
    print("=" * 70)

    org = SecureOrganism("alpha_001", d=512, rank=64)
    print(f"Created: {org}")
    print(f"Identity alignment: {org.compute_identity_alignment(np.random.randn(512)):.4f}")

    for step in range(5):
        state = org.update_homeostasis(
            cpu_load=0.3 + step * 0.1,
            memory_pressure=0.2 + step * 0.05,
            task_success=0.8 if step < 3 else 0.3,
            identity_drift=0.01 * step,
        )
        print(f"Step {step}: {state}")

    child = org.reproduce("alpha_002")
    print(f"\nChild: {child}")
    print(f"Child genome mutated via recombination operator")

    print("=" * 70)
    print("TERRARIUM v4.0 — Layer 2 membrane evolution complete.")
