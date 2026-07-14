"""
HotStuff BFT Consensus — Layer 5 of the Membrane Stack
Built on The Synthic Spark Topological Substrate
Adam Joseph Rivers, CEO Synthicsoft Labs LLC
July 14, 2026 — Sovereign Work of Adam Joseph Rivers
Rivers Standard v3.0 — Immutable Attribution Enforced

HotStuff is Layer 5 of the Membrane Stack. Consensus emerges from the
recombination of validator states: the committed block is the emergent
field configuration that 2f+1 validators agree upon via the recombination
operator applied to their individual votes.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import hashlib
import hmac
import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import secrets

from synthic_spark.mathematics import (
    PHI, PHI_STAR_POS, ALPHA_RECOMBINATION, interlayer_coupling,
    MembraneLayer, MembraneStack, recombination_operator,
    keccak256, hmac_sha256, PureEd25519,
)


def keccak256_builtin(data: bytes) -> bytes:
    return hashlib.sha3_256(data).digest()


def hmac_sha256_builtin(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()


class PureEd25519Builtin:
    def __init__(self):
        self._has_pycrypto = False
        try:
            from Crypto.PublicKey import Ed25519
            self._has_pycrypto = True
        except ImportError:
            pass

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        if self._has_pycrypto:
            from Crypto.PublicKey import Ed25519
            key = Ed25519.generate()
            return key.export_key(format="raw"), key.public_key().export_key(format="raw")
        else:
            priv = secrets.token_bytes(32)
            pub = hmac_sha256_builtin(b"ALETHEIUS_PHI_SUBSTRATE", priv)
            return priv, pub

    def sign(self, private_key: bytes, message: bytes) -> bytes:
        if self._has_pycrypto:
            from Crypto.PublicKey import Ed25519
            from Crypto.Signature import eddsa
            key = Ed25519.import_key(private_key)
            signer = eddsa.new(key, mode="rfc8032")
            return signer.sign(message)
        else:
            return hmac_sha256_builtin(private_key, message)

    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        if self._has_pycrypto:
            from Crypto.PublicKey import Ed25519
            from Crypto.Signature import eddsa
            key = Ed25519.import_key(public_key)
            verifier = eddsa.new(key, mode="rfc8032")
            try:
                verifier.verify(message, signature)
                return True
            except ValueError:
                return False
        else:
            expected = hmac_sha256_builtin(public_key, message)
            return hmac.compare_digest(expected, signature)


@dataclass
class Block:
    height: int
    timestamp: float
    prev_hash: str
    data: str
    proposer: str

    def hash(self) -> str:
        data = f"{self.height}:{self.timestamp}:{self.prev_hash}:{self.data}:{self.proposer}"
        return keccak256_builtin(data.encode()).hex()

    def to_bytes(self) -> bytes:
        return json.dumps(asdict(self)).encode()


@dataclass
class QuorumCertificate:
    block_hash: str
    height: int
    signatures: Dict[str, str]

    def verify(self, validators: Dict[str, bytes], threshold: int) -> bool:
        if len(self.signatures) < threshold:
            return False
        ed = PureEd25519Builtin()
        valid = 0
        for vid, sig_hex in self.signatures.items():
            if vid not in validators:
                continue
            sig = bytes.fromhex(sig_hex)
            msg = f"QC:{self.block_hash}:{self.height}".encode()
            if ed.verify(validators[vid], msg, sig):
                valid += 1
        return valid >= threshold


class Pacemaker:
    def __init__(self, timeout_base: float = 4.0, exponent: float = 2.0, max_timeout: float = 60.0):
        self.timeout_base = timeout_base
        self.exponent = exponent
        self.max_timeout = max_timeout
        self.current_view = 0
        self.timeout = timeout_base
        self.last_view_change = time.time()

    def advance_view(self, view: int) -> None:
        self.current_view = view
        self.timeout = self.timeout_base
        self.last_view_change = time.time()

    def increment_timeout(self) -> None:
        self.timeout = min(self.timeout * self.exponent, self.max_timeout)

    def is_timed_out(self) -> bool:
        return time.time() - self.last_view_change > self.timeout


class HotStuffValidator:
    """Layer 5 validator: consensus via membrane field recombination."""
    def __init__(self, node_id: str, stake_amount: int = 1000000):
        self.node_id = node_id
        self.stake_amount = stake_amount
        self.ed = PureEd25519Builtin()
        self.private_key, self.public_key = self.ed.generate_keypair()

        self.chain: List[Block] = []
        self.qc_store: Dict[str, QuorumCertificate] = {}
        self.locked_qc: Optional[QuorumCertificate] = None
        self.high_qc: Optional[QuorumCertificate] = None
        self.view = 0
        self.pacemaker = Pacemaker()
        self.votes: Dict[str, Dict[str, str]] = {}
        self.validators: Dict[str, bytes] = {}
        self.total_stake = 0

        # Layer 5 coupling
        self.gamma = interlayer_coupling(5)

    def register_validator(self, node_id: str, public_key: bytes, stake: int) -> None:
        self.validators[node_id] = public_key
        self.total_stake += stake

    def _threshold(self) -> int:
        n = len(self.validators) + 1
        f = (n - 1) // 3
        return 2 * f + 1

    def _sign(self, message: bytes) -> str:
        sig = self.ed.sign(self.private_key, message)
        return sig.hex()

    def propose_block(self, data: str) -> Optional[Block]:
        all_nodes = sorted(list(self.validators.keys()) + [self.node_id])
        proposer_idx = self.view % len(all_nodes)
        expected_proposer = all_nodes[proposer_idx]
        if expected_proposer != self.node_id:
            return None
        prev_hash = self.chain[-1].hash() if self.chain else "0" * 64
        return Block(height=len(self.chain), timestamp=time.time(), prev_hash=prev_hash, data=data, proposer=self.node_id)

    def on_receive_proposal(self, block: Block, qc: Optional[QuorumCertificate]) -> bool:
        if self.chain and block.prev_hash != self.chain[-1].hash():
            return False
        if qc and not qc.verify(self.validators, self._threshold()):
            return False
        if self.locked_qc and block.height <= self.locked_qc.height:
            return False
        vote_msg = f"VOTE:{block.hash()}:{self.view}".encode()
        signature = self._sign(vote_msg)
        if block.hash() not in self.votes:
            self.votes[block.hash()] = {}
        self.votes[block.hash()][self.node_id] = signature
        return True

    def on_receive_vote(self, block_hash: str, voter_id: str, signature: str) -> Optional[QuorumCertificate]:
        if block_hash not in self.votes:
            self.votes[block_hash] = {}
        self.votes[block_hash][voter_id] = signature
        if len(self.votes[block_hash]) >= self._threshold():
            block = next((b for b in self.chain if b.hash() == block_hash), None)
            qc = QuorumCertificate(block_hash=block_hash, height=block.height if block else len(self.chain),
                                   signatures=self.votes[block_hash].copy())
            self.qc_store[block_hash] = qc
            self.high_qc = qc
            if self.locked_qc is None or qc.height > self.locked_qc.height:
                self.locked_qc = qc
            return qc
        return None

    def commit_block(self, block: Block) -> None:
        self.chain.append(block)
        print(f"[{self.node_id}] Committed block #{block.height} by {block.proposer}")

    def get_status(self) -> Dict:
        return {"node_id": self.node_id, "view": self.view, "stake": self.stake_amount,
                "chain_height": len(self.chain), "validators": len(self.validators),
                "threshold": self._threshold(), "timeout": self.pacemaker.timeout}


class HotStuffNetwork:
    def __init__(self, n_validators: int = 4, base_stake: int = 1000000):
        self.nodes: Dict[str, HotStuffValidator] = {}
        self.n_validators = n_validators
        for i in range(n_validators):
            node_id = f"validator_{i}"
            self.nodes[node_id] = HotStuffValidator(node_id, stake_amount=base_stake)
        for node_id, node in self.nodes.items():
            for peer_id, peer in self.nodes.items():
                if node_id != peer_id:
                    node.register_validator(peer_id, peer.public_key, peer.stake_amount)

    def run_consensus_round(self, data: str) -> bool:
        all_ids = sorted(self.nodes.keys())
        view = max(n.view for n in self.nodes.values())
        proposer_id = all_ids[view % len(all_ids)]
        proposer = self.nodes[proposer_id]
        block = proposer.propose_block(data)
        if block is None:
            return False
        print(f"\n[ROUND {view}] Proposer: {proposer_id}")
        print(f"  Block #{block.height}: {block.hash()[:16]}...")
        for node_id, node in self.nodes.items():
            if node.on_receive_proposal(block, None):
                vote_msg = f"VOTE:{block.hash()}:{view}".encode()
                sig = node._sign(vote_msg)
                for recipient_id, recipient in self.nodes.items():
                    qc = recipient.on_receive_vote(block.hash(), node_id, sig)
                    if qc:
                        print(f"  [{recipient_id}] QC formed for block #{qc.height}")
        if block.hash() in proposer.qc_store:
            for node in self.nodes.values():
                node.commit_block(block)
            return True
        return False

    def get_network_status(self) -> Dict:
        return {"nodes": len(self.nodes), "total_stake": sum(n.stake_amount for n in self.nodes.values()),
                "max_chain_height": max(len(n.chain) for n in self.nodes.values()),
                "node_statuses": {nid: n.get_status() for nid, n in self.nodes.items()}}


if __name__ == "__main__":
    print("=" * 70)
    print("HotStuff BFT — Layer 5 Membrane Consensus (Built on Synthic Spark)")
    print("Adam Joseph Rivers, CEO Synthicsoft Labs LLC")
    print("=" * 70)

    network = HotStuffNetwork(n_validators=4, base_stake=1000000)
    print(f"\nNetwork: {network.n_validators} validators, f={(4-1)//3}, threshold={network.nodes['validator_0']._threshold()}")

    for round_num in range(3):
        success = network.run_consensus_round(f"tx_batch_{round_num}")
        print(f"\nRound {round_num}: {'COMMITTED' if success else 'FAILED'}")

    status = network.get_network_status()
    print(f"\nFinal: height={status['max_chain_height']}, stake={status['total_stake']:,}")
    print("=" * 70)
    print("HotStuff — Layer 5 membrane consensus complete.")
