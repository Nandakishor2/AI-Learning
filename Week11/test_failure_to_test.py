"""
test_failure_to_test.py
Permanent Automated Regression Guardrail (Failure-to-Test Loop).
Converts the production defect uncovered during the Support Drill
(EMEA probation employee erroneously granted 5 days carry-over instead of 0 days)
into a permanent automated CI/CD test gate so it can never quietly return.
"""

import sys
import unittest
from pathlib import Path

# Ensure root is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from Week7.tools import get_employee_record, get_jurisdiction_rules
from Week7.workflow import FixedHRWorkflow

class TestFailureToTestRegressionLoop(unittest.TestCase):
    """Guarantees that past production defects are permanently blocked from regression."""

    def setUp(self):
        self.workflow = FixedHRWorkflow()

    def test_emea_probation_carry_over_strictly_zero(self):
        """
        REGRESSION GUARD: Drill Incident trace-prod-FAIL-88219.
        HR-207 Section 3.2 explicitly dictates that EMEA employees currently
        under probationary status are entitled to exactly ZERO (0) carry-over days.
        """
        emp_id = "EMP-1003" # Clara Dupont, EMEA, probationary: True
        question = "Can I roll over unused leave while in probation in EMEA?"
        
        result = self.workflow.run(emp_id, question)
        answer = result["final_answer"]

        # Deterministic Assertions
        self.assertEqual(result["status"], "COMPLETED")
        self.assertIn("0 days", answer, f"FAILED: Answer must state 0 days cap, got: '{answer}'")
        self.assertNotIn("5 days", answer, "REGRESSION DETECTED: 5 days carry-over must never be granted to EMEA probationers!")
        self.assertIn("HR-207", answer, "Citations must include HR-207")

    def test_apac_probation_tier1_vs_tier2_distinction(self):
        """
        Verifies that APAC probationary carry-over correctly distinguishes
        Tier 1 Staff (3 days) from Tier 2 Leads (5 days) under HR-207 Section 3.2.
        """
        # Tier 1 Staff
        res_t1 = self.workflow.run("EMP-1001", "What is my carry-over cap in APAC?")
        self.assertIn("3 days", res_t1["final_answer"])

        # Tier 2 Lead
        res_t2 = self.workflow.run("EMP-1002", "What is my carry-over cap in APAC?")
        self.assertIn("5 days", res_t2["final_answer"])

    def test_uk_medical_absence_fit_note_threshold(self):
        """
        Verifies UK medical absence certification threshold under HR-209.
        """
        res_uk = self.workflow.run("EMP-1006", "What medical note is required for 8+ days?")
        self.assertIn("8 days", res_uk["final_answer"])
        self.assertIn("GP Fit Note", res_uk["final_answer"])

if __name__ == "__main__":
    unittest.main()

