"""
squad.py
Multi-Agent HR Policy Squad Architecture.
Composed of an Orchestrator/Manager Agent plus two Narrow Specialists:
1. Manager: PolicySquadManager
2. Specialist 1: EmployeeDataSpecialist (HRIS Employee Lookup)
3. Specialist 2: StatutoryComplianceSpecialist (Handbook Statutory Rules)
Inter-agent communication follows the standard A2A protocol.
"""

import time
import uuid
from typing import Dict, Any, List
from Week10.a2a_protocol import AgentCard, A2AMessage, TaskState
from Week7.tools import get_employee_record, get_jurisdiction_rules

PRICE_PER_1K_TOKENS = 0.00015

class EmployeeDataSpecialist:
    """Specialist 1: Narrow focus on employee identity, tier, tenure, and probation."""

    def __init__(self):
        self.card = AgentCard(
            agent_id="specialist-emp-data",
            name="EmployeeDataSpecialist",
            role="Employee Context Specialist",
            description="Resolves employment records, verification of tenure, probation status, and jurisdiction.",
            capabilities=["employee_lookup", "probation_verification", "tenure_audit"],
            input_contract={"employee_id": "string (EMP-XXXX)"},
            output_contract={"employee_profile": "dict containing name, jurisdiction, tier, tenure, is_prob"}
        )

    def execute_task(self, msg: A2AMessage) -> A2AMessage:
        # Specialist System prompt (350 tokens) + Re-sent user query & task envelope (250 tokens) = 600 tokens
        tokens_consumed = 600
        emp_id = msg.payload.get("employee_id")
        rec = get_employee_record(emp_id)

        if "error" in rec:
            return A2AMessage(
                task_id=msg.task_id,
                sender_id=self.card.agent_id,
                recipient_id=msg.sender_id,
                task_type="employee_resolution_response",
                state=TaskState.FAILED,
                payload={"error": f"Employee {emp_id} not found."},
                parent_task_id=msg.task_id,
                token_usage=tokens_consumed
            )

        return A2AMessage(
            task_id=msg.task_id,
            sender_id=self.card.agent_id,
            recipient_id=msg.sender_id,
            task_type="employee_resolution_response",
            state=TaskState.COMPLETED,
            payload={"profile": rec},
            parent_task_id=msg.task_id,
            token_usage=tokens_consumed
        )


class StatutoryComplianceSpecialist:
    """Specialist 2: Narrow focus on regional statutory addenda and entitlement rules."""

    def __init__(self):
        self.card = AgentCard(
            agent_id="specialist-statutory-rules",
            name="StatutoryComplianceSpecialist",
            role="Regional Handbook Compliance Specialist",
            description="Evaluates statutory policy clauses, regional carry-over thresholds, and leave caps.",
            capabilities=["jurisdiction_lookup", "carry_over_computation", "caregiver_rules"],
            input_contract={"jurisdiction": "string", "tier": "string", "is_probationary": "bool"},
            output_contract={"entitlement": "dict containing policy_id, caps, and legal summary"}
        )

    def execute_task(self, msg: A2AMessage) -> A2AMessage:
        # Specialist System prompt (400 tokens) + Re-sent employee payload & query context (350 tokens) = 750 tokens
        tokens_consumed = 750
        jurisdiction = msg.payload.get("jurisdiction")
        tier = msg.payload.get("tier")
        is_prob = msg.payload.get("is_probationary", False)

        rules = get_jurisdiction_rules(jurisdiction)
        if "error" in rules:
            return A2AMessage(
                task_id=msg.task_id,
                sender_id=self.card.agent_id,
                recipient_id=msg.sender_id,
                task_type="statutory_evaluation_response",
                state=TaskState.FAILED,
                payload={"error": f"Unknown jurisdiction {jurisdiction}"},
                parent_task_id=msg.task_id,
                token_usage=tokens_consumed
            )

        policy_id = rules.get("policy_id", "HR-Policy")
        result_payload = {"policy_id": policy_id, "jurisdiction": jurisdiction}

        if jurisdiction == "APAC":
            cap = rules["probation_carry_over_cap"].get(tier, rules["confirmed_carry_over_cap"]) if is_prob else rules["confirmed_carry_over_cap"]
            result_payload["carry_over_cap"] = cap
            result_payload["summary"] = f"Carry-over cap is {cap} days under {policy_id}."
        elif jurisdiction == "EMEA":
            cap = rules["probation_carry_over_cap"].get(tier, 0) if is_prob else rules["confirmed_carry_over_cap"]
            result_payload["carry_over_cap"] = cap
            result_payload["summary"] = f"Carry-over cap is {cap} days under {policy_id}."
        elif jurisdiction == "LATAM":
            wks = rules["caregiver_paid_weeks"].get(tier, 6)
            result_payload["caregiver_weeks"] = wks
            result_payload["summary"] = f"Entitled to {wks} weeks of paid caregiver leave under {policy_id}."
        elif jurisdiction == "NA":
            wks = rules["primary_caregiver_weeks"].get(tier, 8)
            result_payload["caregiver_weeks"] = wks
            result_payload["summary"] = f"Entitled to {wks} weeks of paid primary caregiver leave under {policy_id}."
        elif jurisdiction == "ANZ":
            cap = rules["carer_conversion_cap"].get(tier, 5)
            result_payload["conversion_cap"] = cap
            result_payload["summary"] = f"Carer's Conversion Cap is {cap} days under {policy_id}."
        elif jurisdiction == "UK":
            threshold = rules["medical_absence_fit_note_threshold_days"]
            result_payload["fit_note_threshold"] = threshold
            result_payload["summary"] = f"Requires a GP Fit Note for absences exceeding {threshold} days under {policy_id}."

        return A2AMessage(
            task_id=msg.task_id,
            sender_id=self.card.agent_id,
            recipient_id=msg.sender_id,
            task_type="statutory_evaluation_response",
            state=TaskState.COMPLETED,
            payload=result_payload,
            parent_task_id=msg.task_id,
            token_usage=tokens_consumed
        )


class PolicySquadManager:
    """Manager / Orchestrator Agent. Coordinates specialists via A2A protocol."""

    def __init__(self):
        self.card = AgentCard(
            agent_id="manager-policy-squad",
            name="PolicySquadManager",
            role="HR Policy Squad Orchestrator",
            description="Decomposes user queries, coordinates specialists, and synthesizes audited responses.",
            capabilities=["task_planning", "specialist_delegation", "answer_synthesis"],
            input_contract={"query": "string", "employee_id": "string"},
            output_contract={"final_answer": "string", "trace": "list of A2AMessages"}
        )
        self.emp_specialist = EmployeeDataSpecialist()
        self.rules_specialist = StatutoryComplianceSpecialist()

    def run(self, emp_id: str, question: str) -> Dict[str, Any]:
        start_time = time.perf_counter()
        a2a_log: List[Dict[str, Any]] = []
        total_tokens = 0

        # Manager initial planning prompt & system overhead: 450 tokens
        total_tokens += 450

        # Step 1: Hand-off 1 -> Delegate to EmployeeDataSpecialist
        task1_id = f"task-emp-{uuid.uuid4().hex[:6]}"
        msg1 = A2AMessage(
            task_id=task1_id,
            sender_id=self.card.agent_id,
            recipient_id=self.emp_specialist.card.agent_id,
            task_type="resolve_employee_context",
            state=TaskState.PENDING,
            payload={"employee_id": emp_id, "query_context": question}
        )
        a2a_log.append(msg1.to_dict())

        res1 = self.emp_specialist.execute_task(msg1)
        total_tokens += res1.token_usage
        a2a_log.append(res1.to_dict())

        if res1.state == TaskState.FAILED:
            latency = (time.perf_counter() - start_time) * 1000.0
            return {
                "system": "PolicySquadMultiAgent",
                "status": "FAILED",
                "answer": res1.payload.get("error"),
                "latency_ms": latency,
                "total_tokens": total_tokens,
                "cost_usd": (total_tokens / 1000.0) * PRICE_PER_1K_TOKENS,
                "a2a_trace": a2a_log
            }

        profile = res1.payload["profile"]

        # Step 2: Hand-off 2 -> Delegate to StatutoryComplianceSpecialist
        # Re-sends query context + accumulated profile to specialist
        task2_id = f"task-rules-{uuid.uuid4().hex[:6]}"
        msg2 = A2AMessage(
            task_id=task2_id,
            sender_id=self.card.agent_id,
            recipient_id=self.rules_specialist.card.agent_id,
            task_type="evaluate_statutory_rules",
            state=TaskState.PENDING,
            payload={
                "jurisdiction": profile["jurisdiction"],
                "tier": profile["tier"],
                "is_probationary": profile["is_probationary"],
                "query_context": question
            }
        )
        a2a_log.append(msg2.to_dict())

        res2 = self.rules_specialist.execute_task(msg2)
        total_tokens += res2.token_usage
        a2a_log.append(res2.to_dict())

        # Step 3: Manager Final Synthesis
        # Manager ingests both responses and synthesizes final answer (550 tokens)
        total_tokens += 550

        summary = res2.payload.get("summary", "")
        final_answer = f"{profile['name']} ({profile['tier']}, {profile['jurisdiction']}): {summary}"

        latency = (time.perf_counter() - start_time) * 1000.0
        cost = (total_tokens / 1000.0) * PRICE_PER_1K_TOKENS

        return {
            "system": "PolicySquadMultiAgent",
            "status": "COMPLETED",
            "answer": final_answer,
            "latency_ms": latency,
            "total_tokens": total_tokens,
            "cost_usd": cost,
            "a2a_trace": a2a_log
        }

