# Independent uv public attestation validation

This branch exists only to produce a public, independent execution record for one public artifact used by Refinery's Commons machine-evidence gate.

It does **not** copy or execute private `alpha-platform` source.

The workflow verifies:

- `ghcr.io/astral-sh/uv:0.12.3-python3.13-trixie-slim` resolves to the predeclared digest `sha256:5f3c58899cb4ab5b723f81641d6aed08968e6c93f9a84641321ae66ba7103f42`;
- GitHub CLI cryptographically verifies an SLSA provenance attestation for `oci://ghcr.io/astral-sh/uv@<digest>` under repository identity `astral-sh/uv`;
- at least one verified statement contains the exact SHA-256 subject digest.

A PASS proves only the public artifact/attestation fact. It does not prove Refinery's private adapter executed, does not transfer evidence to sibling implementations, and does not establish correctness, recommendation, deployment, adoption, external value or reuse rights.
