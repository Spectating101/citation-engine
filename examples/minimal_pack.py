from citation_engine import ContextPack, GateResult


def make_pack(source_ref: str) -> ContextPack:
    """A deliberately domain-free example pack."""

    pack = ContextPack(name="minimal", version="1")

    def evidence_present(subject_ref, context):
        return GateResult(
            gate_id="evidence-present",
            passed=bool(context.get("accepted")),
            basis_refs=(source_ref,),
            reason="accepted evidence is required before promotion",
        )

    pack.register_gate("evidence-present", evidence_present)
    return pack
