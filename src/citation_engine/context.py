from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from .models import GateResult


GateEvaluator = Callable[[str, Mapping[str, Any]], GateResult]
ToolCallable = Callable[..., Any]


@dataclass
class ContextPack:
    """Domain semantics attached to Citation Engine.

    Packs may know papers, circuits, policy instruments, people, datasets, or any
    other domain concept. The engine must not.
    """

    name: str
    version: str
    schemas: dict[str, type] = field(default_factory=dict)
    tools: dict[str, ToolCallable] = field(default_factory=dict)
    gates: dict[str, GateEvaluator] = field(default_factory=dict)
    rules: dict[str, Any] = field(default_factory=dict)
    workflows: dict[str, Any] = field(default_factory=dict)
    renderers: dict[str, Callable[..., Any]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def register_tool(self, name: str, tool: ToolCallable) -> None:
        if name in self.tools:
            raise ValueError(f"tool already registered: {name}")
        self.tools[name] = tool

    def register_gate(self, name: str, evaluator: GateEvaluator) -> None:
        if name in self.gates:
            raise ValueError(f"gate already registered: {name}")
        self.gates[name] = evaluator

    def register_rule(self, name: str, rule: Any) -> None:
        if name in self.rules:
            raise ValueError(f"rule already registered: {name}")
        self.rules[name] = rule
