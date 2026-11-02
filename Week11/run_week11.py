"""
run_week11.py
Master Orchestration Script for Week 11 Production & Observability Deliverables:
1. Production Tracing with Per-Step Time and Cost Spans.
2. Completed Support Drill: Locating planted defect from vague complaint.
3. Measured Cost-Per-Request Improvement via Semantic Caching & Routing.
4. Failure-to-Test Loop: Automated CI/CD Regression Guardrail.
"""

import sys
import unittest
from pathlib import Path

# Ensure root is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from Week11.tracer import ProductionTracer
from Week11.support_drill import populate_sample_production_log, run_support_drill
from Week11.caching_optimizer import run_cost_optimization_benchmark
from Week11.test_failure_to_test import TestFailureToTestRegressionLoop

def run_week11_master():
    print("=" * 80)
    print("WEEK 11: PRODUCTION OBSERVABILITY, COST CONTROL & FAILURE-TO-TEST LOOP")
    print("=" * 80)

    # 1. Tracing & Support Drill
    tracer = ProductionTracer()
    print("\n[Phase 1] Populating Production Log with Structured Per-Step Spans...")
    bad_trace_id = populate_sample_production_log(tracer, count=100)

    print("\n[Phase 2] Executing Support Drill from Vague Complaint...")
    complaint = (
        "An EMEA employee complained that yesterday around 14:00 the HR bot told them "
        "they have 5 days carry-over during probation, but our EMEA handbook says 0 days."
    )
    found_trace = run_support_drill(complaint)
    assert found_trace.get("trace_id") == bad_trace_id, "Support drill failed to pinpoint planted trace!"
    print("\n-> Verification SUCCESS: Defective trace found and root caused from vague complaint alone!")

    # 2. Cost Optimization Benchmark
    print("\n[Phase 3] Running Cost-Per-Request Optimization Benchmark...")
    cost_summary = run_cost_optimization_benchmark()
    assert cost_summary["cost_reduction_pct"] > 30.0, "Cost reduction below 30% target!"
    print(f"\n-> Verification SUCCESS: Cost reduced by {cost_summary['cost_reduction_pct']:.1f}% per request!")

    # 3. Failure-to-Test Loop
    print("\n[Phase 4] Executing Failure-to-Test Automated Regression Suite...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFailureToTestRegressionLoop)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    assert result.wasSuccessful(), "Regression tests failed!"
    print("\n-> Verification SUCCESS: Planted defect permanently converted into passing regression test!")

    print("\n" + "=" * 80)
    print("ALL WEEK 11 PRODUCTION QUALITY GATES PASSED")
    print("=" * 80)

if __name__ == "__main__":
    run_week11_master()

