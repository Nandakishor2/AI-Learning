import re
from typing import Any, Tuple

# Common Employee Identifier patterns
EMP_ID_PATTERN = re.compile(r'\b(?:EMP|EID|STAFF|ID)[-_]?\d{3,8}\b', re.IGNORECASE)
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_PATTERN = re.compile(r'\b(?:\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b')
KNOWN_NAMES_PATTERN = re.compile(
    r'\b(?:John Doe|Jane Smith|Alice Johnson|Bob Miller|Charlie Brown|David Wilson|Sarah Connor|Emily Davis|Michael Scott|Jim Halpert|Pam Beesly)\b',
    re.IGNORECASE
)

def redact_pii(text: str) -> str:
    """
    Redacts employee names, IDs, email addresses, and contact info before persistence.
    """
    if not isinstance(text, str):
        return text
    
    redacted = EMP_ID_PATTERN.sub("[REDACTED_EMP_ID]", text)
    redacted = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", redacted)
    redacted = PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)
    redacted = KNOWN_NAMES_PATTERN.sub("[REDACTED_EMPLOYEE_NAME]", redacted)
    return redacted

def validate_privacy_cleanliness(data: Any) -> Tuple[int, list]:
    """
    Recursively scans structured data (dict, list, str) to verify that no
    employee identifiers or sensitive PII leaked unredacted.
    Returns: (employee_identifiers_found, list_of_violations)
    """
    violations = []
    
    def check_value(val, path=""):
        if isinstance(val, str):
            if EMP_ID_PATTERN.search(val):
                violations.append(f"Unredacted Employee ID at {path}: {val}")
            if EMAIL_PATTERN.search(val):
                violations.append(f"Unredacted Email at {path}: {val}")
            if KNOWN_NAMES_PATTERN.search(val):
                violations.append(f"Unredacted Employee Name at {path}: {val}")
        elif isinstance(val, dict):
            for k, v in val.items():
                check_value(v, f"{path}.{k}")
        elif isinstance(val, list):
            for i, v in enumerate(val):
                check_value(v, f"{path}[{i}]")

    check_value(data, "root")
    return len(violations), violations
