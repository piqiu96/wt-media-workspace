---
name: cross-repo-change
description: Coordinate changes that affect Cloud, Agent, Desktop, and Workspace together.
---
<!-- GENERATED FILE - DO NOT EDIT DIRECTLY -->
<!-- Source: skills/workspace/cross-repo-change/SKILL.md -->


# Cross-Repo Change

Use this skill when one task touches multiple WT Media repositories.

## Sequence

1. Identify affected repositories.
2. Identify contract providers and consumers.
3. Modify provider contracts first.
4. Update generated consumers second.
5. Keep business rules in Cloud unless execution-specific.
6. Test each repository independently.
7. Run cross-repo contract or integration checks.
8. Update the active delivery record, decision records, or release matrix when needed.

## Commit Rule

Keep commits separate per repository unless the user explicitly asks for a different workflow.
