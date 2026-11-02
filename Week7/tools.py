from typing import Literal, Dict, Any

JurisdictionType = Literal["APAC", "EMEA", "LATAM", "NA", "ANZ", "UK"]

# Mock Employee Database
EMPLOYEE_DB = {
    "EMP-1001": {"id": "EMP-1001", "name": "Alice Chen", "jurisdiction": "APAC", "tier": "Tier 1 Staff", "tenure_months": 4, "is_probationary": True},
    "EMP-1002": {"id": "EMP-1002", "name": "Bob Smith", "jurisdiction": "APAC", "tier": "Tier 2 Leads", "tenure_months": 5, "is_probationary": True},
    "EMP-1003": {"id": "EMP-1003", "name": "Clara Dupont", "jurisdiction": "EMEA", "tier": "All Tiers", "tenure_months": 3, "is_probationary": True},
    "EMP-1004": {"id": "EMP-1004", "name": "David Miller", "jurisdiction": "NA", "tier": "Standard", "tenure_months": 24, "is_probationary": False},
    "EMP-1005": {"id": "EMP-1005", "name": "Elena Gomez", "jurisdiction": "LATAM", "tier": "Category B", "tenure_months": 18, "is_probationary": False},
    "EMP-1006": {"id": "EMP-1006", "name": "Frank Wright", "jurisdiction": "UK", "tier": "Standard", "tenure_months": 36, "is_probationary": False},
    "EMP-1007": {"id": "EMP-1007", "name": "Grace Hopper", "jurisdiction": "ANZ", "tier": "Year 2+", "tenure_months": 28, "is_probationary": False},
    "EMP-1008": {"id": "EMP-1008", "name": "Hector Silva", "jurisdiction": "LATAM", "tier": "Category A", "tenure_months": 2, "is_probationary": True},
    "EMP-1009": {"id": "EMP-1009", "name": "Isabel Taylor", "jurisdiction": "NA", "tier": "Early Stage", "tenure_months": 8, "is_probationary": True},
    "EMP-1010": {"id": "EMP-1010", "name": "Jack Davies", "jurisdiction": "UK", "tier": "Standard", "tenure_months": 12, "is_probationary": False},
}

# Policy Rule Lookup
JURISDICTION_RULES = {
    "APAC": {
        "policy_id": "HR-207",
        "probation_carry_over_cap": {"Tier 1 Staff": 3, "Tier 2 Leads": 5},
        "confirmed_carry_over_cap": 10,
        "accrual_monthly": 1.75
    },
    "EMEA": {
        "policy_id": "HR-207",
        "probation_carry_over_cap": {"All Tiers": 0},
        "confirmed_carry_over_cap": 5,
        "annual_allocation": 25
    },
    "LATAM": {
        "policy_id": "HR-208",
        "caregiver_paid_weeks": {"Category A": 6, "Category B": 12},
        "paternity_days": 15
    },
    "NA": {
        "policy_id": "HR-208",
        "primary_caregiver_weeks": {"Early Stage": 8, "Standard": 14, "Senior": 18},
        "secondary_caregiver_weeks": 4
    },
    "ANZ": {
        "policy_id": "HR-209",
        "personal_leave_days": {"Year 1": 10, "Year 2+": 12},
        "carer_conversion_cap": {"Year 1": 5, "Year 2+": 8}
    },
    "UK": {
        "policy_id": "HR-209",
        "medical_absence_fit_note_threshold_days": 8,
        "full_pay_weeks_max": 4
    }
}

def get_employee_record(employee_id: str) -> Dict[str, Any]:
    """
    Fetch an employee's employment metadata by ID.
    Job: Read employee jurisdiction, tenure, tier, and probation status.
    """
    if employee_id not in EMPLOYEE_DB:
        return {"error": f"Employee {employee_id} not found."}
    return EMPLOYEE_DB[employee_id]

def search_handbook(query: str, policy_id: str) -> Dict[str, Any]:
    """
    Search specific policy handbook text clauses by policy ID.
    Job: Retrieve raw textual clauses from indexed policy markdown documents.
    """
    return {
        "policy_id": policy_id,
        "query": query,
        "snippet": f"Handbook policy text for {policy_id} matching query '{query}'."
    }

def get_jurisdiction_rules(jurisdiction: JurisdictionType) -> Dict[str, Any]:
    """
    Lookup regional leave statutory parameters and threshold rules for a given jurisdiction.
    Job: Retrieve structured statutory constants and calculation caps for an exact jurisdiction.
    """
    if jurisdiction not in JURISDICTION_RULES:
        return {"error": f"Unknown jurisdiction: {jurisdiction}"}
    return JURISDICTION_RULES[jurisdiction]
