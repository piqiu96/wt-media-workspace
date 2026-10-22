"""Risk-based verification planning for `wt chg verify`."""

from __future__ import annotations

from scripts.lib.change_metadata import ChangeMetadata


def scenarios_for(change: ChangeMetadata) -> list[str]:
    runtime_repos = set(change.affected_repos) - {"wt-media-workspace"}
    scenarios = ["fast"]
    if change.risk in {"M", "H"}:
        scenarios.append("integration" if runtime_repos else "repo")
    scenarios.extend(change.verify_scenarios)
    scenarios = list(dict.fromkeys(scenarios))
    if "repo" in scenarios and "fast" in scenarios:
        scenarios.remove("fast")  # The repository suite includes its fast tests.
    return scenarios


def risk_note(change: ChangeMetadata) -> str | None:
    if change.risk == "H":
        return "H risk: also run targeted contract and e2e/real smoke when the CHG requires them; record evidence"
    return None
