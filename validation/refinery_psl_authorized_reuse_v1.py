from __future__ import annotations

import ast
import hashlib
import json
import re
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

UPSTREAM_COMMIT = "e8c9a2b2b2856b6449999dd0ec0d118f364ed0cd"
BASE = f"https://raw.githubusercontent.com/publicsuffix/list/{UPSTREAM_COMMIT}"
URLS = {
    "list": f"{BASE}/public_suffix_list.dat",
    "tests": f"{BASE}/tests/test_psl.txt",
    "license": f"{BASE}/LICENSE",
}
RESULT = Path("refinery-psl-authorized-reuse-result.json")
TEST_RE = re.compile(r"checkPublicSuffix\((null|'(?:[^'\\]|\\.)*'),\s*(null|'(?:[^'\\]|\\.)*')\);")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "refinery-authorized-reuse-control/1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def js_value(token: str):
    if token == "null":
        return None
    return ast.literal_eval(token)


def parse_tests(text: str):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        match = TEST_RE.fullmatch(line)
        if not match:
            raise ValueError(f"unparsed official test line: {line}")
        rows.append((js_value(match.group(1)), js_value(match.group(2))))
    if not rows:
        raise ValueError("official test corpus parsed to zero cases")
    return rows


@dataclass(frozen=True)
class Rules:
    exact: frozenset[str]
    wildcard: frozenset[str]
    exception: frozenset[str]


def idna_ascii(name: str) -> str:
    return ".".join(label.encode("idna").decode("ascii") for label in name.split("."))


def add_rule_forms(target: set[str], rule: str) -> None:
    target.add(rule)
    ascii_rule = idna_ascii(rule)
    target.add(ascii_rule)


def parse_rules(text: str) -> Rules:
    exact: set[str] = set()
    wildcard: set[str] = set()
    exception: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//"):
            continue
        line = line.lower()
        if line.startswith("!"):
            add_rule_forms(exception, line[1:])
        elif line.startswith("*."):
            add_rule_forms(wildcard, line[2:])
        else:
            add_rule_forms(exact, line)
    return Rules(frozenset(exact), frozenset(wildcard), frozenset(exception))


def registrable_with_psl(domain: str | None, rules: Rules) -> str | None:
    if domain is None or domain.startswith("."):
        return None
    value = domain.lower()
    labels = value.split(".")
    if not labels or any(label == "" for label in labels):
        return None

    exception_len = None
    best_len = 1
    for i in range(len(labels)):
        suffix = ".".join(labels[i:])
        label_count = len(labels) - i
        if suffix in rules.exception:
            exception_len = label_count
            break
        if suffix in rules.exact:
            best_len = max(best_len, label_count)
        if i + 1 < len(labels):
            wildcard_suffix = ".".join(labels[i + 1 :])
            if wildcard_suffix in rules.wildcard:
                best_len = max(best_len, label_count)

    public_suffix_len = (exception_len - 1) if exception_len is not None else best_len
    if len(labels) <= public_suffix_len:
        return None
    return ".".join(labels[-(public_suffix_len + 1) :])


def registrable_generic_rebuild(domain: str | None) -> str | None:
    """Generic code-only reconstruction with no accumulated PSL rule asset."""
    if domain is None or domain.startswith("."):
        return None
    labels = domain.lower().split(".")
    if len(labels) < 2 or any(label == "" for label in labels):
        return None
    return ".".join(labels[-2:])


def evaluate(name, fn, tests):
    start = time.perf_counter_ns()
    failures = []
    for domain, expected in tests:
        actual = fn(domain)
        if actual != expected:
            failures.append({"domain": domain, "expected": expected, "actual": actual})
    elapsed = time.perf_counter_ns() - start
    return {
        "arm": name,
        "pass_count": len(tests) - len(failures),
        "fail_count": len(failures),
        "total": len(tests),
        "accuracy": (len(tests) - len(failures)) / len(tests),
        "elapsed_ns": elapsed,
        "failures": failures,
    }


def main() -> None:
    blobs = {name: fetch(url) for name, url in URLS.items()}
    list_text = blobs["list"].decode("utf-8")
    tests_text = blobs["tests"].decode("utf-8")
    license_text = blobs["license"].decode("utf-8")

    if not license_text.startswith("Mozilla Public License Version 2.0"):
        raise SystemExit("upstream license is not the predeclared MPL-2.0 text")
    if "Any copyright is dedicated to the Public Domain." not in tests_text:
        raise SystemExit("official test corpus no longer carries the predeclared public-domain notice")
    if "Mozilla Public" not in str(list_text.splitlines()[0:8]):
        raise SystemExit("PSL data file no longer carries the expected MPL notice near its header")

    tests = parse_tests(tests_text)
    rules = parse_rules(list_text)
    reuse = evaluate("authorized_reuse_of_curated_psl", lambda d: registrable_with_psl(d, rules), tests)
    rebuild = evaluate("generic_code_only_rebuild_without_psl_asset", registrable_generic_rebuild, tests)

    delta = reuse["accuracy"] - rebuild["accuracy"]
    if reuse["fail_count"] == 0 and delta > 0:
        verdict = "AUTHORIZED_CURATED_ASSET_CORRECTNESS_ADVANTAGE_ESTABLISHED"
    elif reuse["accuracy"] <= rebuild["accuracy"]:
        verdict = "NO_AUTHORIZED_REUSE_ADVANTAGE_ESTABLISHED"
    else:
        verdict = "PARTIAL_AUTHORIZED_REUSE_ADVANTAGE_REQUIRES_REVIEW"

    result = {
        "schema_version": 1,
        "experiment": "refinery_psl_authorized_reuse_v1",
        "predeclared_upstream": {
            "repository": "publicsuffix/list",
            "commit": UPSTREAM_COMMIT,
            "list_url": URLS["list"],
            "tests_url": URLS["tests"],
            "license_url": URLS["license"],
            "list_sha256": sha256(blobs["list"]),
            "tests_sha256": sha256(blobs["tests"]),
            "license_sha256": sha256(blobs["license"]),
        },
        "authorization": {
            "reuse_basis": "MPL-2.0 license attached to publicsuffix/list and public_suffix_list.dat",
            "test_corpus_basis": "CC0/public-domain dedication stated in tests/test_psl.txt",
            "direct_owner_contact": False,
            "boundary": "This experiment relies only on the rights granted by the published licenses/notices and claims no broader permission.",
        },
        "capability": "derive registrable domain / eTLD+1-like boundary from a hostname",
        "scarce_asset_hypothesis": "the matching algorithm is generic, while the maintained multi-level/wildcard/exception suffix knowledge is accumulated curated state",
        "design": {
            "reuse_arm": "same bounded lookup logic supplied with the pinned curated PSL rule asset; Unicode rules are deterministically mirrored into standard-library IDNA ASCII form for equivalent punycode inputs",
            "rebuild_arm": "generic code-only default-rule heuristic with no PSL entries, wildcard knowledge, or exceptions",
            "evaluator": "official publicsuffix/list tests/test_psl.txt at the same pinned commit",
            "primary_metric": "exact expected registrable-domain match rate",
            "decision_rule": "PASS advantage only if reuse has zero official-test failures and strictly higher accuracy than rebuild",
            "timing_boundary": "elapsed_ns is diagnostic only and is not used for the verdict",
        },
        "rule_inventory": {
            "exact_and_idna_forms": len(rules.exact),
            "wildcard_and_idna_forms": len(rules.wildcard),
            "exception_and_idna_forms": len(rules.exception),
            "total_stored_forms": len(rules.exact) + len(rules.wildcard) + len(rules.exception),
        },
        "official_test_cases": len(tests),
        "arms": [reuse, rebuild],
        "accuracy_delta": delta,
        "verdict": verdict,
        "boundaries": [
            "This establishes only a bounded correctness advantage attributable to use of the pinned curated PSL asset on its official conformance corpus.",
            "It is not a price, revenue, product-market-fit, retention, or general software-quality result.",
            "It does not imply that every reused asset beats reconstruction.",
            "It does not transform MPL-2.0 permission into rights beyond the license terms.",
            "The generic rebuild arm intentionally excludes accumulated suffix knowledge so the experiment isolates the value of the curated rule asset rather than comparing two copies of the same data.",
        ],
    }
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": verdict,
        "official_test_cases": len(tests),
        "reuse_pass": reuse["pass_count"],
        "rebuild_pass": rebuild["pass_count"],
        "accuracy_delta": delta,
        "result_file": str(RESULT),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
