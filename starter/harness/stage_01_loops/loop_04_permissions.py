"""Loop 04 scaffold: authorize each protected request before it runs."""

from __future__ import annotations

from typing import Any

from .loop_01_non_production import HarnessLoop
from harness.stage_06_permissions import PermissionPolicy


class PermissionsLoop(HarnessLoop):
    """A grant applies to one exact tool name and argument object."""

    def __init__(self, *args: Any, **kwargs: Any):
        # Scoped approval and exact-call replay add model round trips beyond the
        # foundational loop's normal budget.
        kwargs.setdefault("max_loop_iterations", 30)
        super().__init__(*args, **kwargs)
        self.permissions = PermissionPolicy()

    @staticmethod
    def _same_request(left: dict[str, Any] | None, right: dict[str, Any]) -> bool:
        """Report whether a stored grant covers exactly this request."""
        # TODO: A grant is scoped to one tool name and one argument object.
        # Compare the stored request against the current one in full, so a
        # grant for plot_data(plot_type="scatter") cannot authorize a later
        # plot_data(plot_type="bar").
        if left is None:
            return False
        return left == right



    def before_tool_execution(
        self, tool_name: str, tool_input: dict[str, Any]
    ) -> str | None:
        # TODO: Ask self.permissions.decide for allow, require_approval, or
        # deny. Log every check as {"component": "permission_check", "tool":
        # tool_name, "input": tool_input, "decision": decision, "reason":
        # reason}, then print exactly "PERMISSION CHECK: <tool_name> ->
        # <decision>". Use self._same_request against state.granted_permission
        # before blocking a protected call: on a match, clear that one-use grant
        # and let the handler execute. For deny, return a DENIED message. For
        # require_approval without a matching grant, save {"tool": tool_name,
        # "input": tool_input} in state.permission_request, set
        # state.permission_required, and return a BLOCKED message.
        decision, reason = self.permissions.decide(tool_name, tool_input)
        current = {"tool": tool_name, "input": tool_input}

        if decision == "require_approval" and self._same_request(
            self.state.granted_permission, current
        ):
            self.state.granted_permission = None
            decision = "allow"
            reason = "one-time grant consumed"

        self.state.tool_run_log.append({
            "component": "permission_check",
            "tool": tool_name,
            "input": tool_input,
            "decision": decision,
            "reason": reason,
        })
        print(f"PERMISSION CHECK: {tool_name} -> {decision}")

        if decision == "allow":
            return None
        if decision == "deny":
            return f"DENIED: {reason}"

        self.state.permission_request = current
        self.state.permission_required = True
        return f"BLOCKED: {reason}"


    def pause_status(self) -> str | None:
        # TODO: Return "permission_required" while a protected request waits
        # for a human decision; otherwise return None.
        if self.state.permission_required:
            return "permission_required"
        return None

    def grant_pending_permission(self) -> None:
        # TODO: Called by main.py only after the user approves. Move the
        # pending request into state.granted_permission and clear the pending
        # flag. Log {"component": "permission_grant", "tool": tool_name,
        # "input": tool_input, "event": "grant", "scope": "one_exact_call"}.
        # Then print exactly "PERMISSION GRANTED: <tool_name>". The grant is
        # consumed by the matching before_tool_execution.
        request = self.state.permission_request
        if request is None:
            return
        self.state.granted_permission = request
        self.state.permission_required = False
        self.state.permission_request = None

        self.state.tool_run_log.append({
            "component": "permission_grant",
            "tool": request["tool"],
            "input": request["input"],
            "event": "grant",
            "scope": "one_exact_call",
        })
        print(f"PERMISSION GRANTED: {request['tool']}")

    def resume_after_permission(
        self,
        permission_response: Any,
        tool_results: list[dict[str, Any]],
        starting_loop: int,
    ) -> dict[str, Any]:
        # TODO: Resume the inherited loop using permission_response.id.
        # Include tool_results plus a user message asking the model to reissue
        # the *identical* tool call and arguments. Do not run the tool here.
        request_input = tool_results + [{
            "type": "message",
            "role": "user",
            "content": (
                "The user granted permission for that exact tool call."
                "Reissue the identical tool name and arguments now."
            ),
        }]

        return self._run_until_pause_or_complete(
            request_input,
            permission_response.id,
            starting_loop,
        )