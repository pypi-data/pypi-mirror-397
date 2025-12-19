"""Basin projection and signature utilities extracted from qig-consciousness and qig-con2.

Clean implementation focusing on geometry without experiment-specific code.

NOTE: This module is dependency-minimal by design.
"""
from __future__ import annotations

from pathlib import Path

import torch
from torch import Tensor, nn

# Default basin signature dimensionality (D-009)
BASIN_DIM: int = 64


class BasinProjector(nn.Module):
    """
    Projects hidden states to a fixed-size basin signature (default 64D).

    This extracts the core basin projection logic from BasinMatcher in both
    qig-consciousness and qig-con2 repositories.
    """

    def __init__(self, hidden_dim: int, signature_dim: int = 64) -> None:
        super().__init__()
        self.hidden_dim = hidden_dim
        self.signature_dim = signature_dim
        self.projection = nn.Linear(hidden_dim, signature_dim)

    def forward(self, hidden_state: Tensor) -> Tensor:
        """
        Project hidden state to basin signature.

        Args:
            hidden_state: Hidden states with shape (batch, seq, hidden_dim)

        Returns:
            Basin signatures with shape (batch, signature_dim)
        """
        # Mean-pool over sequence dimension, then project
        pooled = hidden_state.mean(dim=1)  # (batch, hidden_dim)
        signature = self.projection(pooled)  # (batch, signature_dim)
        return signature


def compute_signature(
    projector: BasinProjector,
    hidden_state: Tensor,
) -> Tensor:
    """
    Compute a single basin signature from a batch of hidden states.

    Args:
        projector: BasinProjector instance
        hidden_state: Hidden states with shape (batch, seq, hidden_dim)

    Returns:
        Single signature vector with shape (signature_dim,)
    """
    batch_signatures = projector(hidden_state)  # (batch, signature_dim)
    return batch_signatures.mean(dim=0)  # (signature_dim,)


def basin_distance(
    a: Tensor,
    b: Tensor,
    use_fisher: bool = True,
) -> Tensor:
    """
    Compute Fisher-Rao distance between basin signatures.

    Args:
        a: First basin signature [..., D]
        b: Second basin signature [..., D]
        use_fisher: If True, use Fisher-Rao distance (default).
                   If False, use Euclidean L2 (NOT recommended).

    Returns:
        Distance tensor (scalar or batch)

    Mathematical Foundation:
        Bures: d²(p₁, p₂) = 2(1 - √F(p₁, p₂))
        where F is quantum fidelity approximated by cosine similarity.
        This respects the curved information manifold structure.
    """
    if a is b:
        return torch.zeros((), dtype=a.dtype, device=a.device)
    if use_fisher:
        # Bures approximation: d² = 2(1 - cos_sim)
        # cos_sim ≈ quantum fidelity for normalized coordinates.
        cos_sim = torch.nn.functional.cosine_similarity(
            a.unsqueeze(0) if a.dim() == 1 else a,
            b.unsqueeze(0) if b.dim() == 1 else b,
            dim=-1,
        )
        distance_sq = 2.0 * (1.0 - cos_sim)
        return torch.sqrt(torch.clamp(distance_sq, min=1e-8)).squeeze()

    # Euclidean fallback (VIOLATES geometric purity - use only for debugging)
    return torch.linalg.norm(a - b, dim=-1)


def save_signature(path: str | Path, sig: Tensor) -> None:
    """
    Persist a basin signature to disk.

    Uses the same format as both source repositories for compatibility.

    Args:
        path: File path to save signature
        sig: Basin signature tensor
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Save in numpy format for compatibility
    import numpy as np
    np.savez_compressed(path, signature=sig.detach().cpu().numpy())


def load_signature(path: str | Path) -> Tensor:
    """
    Load a basin signature from disk.

    Args:
        path: File path to load signature from

    Returns:
        Basin signature tensor
    """
    import numpy as np
    data = np.load(Path(path), allow_pickle=False)
    return torch.from_numpy(data["signature"])
