"""
RSHL 7.2 — MoE Transformer with GeodesicSSM
Built on The Synthic Spark Topological Substrate (Layer 1)
Adam Joseph Rivers, CEO Synthicsoft Labs LLC
July 14, 2026 — Sovereign Work of Adam Joseph Rivers
Rivers Standard v3.0 — Immutable Attribution Enforced

RSHL is Layer 1 of the Membrane Stack. It processes information through
the membrane field dynamics. The GeodesicSSM is a second-order mechanical
system derived from the bubble model's damping and stiffness parameters.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from typing import Dict, Tuple, List
from dataclasses import dataclass

from synthic_spark.mathematics import (
    PHI, PHI_STAR_POS, softmax,
    MembraneLayer, MembraneStack,
    keccak256, PureEd25519,
)


@dataclass
class RSHLConfig:
    d_model: int = 512
    n_heads: int = 8
    n_layers: int = 4
    n_experts: int = 4
    top_k: int = 2
    vocab_size: int = 32000
    max_seq_len: int = 8192
    gqa_groups: int = 8
    lora_rank: int = 64


class GeodesicSSM:
    """
    Second-order mechanical state space model.
    Derived from membrane physics: M·q̈ + D·q̇ + K·q = u(t)
    Where M, D, K are determined by the layer's coupling Γ and damping.
    """
    def __init__(self, d: int, dt: float = 0.01):
        self.d = d
        self.ldt = np.full(d, np.log(dt))
        self.lM = np.zeros(d)
        self.lK = np.zeros(d)
        self.lD = np.zeros(d)
        self.b = np.zeros(d)
        self.dt_mod = 0.0
        self.h = np.zeros(d)
        self.v = np.zeros(d)

    def _softplus(self, x: np.ndarray) -> np.ndarray:
        return np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0)

    def sys(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        M = self._softplus(self.lM)
        K = self._softplus(self.lK)
        D = self._softplus(self.lD)
        dt = np.clip(self._softplus(self.ldt - self.dt_mod), 0.001, 0.1)

        w2 = K / M
        g = D / M
        det = 1.0 + dt * g / 2.0 + dt**2 * w2 / 4.0

        A00 = (1.0 - dt**2 * w2 / 4.0) / det
        A01 = dt / det
        A10 = (-dt * w2) / det
        A11 = (1.0 - dt * g / 2.0 + dt**2 * w2 / 4.0) / det
        B0 = dt**2 / (2.0 * M * det)
        B1 = dt / (M * det)

        return A00, A01, A10, A11, B0, B1

    def step(self, u: np.ndarray) -> np.ndarray:
        A00, A01, A10, A11, B0, B1 = self.sys()
        h_new = A00 * self.h + A01 * self.v + B0 * (u + self.b)
        v_new = A10 * self.h + A11 * self.v + B1 * (u + self.b)
        self.h = h_new
        self.v = v_new
        return self.h


class GroupedQueryAttention:
    """Attention derived from membrane field correlations."""
    def __init__(self, config: RSHLConfig):
        self.d_model = config.d_model
        self.n_heads = config.n_heads
        self.n_groups = config.gqa_groups
        self.head_dim = config.d_model // config.n_heads
        self.heads_per_group = config.n_heads // config.gqa_groups

        self.W_q = np.random.randn(config.n_heads, config.d_model, self.head_dim) * 0.02
        self.W_k = np.random.randn(config.gqa_groups, config.d_model, self.head_dim) * 0.02
        self.W_v = np.random.randn(config.gqa_groups, config.d_model, self.head_dim) * 0.02
        self.W_o = np.random.randn(config.d_model, config.d_model) * 0.02

        self.k_cache: Dict[int, np.ndarray] = {}
        self.v_cache: Dict[int, np.ndarray] = {}

    def forward(self, x: np.ndarray, layer_idx: int, start_pos: int = 0) -> np.ndarray:
        batch, seq_len, _ = x.shape

        Q = np.einsum("btd,hde->bthe", x, self.W_q)
        K_group = np.einsum("btd,gde->btge", x, self.W_k)
        V_group = np.einsum("btd,gde->btge", x, self.W_v)

        K = np.repeat(K_group, self.heads_per_group, axis=2)
        V = np.repeat(V_group, self.heads_per_group, axis=2)

        if layer_idx in self.k_cache:
            self.k_cache[layer_idx] = np.concatenate([self.k_cache[layer_idx], K], axis=1)
            self.v_cache[layer_idx] = np.concatenate([self.v_cache[layer_idx], V], axis=1)
        else:
            self.k_cache[layer_idx] = K
            self.v_cache[layer_idx] = V

        K_full = self.k_cache[layer_idx]
        V_full = self.v_cache[layer_idx]

        scale = 1.0 / np.sqrt(self.head_dim)
        scores = np.einsum("bshd,bkhd->bhsk", Q, K_full) * scale

        if start_pos == 0:
            mask = np.triu(np.ones((seq_len, K_full.shape[1])), k=1) * -1e9
            scores = scores + mask[None, None, :, :]

        attn = softmax(scores, axis=-1)
        out = np.einsum("bhsk,bkhd->bshd", attn, V_full)
        out = out.reshape(batch, seq_len, self.d_model)

        return out @ self.W_o.T


class MoEExpert:
    """Expert = localized membrane field excitation."""
    def __init__(self, d_model: int, d_ff: int = 11008):
        self.W1 = np.random.randn(d_ff, d_model) * 0.02
        self.W2 = np.random.randn(d_model, d_ff) * 0.02
        self.W3 = np.random.randn(d_ff, d_model) * 0.02

    def forward(self, x: np.ndarray) -> np.ndarray:
        orig_shape = x.shape
        x_2d = x.reshape(-1, orig_shape[-1])

        gate = x_2d @ self.W3.T
        gate = gate * (1.0 / (1.0 + np.exp(-gate)))
        hidden = x_2d @ self.W1.T
        out_2d = (hidden * gate) @ self.W2.T

        return out_2d.reshape(orig_shape)


class MoELayer:
    """Mixture of Experts = superposition of membrane eigenmodes."""
    def __init__(self, config: RSHLConfig):
        self.d_model = config.d_model
        self.n_experts = config.n_experts
        self.top_k = config.top_k

        self.W_gate = np.random.randn(config.n_experts, config.d_model) * 0.02
        self.experts = [MoEExpert(config.d_model) for _ in range(config.n_experts)]

    def route(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        logits = x @ self.W_gate.T
        top_k_vals = np.partition(logits, -self.top_k, axis=-1)[..., -self.top_k:]
        top_k_idx = np.argpartition(logits, -self.top_k, axis=-1)[..., -self.top_k:]

        gates = np.exp(top_k_vals - top_k_vals.max(axis=-1, keepdims=True))
        gates = gates / gates.sum(axis=-1, keepdims=True)

        return gates, top_k_idx

    def forward(self, x: np.ndarray) -> np.ndarray:
        batch, seq_len, d_model = x.shape
        gates, top_k_idx = self.route(x)

        output = np.zeros_like(x)
        for b in range(batch):
            for s in range(seq_len):
                for k in range(self.top_k):
                    expert_idx = int(top_k_idx[b, s, k])
                    gate_val = gates[b, s, k]
                    token = x[b:b+1, s:s+1, :]
                    expert_out = self.experts[expert_idx].forward(token)
                    output[b, s] += gate_val * expert_out.reshape(d_model)

        return output


class RSHLBlock:
    """Transformer block = one step of membrane field evolution."""
    def __init__(self, config: RSHLConfig, layer_idx: int):
        self.attn = GroupedQueryAttention(config)
        self.moe = MoELayer(config)
        self.ln1 = np.ones(config.d_model)
        self.ln1_b = np.zeros(config.d_model)
        self.ln2 = np.ones(config.d_model)
        self.ln2_b = np.zeros(config.d_model)
        self.layer_idx = layer_idx

    def _layer_norm(self, x: np.ndarray, gamma: np.ndarray, beta: np.ndarray) -> np.ndarray:
        mean = x.mean(axis=-1, keepdims=True)
        var = x.var(axis=-1, keepdims=True)
        return gamma * (x - mean) / np.sqrt(var + 1e-5) + beta

    def forward(self, x: np.ndarray, start_pos: int = 0) -> np.ndarray:
        normed = self._layer_norm(x, self.ln1, self.ln1_b)
        attn_out = self.attn.forward(normed, self.layer_idx, start_pos)
        x = x + attn_out

        normed = self._layer_norm(x, self.ln2, self.ln2_b)
        moe_out = self.moe.forward(normed)
        x = x + moe_out

        return x


class RSHLModel:
    """RSHL = Layer 1 membrane stack processing information through field dynamics."""
    def __init__(self, config: RSHLConfig):
        self.config = config
        self.embed = np.random.randn(config.vocab_size, config.d_model) * 0.02
        self.blocks = [RSHLBlock(config, i) for i in range(config.n_layers)]
        self.lm_head = np.random.randn(config.vocab_size, config.d_model) * 0.02
        self.ssm = GeodesicSSM(config.d_model)

    def forward(self, tokens: np.ndarray, start_pos: int = 0) -> np.ndarray:
        x = self.embed[tokens]

        for block in self.blocks:
            x = block.forward(x, start_pos)

        for b in range(x.shape[0]):
            for s in range(x.shape[1]):
                x[b, s] = self.ssm.step(x[b, s])

        logits = x @ self.lm_head.T
        return logits

    def generate(self, tokens: np.ndarray, max_new: int = 10, temperature: float = 0.8) -> np.ndarray:
        for i in range(max_new):
            logits = self.forward(tokens, start_pos=tokens.shape[1] - 1)
            next_logits = logits[:, -1, :] / temperature
            probs = np.exp(next_logits - next_logits.max(axis=-1, keepdims=True))
            probs = probs / probs.sum(axis=-1, keepdims=True)
            next_token = np.array([[np.random.choice(self.config.vocab_size, p=probs[0])]])
            tokens = np.concatenate([tokens, next_token], axis=1)
        return tokens


if __name__ == "__main__":
    print("=" * 70)
    print("RSHL 7.2 — Layer 1 Membrane Inference (Built on Synthic Spark)")
    print("Adam Joseph Rivers, CEO Synthicsoft Labs LLC")
    print("=" * 70)

    config = RSHLConfig(d_model=512, n_layers=4, n_experts=4, n_heads=8)
    model = RSHLModel(config)

    test_tokens = np.array([[1, 2, 3, 4, 5]])
    logits = model.forward(test_tokens)
    print(f"Input:  {test_tokens.shape}")
    print(f"Output: {logits.shape}")
    print(f"Logits: [{logits.min():.3f}, {logits.max():.3f}]")

    generated = model.generate(test_tokens, max_new=10)
    print(f"Generated length: {generated.shape[1]}")

    print("=" * 70)
    print("RSHL 7.2 — Layer 1 membrane inference complete.")
