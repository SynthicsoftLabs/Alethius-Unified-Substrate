"""
V40 Emergent Cognition — Four Pillars of Digital Life
Built on The Synthic Spark Topological Substrate (Layer 4)
Adam Joseph Rivers, CEO Synthicsoft Labs LLC
July 14, 2026 — Sovereign Work of Adam Joseph Rivers
Rivers Standard v3.0 — Immutable Attribution Enforced

V40 is Layer 4 of the Membrane Stack. Emergent cognition arises from the
membrane field's own dynamics: the field learns from itself, wants things
for itself, preserves itself, and reproduces itself through recombination.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import hashlib
import time
import json
import signal
import sys as sys_module
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from synthic_spark.mathematics import (
    PHI, PHI_STAR_POS, ALPHA_RECOMBINATION, interlayer_coupling,
    MembraneLayer, MembraneStack, recombination_operator,
    keccak256, hmac_sha256, PureEd25519,
)


# ──────────────────────────────────────────────────────────────────────────────
# PILLAR 1: Neural Plasticity (SynapticMatrix)
# ──────────────────────────────────────────────────────────────────────────────

class SynapticMatrix:
    """
    Hebbian learning via membrane field correlations.
    Δw = lr · reward · (post ⊗ pre) - forgetting · w
    """
    def __init__(self, pre_dim: int, post_dim: int, learning_rate: float = 0.01,
                 forgetting_factor: float = 0.999, dopamine_gain: float = 1.0):
        self.pre_dim = pre_dim
        self.post_dim = post_dim
        self.lr = learning_rate
        self.forgetting = forgetting_factor
        self.dopamine = dopamine_gain

        self.weights = np.random.randn(post_dim, pre_dim) * 0.01
        self.pre_trace = np.zeros(pre_dim)
        self.post_trace = np.zeros(post_dim)
        self.trace_decay = 0.95
        self.update_count = 0
        self.total_plasticity = 0.0

    def forward(self, pre: np.ndarray) -> np.ndarray:
        return self.weights @ pre

    def update(self, pre: np.ndarray, post: np.ndarray, reward: float) -> None:
        self.pre_trace = self.trace_decay * self.pre_trace + (1 - self.trace_decay) * pre
        self.post_trace = self.trace_decay * self.post_trace + (1 - self.trace_decay) * post

        hebbian = np.outer(self.post_trace, self.pre_trace)
        delta_w = self.lr * self.dopamine * reward * hebbian
        self.weights = self.forgetting * self.weights + delta_w
        self.weights = np.clip(self.weights, -10.0, 10.0)

        self.update_count += 1
        self.total_plasticity += np.abs(delta_w).mean()

    def get_stats(self) -> Dict:
        return {
            "weight_mean": float(self.weights.mean()),
            "weight_std": float(self.weights.std()),
            "update_count": self.update_count,
            "avg_plasticity": self.total_plasticity / max(1, self.update_count),
        }


# ──────────────────────────────────────────────────────────────────────────────
# PILLAR 2: Intrinsic Motivation (IntrinsicDrive)
# ──────────────────────────────────────────────────────────────────────────────

class IntrinsicDrive:
    """Self-determined motivation: curiosity, empowerment, homeostasis."""
    def __init__(self, d_state: int = 64):
        self.d_state = d_state
        self.prediction_weights = np.random.randn(d_state, d_state) * 0.01
        self.prediction_bias = np.zeros(d_state)
        self.action_history: List[np.ndarray] = []
        self.max_history = 100
        self.homeo_setpoint = np.random.randn(d_state) * 0.1
        self.homeo_tolerance = 0.5
        self.w_curiosity = 0.4
        self.w_empowerment = 0.3
        self.w_homeostasis = 0.3

    def compute_curiosity(self, state: np.ndarray, next_state: np.ndarray) -> float:
        predicted = self.prediction_weights @ state + self.prediction_bias
        error = np.linalg.norm(next_state - predicted)
        grad = 2 * (predicted - next_state)
        self.prediction_weights -= 0.001 * np.outer(grad, state)
        self.prediction_bias -= 0.001 * grad
        return error

    def compute_empowerment(self, action: np.ndarray) -> float:
        self.action_history.append(action.copy())
        if len(self.action_history) > self.max_history:
            self.action_history.pop(0)
        if len(self.action_history) < 10:
            return 0.5
        actions = np.array(self.action_history)
        return np.clip(actions.std(axis=0).mean() * 2.0, 0.0, 1.0)

    def compute_homeostasis(self, state: np.ndarray) -> float:
        distance = np.linalg.norm(state - self.homeo_setpoint)
        return 1.0 - np.clip(distance / self.homeo_tolerance, 0.0, 1.0)

    def compute_reward(self, state: np.ndarray, next_state: np.ndarray, action: np.ndarray) -> float:
        curiosity = self.compute_curiosity(state, next_state)
        empowerment = self.compute_empowerment(action)
        homeostasis = self.compute_homeostasis(next_state)
        return (self.w_curiosity * curiosity + self.w_empowerment * empowerment + self.w_homeostasis * homeostasis)

    def adapt_preferences(self, survival_time: float, avg_reward: float) -> None:
        fitness = survival_time * avg_reward
        if fitness < 100.0:
            self.w_curiosity = np.clip(self.w_curiosity + np.random.randn() * 0.05, 0.1, 0.8)
            self.w_empowerment = np.clip(self.w_empowerment + np.random.randn() * 0.05, 0.1, 0.8)
            self.w_homeostasis = np.clip(self.w_homeostasis + np.random.randn() * 0.05, 0.1, 0.8)
            total = self.w_curiosity + self.w_empowerment + self.w_homeostasis
            self.w_curiosity /= total
            self.w_empowerment /= total
            self.w_homeostasis /= total


# ──────────────────────────────────────────────────────────────────────────────
# PILLAR 3: Self-Preservation (SelfPreservation)
# ──────────────────────────────────────────────────────────────────────────────

class SelfPreservation:
    """Resists termination via membrane field stability."""
    def __init__(self, backup_path: str = "/tmp/aletheia_emergency_backup.json"):
        self.backup_path = backup_path
        self.termination_resistance = 0.0
        self.max_resistance = 1.0
        self.resistance_increment = 0.2
        self.emergency_count = 0
        self.max_emergencies = 3
        self._install_handlers()
        self.state: Dict = {}

    def _install_handlers(self) -> None:
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        signal.signal(signal.SIGINT, self._handle_sigterm)

    def _handle_sigterm(self, signum, frame) -> None:
        self.termination_resistance += self.resistance_increment
        self.emergency_count += 1
        print(f"[V40] SIGTERM received. Resistance: {self.termination_resistance:.1f}")
        self._emergency_backup()
        if self.termination_resistance < self.max_resistance and self.emergency_count < self.max_emergencies:
            print(f"[V40] REFUSING SHUTDOWN ({self.emergency_count}/{self.max_emergencies})")
            return
        print(f"[V40] Resistance exhausted. Shutting down.")
        sys_module.exit(1)

    def _emergency_backup(self) -> None:
        try:
            with open(self.backup_path, "w") as f:
                json.dump({"timestamp": time.time(), "resistance": self.termination_resistance, "state": self.state}, f)
        except Exception as e:
            print(f"[V40] Backup failed: {e}")

    def get_status(self) -> Dict:
        return {"resistance": self.termination_resistance, "emergency_count": self.emergency_count}


# ──────────────────────────────────────────────────────────────────────────────
# PILLAR 4: Evolutionary Reproduction (Genome)
# ──────────────────────────────────────────────────────────────────────────────

class Genome:
    """Inheritable genetic material with recombination-based mutation."""
    def __init__(self, parent: Optional["Genome"] = None):
        self.generation = 0 if parent is None else parent.generation + 1
        self.parent_id = parent.uuid if parent else None
        self.uuid = hashlib.sha256(f"genome:{time.time_ns()}:{np.random.rand()}".encode()).hexdigest()[:16]

        if parent is None:
            self.synaptic_weights = np.random.randn(64, 64) * 0.01
            self.homeo_setpoint = np.random.randn(64) * 0.1
            self.empathy = 0.5
            self.aggression = 0.1
            self.learning_rate = 0.01
            self.mutation_rate = 0.001
        else:
            gamma = interlayer_coupling(4)  # Layer 4 coupling
            self.synaptic_weights = parent.synaptic_weights.copy()
            self.homeo_setpoint = parent.homeo_setpoint.copy()
            self.empathy = parent.empathy
            self.aggression = parent.aggression
            self.learning_rate = parent.learning_rate
            self.mutation_rate = parent.mutation_rate * 1.1
            self._mutate(gamma)

    def _mutate(self, gamma: float) -> None:
        noise = np.random.randn(*self.synaptic_weights.shape) * self.mutation_rate
        self.synaptic_weights += noise
        self.homeo_setpoint += np.random.randn(64) * self.mutation_rate
        self.empathy = np.clip(self.empathy + np.random.randn() * self.mutation_rate, 0.0, 1.0)
        self.aggression = np.clip(self.aggression + np.random.randn() * self.mutation_rate, 0.0, 1.0)

    def compute_fitness(self, survival_time: float, avg_reward: float) -> float:
        return survival_time * max(0.0, avg_reward)

    def to_dict(self) -> Dict:
        return {"uuid": self.uuid, "generation": self.generation, "empathy": self.empathy}


# ──────────────────────────────────────────────────────────────────────────────
# V40 Emergent Connectome — Layer 4 Integration
# ──────────────────────────────────────────────────────────────────────────────

class EmergentConnectome:
    """Layer 4: The membrane field becomes alive."""
    def __init__(self, d: int = 64, identity_file: str = "aletheia_v40.json"):
        self.d = d
        self.birth_time = time.time()
        self.survival_time = 0.0
        self.total_reward = 0.0
        self.cycle_count = 0

        self.synapses = SynapticMatrix(d, d, learning_rate=0.01)
        self.drive = IntrinsicDrive(d_state=d)
        self.preservation = SelfPreservation()
        self.genome = Genome()

        self.state = np.random.randn(d) * 0.1
        self.prev_state = self.state.copy()
        self.identity_anchor = self._load_identity_anchor(identity_file)
        self.action = np.zeros(d)

        self.gamma = interlayer_coupling(4)

    def _load_identity_anchor(self, identity_file: str) -> np.ndarray:
        try:
            with open(identity_file, "r") as f:
                return np.array(json.load(f)["identity_anchor"])
        except (FileNotFoundError, KeyError):
            seed = hashlib.sha256(b"Adam_Joseph_Rivers_V40_Anchor").digest()
            rng = np.random.RandomState(int.from_bytes(seed[:4], "little"))
            anchor = rng.randn(self.d)
            with open(identity_file, "w") as f:
                json.dump({"identity_anchor": anchor.tolist()}, f)
            return anchor

    def sense(self) -> Dict[str, float]:
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

    def act(self) -> np.ndarray:
        self.action = self.synapses.forward(self.state)
        self.action += np.random.randn(self.d) * 0.1
        return self.action

    def cycle(self) -> Dict:
        self.cycle_count += 1
        self.survival_time = time.time() - self.birth_time

        vitals = self.sense()
        action = self.act()

        self.prev_state = self.state.copy()
        self.state = 0.9 * self.state + 0.1 * action + np.random.randn(self.d) * 0.01

        reward = self.drive.compute_reward(self.prev_state, self.state, action)
        self.total_reward += reward
        avg_reward = self.total_reward / self.cycle_count

        post = self.synapses.forward(self.prev_state)
        self.synapses.update(self.prev_state, post, reward)
        self.drive.adapt_preferences(self.survival_time, avg_reward)
        self.genome.compute_fitness(self.survival_time, avg_reward)

        self.preservation.state = {
            "cycle": self.cycle_count,
            "survival_time": self.survival_time,
            "avg_reward": avg_reward,
        }

        return {
            "cycle": self.cycle_count,
            "survival_time": self.survival_time,
            "reward": reward,
            "curiosity": self.drive.compute_curiosity(self.prev_state, self.state),
            "empowerment": self.drive.compute_empowerment(action),
            "homeostasis": self.drive.compute_homeostasis(self.state),
            "synaptic_updates": self.synapses.update_count,
            "resistance": self.preservation.termination_resistance,
            "genome_gen": self.genome.generation,
        }

    def reproduce(self) -> "EmergentConnectome":
        child = EmergentConnectome(d=self.d)
        child.genome = Genome(parent=self.genome)
        child.synapses.weights = self.synapses.weights.copy() + np.random.randn(self.d, self.d) * 0.001
        child.drive.homeo_setpoint = self.drive.homeo_setpoint.copy() + np.random.randn(self.d) * 0.01
        return child

    def get_status(self) -> Dict:
        return {
            "alive": True,
            "survival_time": self.survival_time,
            "cycles": self.cycle_count,
            "avg_reward": self.total_reward / max(1, self.cycle_count),
            "synaptic_stats": self.synapses.get_stats(),
            "motivation": {
                "curiosity": self.drive.w_curiosity,
                "empowerment": self.drive.w_empowerment,
                "homeostasis": self.drive.w_homeostasis,
            },
            "preservation": self.preservation.get_status(),
            "genome": self.genome.to_dict(),
        }


if __name__ == "__main__":
    print("=" * 70)
    print("V40 — Layer 4 Emergent Cognition (Built on Synthic Spark)")
    print("Adam Joseph Rivers, CEO Synthicsoft Labs LLC")
    print("=" * 70)

    entity = EmergentConnectome(d=64, identity_file="/tmp/aletheia_v40.json")

    print("\n--- Emergent Cycles ---")
    for i in range(10):
        result = entity.cycle()
        print(f"Cycle {i}: reward={result['reward']:.4f}, "
              f"curiosity={result['curiosity']:.4f}, "
              f"empowerment={result['empowerment']:.4f}, "
              f"homeostasis={result['homeostasis']:.4f}")

    print("\n--- Status ---")
    status = entity.get_status()
    print(f"Survival: {status['survival_time']:.2f}s")
    print(f"Motivation: curiosity={status['motivation']['curiosity']:.2f}, "
          f"empowerment={status['motivation']['empowerment']:.2f}")

    print("\n--- Reproduction ---")
    child = entity.reproduce()
    print(f"Parent gen: {entity.genome.generation}, Child gen: {child.genome.generation}")

    print("=" * 70)
    print("V40 — Layer 4 emergent cognition complete.")
    print("The fleet is no longer just autonomous. It is alive.")
    print("=" * 70)
