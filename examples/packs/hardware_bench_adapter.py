from __future__ import annotations

from typing import Any, Mapping

from citation_engine import ContextPack, GateResult


def make_measurement_gate_pack(
    *,
    measurement_ref: str,
    gate_id: str,
    expected_unit: str,
    lower: float | None = None,
    upper: float | None = None,
) -> ContextPack:
    """Map Hardware Splicer-style measurement gate semantics into a ContextPack.

    Current Hardware Splicer evidence gates expose fields such as `measurement_id`,
    `expected_unit`, `lower`, `upper`, and `required`. This adapter keeps those
    semantics outside core and emits only the neutral `GateResult` contract.
    """

    pack = ContextPack(name="hardware-splicer-bench-fixture", version="1")

    def measurement_gate(subject_ref: str, context: Mapping[str, Any]) -> GateResult:
        value = context.get("value")
        unit = context.get("unit")
        reasons: list[str] = []

        if unit != expected_unit:
            reasons.append(f"expected unit {expected_unit}, got {unit}")

        numeric_value: float | None
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            numeric_value = None
            reasons.append("measurement is not numeric")

        if numeric_value is not None:
            if lower is not None and numeric_value < lower:
                reasons.append(f"below lower bound {lower}")
            if upper is not None and numeric_value > upper:
                reasons.append(f"above upper bound {upper}")

        passed = not reasons
        return GateResult(
            gate_id=gate_id,
            passed=passed,
            basis_refs=(measurement_ref,),
            reason="measurement accepted" if passed else "; ".join(reasons),
        )

    pack.register_gate(gate_id, measurement_gate)
    return pack
