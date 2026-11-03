"""Loop 04 component: classify tools by least-privilege policy."""

from __future__ import annotations

from typing import Any, Literal


PermissionDecision = Literal["allow", "require_approval", "deny"]


class PermissionPolicy:
    """Return allow, require_approval, or deny for each requested tool."""

    # TODO: Add the skill, planning, and bounded read-only EDA tool names.
    ALLOWED = frozenset({
        "list_skills","load_skill",
        "write_plan","request_approval",
        "dataset_info","sample_rows","describe_numeric",
        "data_quality_report","hypothesis_test","value_counts",
        "filter_inventory","lookup_vehicle","model_history",
        "compare_vehicles",
    })
    # TODO: plot_data and rank_inventory require a separate human grant.
    APPROVAL_REQUIRED = frozenset({
        "plot_data","rank_inventory",
    })

    def decide(
        self, tool_name: str, tool_input: dict[str, Any]
    ) -> tuple[PermissionDecision, str]:
        # TODO: Return ("allow", reason) for ALLOWED;
        # ("require_approval", reason) for APPROVAL_REQUIRED; otherwise
        # ("deny", reason). The reason is printed and saved in the tool trace.
        if tool_name in self.ALLOWED:
            return ("allow", f"{tool_name} is read-only / permitted")
        if tool_name in self.APPROVAL_REQUIRED:
            return ("require_approval",f"{tool_name} requires scoped user permission")
        return ("deny", f"{tool_name} is not allowed")