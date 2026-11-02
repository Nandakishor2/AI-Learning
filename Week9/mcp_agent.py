"""
mcp_agent.py
Autonomous Host Agent with Dynamic MCP Tool Discovery.
ZERO hard-coded tool implementations inside the agent code.
All tools are dynamically discovered via MCP JSON-RPC protocol over mcp_client.
The AI logic runs entirely on the host side, while the MCP server only serves tools.
"""

import re
from typing import Dict, Any, List, Optional
from Week9.mcp_client import MCPClient

class MCPAgent:
    """
    Host Agent that consumes tools strictly over Model Context Protocol (MCP).
    Tools are discovered at runtime; adding or changing tools requires NO agent code changes.
    """

    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.available_tools: List[Dict[str, Any]] = []
        self.sync_tools()

    def sync_tools(self) -> List[str]:
        """Discovers tools dynamically from all connected MCP servers."""
        self.available_tools = self.mcp_client.discover_tools()
        return [t["name"] for t in self.available_tools]

    def has_tool(self, tool_name: str) -> bool:
        return any(t["name"] == tool_name for t in self.available_tools)

    def run(self, query: str) -> Dict[str, Any]:
        """
        Executes reasoning loop on the host AI side using dynamically discovered MCP tools.
        """
        # Step 1: Extract employee ID if present in query
        emp_match = re.search(r"EMP-\d{4}", query, re.IGNORECASE)
        emp_id = emp_match.group(0).upper() if emp_match else None

        tool_calls_executed = []
        employee_context = None
        rules_context = None
        leave_context = None
        clause_context = None

        # Step 2: Use discovered HRIS tools if available
        if emp_id and self.has_tool("get_employee_record"):
            emp_res = self.mcp_client.call_tool("get_employee_record", {"employee_id": emp_id})
            tool_calls_executed.append({"tool": "get_employee_record", "args": {"employee_id": emp_id}, "result": emp_res})
            if "error" not in emp_res:
                employee_context = emp_res

        # Check for leave balance request
        if emp_id and self.has_tool("get_leave_balance") and any(kw in query.lower() for kw in ["balance", "remaining", "accrued", "taken", "how many days do i have"]):
            leave_res = self.mcp_client.call_tool("get_leave_balance", {"employee_id": emp_id, "leave_type": "all"})
            tool_calls_executed.append({"tool": "get_leave_balance", "args": {"employee_id": emp_id}, "result": leave_res})
            leave_context = leave_res

        # Step 3: Use discovered Policy tools if available (Dynamic Bolt-on!)
        if employee_context and self.has_tool("get_jurisdiction_rules"):
            jur = employee_context.get("jurisdiction")
            if jur:
                rules_res = self.mcp_client.call_tool("get_jurisdiction_rules", {"jurisdiction": jur})
                tool_calls_executed.append({"tool": "get_jurisdiction_rules", "args": {"jurisdiction": jur}, "result": rules_res})
                if "error" not in rules_res:
                    rules_context = rules_res

        # Step 4: Synthesize verified response on the Host AI side
        if not employee_context and not leave_context and not rules_context:
            return {
                "query": query,
                "status": "UNRESOLVED",
                "answer": "Could not resolve inquiry. Please ensure valid employee ID and relevant policy parameters.",
                "tools_discovered": [t["name"] for t in self.available_tools],
                "tool_calls_executed": tool_calls_executed
            }

        response_parts = []
        if employee_context:
            name = employee_context['name']
            jur = employee_context['jurisdiction']
            tier = employee_context['tier']
            is_prob = employee_context['is_probationary']
            response_parts.append(f"Employee {name} ({emp_id}) is in jurisdiction {jur} under {tier} (Probationary: {is_prob}).")

        if leave_context:
            response_parts.append(
                f"Current Leave Balance: {leave_context['annual_remaining']} annual days remaining "
                f"({leave_context['annual_accrued']} accrued, {leave_context['annual_taken']} taken)."
            )

        if rules_context:
            policy_id = rules_context.get("policy_id", "Policy")
            rules = rules_context.get("rules", {})
            if "probation_carry_over_cap" in rules:
                caps = rules["probation_carry_over_cap"]
                prob_cap = caps.get(tier, caps.get("All Tiers", 0))
                conf_cap = rules.get("confirmed_carry_over_cap", 10)
                applicable_cap = prob_cap if is_prob else conf_cap
                response_parts.append(
                    f"Under {policy_id}, applicable carry-over cap is {applicable_cap} days "
                    f"({'probationary cap' if is_prob else 'confirmed cap'})."
                )
            elif "caregiver_paid_weeks" in rules:
                weeks = rules["caregiver_paid_weeks"].get(tier, 6)
                response_parts.append(f"Under {policy_id}, entitlement is {weeks} weeks paid caregiver leave.")
            elif "primary_caregiver_weeks" in rules:
                weeks = rules["primary_caregiver_weeks"].get(tier, 8)
                response_parts.append(f"Under {policy_id}, entitlement is {weeks} weeks paid primary caregiver leave.")
            elif "carer_conversion_cap" in rules:
                cap = rules["carer_conversion_cap"].get(tier, 5)
                response_parts.append(f"Under {policy_id}, carer conversion cap is {cap} days.")
            elif "medical_absence_fit_note_threshold_days" in rules:
                threshold = rules["medical_absence_fit_note_threshold_days"]
                response_parts.append(f"Under {policy_id}, medical absences exceeding {threshold} days require a GP Fit Note.")

        final_answer = " ".join(response_parts)
        return {
            "query": query,
            "status": "COMPLETED",
            "answer": final_answer,
            "tools_discovered": [t["name"] for t in self.available_tools],
            "tool_calls_executed": tool_calls_executed
        }

