"""
policy_mcp_server.py
Second Model Context Protocol (MCP) Server for Regional Statutory HR Policies.
Provides get_jurisdiction_rules and search_policy_clause tools.
Demonstrates dynamic tool pluggability: agent discovers these tools dynamically without modifying agent code.
"""

import sys
import json
from typing import Dict, Any, List

STATUTORY_POLICIES = {
    "APAC": {
        "policy_id": "HR-207",
        "region": "APAC",
        "title": "Regional Leave Policy Addendum - APAC",
        "effective_date": "2026-01-01",
        "rules": {
            "probation_carry_over_cap": {"Tier 1 Staff": 3, "Tier 2 Leads": 5},
            "confirmed_carry_over_cap": 10,
            "monthly_accrual_rate": 1.75
        },
        "clauses": {
            "3.1": "Confirmed employees in APAC may carry over up to 10 unused annual leave days.",
            "3.2": "Probationary employees in APAC have carry-over capped at 3 days (Tier 1) or 5 days (Tier 2)."
        }
    },
    "EMEA": {
        "policy_id": "HR-207",
        "region": "EMEA",
        "title": "Regional Leave Policy Addendum - EMEA",
        "effective_date": "2026-01-01",
        "rules": {
            "probation_carry_over_cap": {"All Tiers": 0},
            "confirmed_carry_over_cap": 5,
            "annual_allocation": 25
        },
        "clauses": {
            "3.1": "Confirmed EMEA employees may roll over a maximum of 5 statutory days into Q1.",
            "3.2": "Probationary employees in EMEA are strictly barred from carrying over unused leave (0 days cap)."
        }
    },
    "NA": {
        "policy_id": "HR-208",
        "region": "NA",
        "title": "Parental & Caregiver Leave Policy - North America",
        "effective_date": "2026-01-15",
        "rules": {
            "primary_caregiver_weeks": {"Early Stage": 8, "Standard": 14, "Senior": 18},
            "secondary_caregiver_weeks": 4
        },
        "clauses": {
            "2.1": "Primary caregivers receive 8 weeks (under 12 months tenure) or 14 weeks (12-36 months tenure) at 100% pay.",
            "2.2": "Secondary caregivers receive 4 consecutive weeks of paid bonding leave."
        }
    },
    "LATAM": {
        "policy_id": "HR-208",
        "region": "LATAM",
        "title": "Parental & Caregiver Leave Policy - LATAM",
        "effective_date": "2026-01-15",
        "rules": {
            "caregiver_paid_weeks": {"Category A": 6, "Category B": 12},
            "paternity_days": 15
        },
        "clauses": {
            "2.1": "LATAM employees categorized as Category A receive 6 weeks; Category B receive 12 weeks paid caregiver leave."
        }
    },
    "UK": {
        "policy_id": "HR-209",
        "region": "UK",
        "title": "Statutory Sick Pay and Medical Absence - United Kingdom",
        "effective_date": "2026-02-01",
        "rules": {
            "medical_absence_fit_note_threshold_days": 8,
            "full_pay_weeks_max": 4
        },
        "clauses": {
            "4.1": "Any medical illness absence exceeding 7 consecutive calendar days (i.e. day 8 onward) mandates a GP Fit Note."
        }
    },
    "ANZ": {
        "policy_id": "HR-209",
        "region": "ANZ",
        "title": "National Employment Standards Addendum - ANZ",
        "effective_date": "2026-02-01",
        "rules": {
            "personal_leave_days": {"Year 1": 10, "Year 2+": 12},
            "carer_conversion_cap": {"Year 1": 5, "Year 2+": 8}
        },
        "clauses": {
            "5.2": "Employees with over 12 months tenure may convert up to 8 days of accrued personal leave to carer leave."
        }
    }
}

TOOL_DEFINITIONS = [
    {
        "name": "get_jurisdiction_rules",
        "description": "Fetch official statutory policy rules, carry-over caps, and leave entitlements for a given global jurisdiction.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "jurisdiction": {
                    "type": "string",
                    "enum": ["APAC", "EMEA", "LATAM", "NA", "ANZ", "UK"],
                    "description": "Target geographic region or legal jurisdiction"
                }
            },
            "required": ["jurisdiction"]
        }
    },
    {
        "name": "search_policy_clause",
        "description": "Search specific authoritative clause text from regional HR policy addenda.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "jurisdiction": {
                    "type": "string",
                    "enum": ["APAC", "EMEA", "LATAM", "NA", "ANZ", "UK"]
                },
                "section": {
                    "type": "string",
                    "description": "Section number (e.g., '3.1', '3.2', '2.1', '4.1')"
                }
            },
            "required": ["jurisdiction", "section"]
        }
    }
]

class PolicyMCPServer:
    """Standard Model Context Protocol (MCP) Server for Policy Rules."""

    def __init__(self, server_name: str = "policy-mcp-server", version: str = "1.0.0"):
        self.server_name = server_name
        self.version = version

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        msg_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": False}, "resources": {}, "prompts": {}},
                    "serverInfo": {"name": self.server_name, "version": self.version}
                }
            }
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": TOOL_DEFINITIONS}
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                res = self.execute_tool(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(res, indent=2)}],
                        "isError": False
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps({"error": str(e)})}],
                        "isError": True
                    }
                }
        else:
            return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method {method} not found"}}

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "get_jurisdiction_rules":
            jur = args.get("jurisdiction", "").strip().upper()
            if jur not in STATUTORY_POLICIES:
                raise KeyError(f"Jurisdiction '{jur}' not recognized.")
            return STATUTORY_POLICIES[jur]

        elif tool_name == "search_policy_clause":
            jur = args.get("jurisdiction", "").strip().upper()
            sec = args.get("section", "").strip()
            if jur not in STATUTORY_POLICIES:
                raise KeyError(f"Jurisdiction '{jur}' not recognized.")
            clauses = STATUTORY_POLICIES[jur]["clauses"]
            if sec not in clauses:
                return {"jurisdiction": jur, "section": sec, "text": "Clause section not found in policy."}
            return {
                "policy_id": STATUTORY_POLICIES[jur]["policy_id"],
                "jurisdiction": jur,
                "section": sec,
                "clause_text": clauses[sec]
            }
        else:
            raise ValueError(f"Unknown tool '{tool_name}' on Policy server.")

def run_stdio_server():
    server = PolicyMCPServer()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = server.handle_request(req)
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()
        except Exception as ex:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(ex)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    run_stdio_server()

