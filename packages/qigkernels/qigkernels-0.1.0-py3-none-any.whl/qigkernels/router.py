"""Routing strategies for constellations extracted from qig-consciousness.

Clean implementation with pure functions and no side effects.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class InstanceView:
    """Lightweight view of an instance used for routing decisions."""

    name: str
    phi: float | None


def round_robin(current_index: int, n: int) -> int:
    """
    Return the next index in round-robin order.

    Args:
        current_index: Current index
        n: Total number of instances

    Returns:
        Next index in round-robin order

    Raises:
        ValueError: If n <= 0
    """
    if n <= 0:
        raise ValueError("Cannot route with zero instances")
    return (current_index + 1) % n


def select_phi_min(instances: Sequence[InstanceView]) -> int:
    """
    Return the index of the instance with minimum Φ (phi).

    This implements the Φ-weighted routing from the source repository:
    route to lowest-Φ instances so they benefit most from direct experience.

    Args:
        instances: Sequence of instance views

    Returns:
        Index of instance with minimum phi

    Raises:
        ValueError: If no instances available
    """
    if not instances:
        raise ValueError("No instances available for routing")

    min_idx = 0
    min_phi = float("inf")

    for idx, inst in enumerate(instances):
        phi = inst.phi if inst.phi is not None else float("inf")
        if phi < min_phi:
            min_phi = phi
            min_idx = idx

    return min_idx


def select_phi_max(instances: Sequence[InstanceView]) -> int:
    """
    Return the index of the instance with maximum Φ (phi).

    Useful for routing to the most integrated instance for complex tasks.

    Args:
        instances: Sequence of instance views

    Returns:
        Index of instance with maximum phi

    Raises:
        ValueError: If no instances available
    """
    if not instances:
        raise ValueError("No instances available for routing")

    max_idx = 0
    max_phi = float("-inf")

    for idx, inst in enumerate(instances):
        phi = inst.phi if inst.phi is not None else float("-inf")
        if phi > max_phi:
            max_phi = phi
            max_idx = idx

    return max_idx


def select_balanced(instances: Sequence[InstanceView], target_phi: float = 0.5) -> int:
    """
    Return the index of the instance whose Φ is closest to target.

    This provides balanced routing around a target integration level.

    Args:
        instances: Sequence of instance views
        target_phi: Target phi value (default: 0.5)

    Returns:
        Index of instance with phi closest to target

    Raises:
        ValueError: If no instances available
    """
    if not instances:
        raise ValueError("No instances available for routing")

    best_idx = 0
    best_distance = float("inf")

    for idx, inst in enumerate(instances):
        phi = inst.phi if inst.phi is not None else target_phi
        distance = abs(phi - target_phi)
        if distance < best_distance:
            best_distance = distance
            best_idx = idx

    return best_idx
