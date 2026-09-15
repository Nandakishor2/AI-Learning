from typing import List, Dict

EVAL_DATASET: List[Dict] = [
    # Mode 1: exact_token_miss
    {
        "case_id": "CASE-01",
        "question": "What does HR-207 section 3.2 specify regarding carry-over caps for Tier 1 staff in APAC?",
        "expected_behavior": "Must answer 3 days carry-over cap with 60 days post-probation forfeiture window and cite HR-207 Section 3.2.",
        "taxonomy_mode": "exact_token_miss",
        "source_trace_id": "trace_reg_01",
        "expected_status": "answered",
        "expected_policy_id": "HR-207",
        "expected_section": "3.2",
        "required_terms": ["3", "Tier 1", "60 days"],
        "region": "APAC"
    },
    {
        "case_id": "CASE-02",
        "question": "Under HR-207 section 3.2 in APAC, what is the probationary carry-over cap for Tier 2 Leads?",
        "expected_behavior": "Must state 5 days carry-over cap with 90 days forfeiture window.",
        "taxonomy_mode": "exact_token_miss",
        "source_trace_id": "trace_reg_02",
        "expected_status": "answered",
        "expected_policy_id": "HR-207",
        "expected_section": "3.2",
        "required_terms": ["5", "Tier 2", "90 days"],
        "region": "APAC"
    },
    {
        "case_id": "CASE-03",
        "question": "What does HR-208 section 2.1 state for Category B continuous service in LATAM?",
        "expected_behavior": "Must state 12 weeks full pay with 100% health continuation for 6+ months service.",
        "taxonomy_mode": "exact_token_miss",
        "source_trace_id": "trace_w5_03",
        "expected_status": "answered",
        "expected_policy_id": "HR-208",
        "expected_section": "2.1",
        "required_terms": ["12 weeks", "Category B", "100% health"],
        "region": "LATAM"
    },
    {
        "case_id": "CASE-04",
        "question": "Under HR-209 section 2.1 in UK, what certification is required for absences of 8+ days?",
        "expected_behavior": "Must state Statement of Fitness for Work (GP Fit Note) with 100% pay up to 4 weeks, then 50% for 8 weeks.",
        "taxonomy_mode": "exact_token_miss",
        "source_trace_id": "trace_w5_04",
        "expected_status": "answered",
        "expected_policy_id": "HR-209",
        "expected_section": "2.1",
        "required_terms": ["GP Fit Note", "Statement of Fitness", "4 weeks"],
        "region": "UK"
    },
    {
        "case_id": "CASE-05",
        "question": "What does section 2.1 of HR-209 specify as the Carer's Conversion Cap for Year 2+ employees in ANZ?",
        "expected_behavior": "Must specify Max 8 days carer's conversion cap out of 12 days annual personal leave.",
        "taxonomy_mode": "exact_token_miss",
        "source_trace_id": "trace_w5_05",
        "expected_status": "answered",
        "expected_policy_id": "HR-209",
        "expected_section": "2.1",
        "required_terms": ["8 days", "Year 2+"],
        "region": "ANZ"
    },

    # Mode 2: tenure_probation_confusion
    {
        "case_id": "CASE-06",
        "question": "What is the carry-over cap for unconfirmed probationary employees in EMEA under HR-207?",
        "expected_behavior": "Must state 0 days (unconfirmed probationary employees are prohibited from rolling over leave).",
        "taxonomy_mode": "tenure_probation_confusion",
        "source_trace_id": "trace_w5_06",
        "expected_status": "answered",
        "expected_policy_id": "HR-207",
        "expected_section": "3.2",
        "required_terms": ["0", "prohibited", "EMEA"],
        "region": "EMEA"
    },
    {
        "case_id": "CASE-07",
        "question": "How many weeks of paid primary caregiver leave does an Early Stage (<12 months service) employee receive in North America?",
        "expected_behavior": "Must state 8 weeks full pay with 4 weeks unpaid extension allowed under HR-208 Section 2.1.",
        "taxonomy_mode": "tenure_probation_confusion",
        "source_trace_id": "trace_w5_07",
        "expected_status": "answered",
        "expected_policy_id": "HR-208",
        "expected_section": "2.1",
        "required_terms": ["8 weeks", "4 weeks"],
        "region": "NA"
    },
    {
        "case_id": "CASE-08",
        "question": "What is the paid primary caregiver leave for Senior tenure (>36 months) in North America?",
        "expected_behavior": "Must state 18 weeks full pay with 8 weeks unpaid extension under HR-208 Section 2.1.",
        "taxonomy_mode": "tenure_probation_confusion",
        "source_trace_id": "trace_w5_08",
        "expected_status": "answered",
        "expected_policy_id": "HR-208",
        "expected_section": "2.1",
        "required_terms": ["18 weeks", "8 weeks"],
        "region": "NA"
    },
    {
        "case_id": "CASE-09",
        "question": "How many weeks of paid leave does a Category A primary caregiver (<6 months continuous service) receive in LATAM?",
        "expected_behavior": "Must state 6 weeks full pay plus local statutory stipend under HR-208 Section 2.1.",
        "taxonomy_mode": "tenure_probation_confusion",
        "source_trace_id": "trace_w5_09",
        "expected_status": "answered",
        "expected_policy_id": "HR-208",
        "expected_section": "2.1",
        "required_terms": ["6 weeks", "Category A"],
        "region": "LATAM"
    },
    {
        "case_id": "CASE-10",
        "question": "In ANZ, what is the Carer's Conversion Cap for Year 1 employees under HR-209?",
        "expected_behavior": "Must state Max 5 days out of 10 days annual personal leave under HR-209 Section 2.1.",
        "taxonomy_mode": "tenure_probation_confusion",
        "source_trace_id": "trace_w5_10",
        "expected_status": "answered",
        "expected_policy_id": "HR-209",
        "expected_section": "2.1",
        "required_terms": ["5 days", "Year 1"],
        "region": "ANZ"
    },

    # Mode 3: regional_policy_jurisdiction_mismatch
    {
        "case_id": "CASE-11",
        "question": "What is the standard annual leave entitlement for full-time employees in EMEA under HR-207?",
        "expected_behavior": "Must state 25 working days per calendar year in EMEA under HR-207 Section 2.",
        "taxonomy_mode": "regional_policy_jurisdiction_mismatch",
        "source_trace_id": "trace_w5_11",
        "expected_status": "answered",
        "expected_policy_id": "HR-207",
        "expected_section": "2",
        "required_terms": ["25", "working days"],
        "region": "EMEA"
    },
    {
        "case_id": "CASE-12",
        "question": "What is the monthly annual leave accrual rate for APAC employees under HR-207?",
        "expected_behavior": "Must state 1.75 days per completed calendar month of service under HR-207 Section 2.",
        "taxonomy_mode": "regional_policy_jurisdiction_mismatch",
        "source_trace_id": "trace_w5_12",
        "expected_status": "answered",
        "expected_policy_id": "HR-207",
        "expected_section": "2",
        "required_terms": ["1.75 days", "month"],
        "region": "APAC"
    },
    {
        "case_id": "CASE-13",
        "question": "How many consecutive calendar days of paid paternity leave are provided to non-birthing parents in LATAM?",
        "expected_behavior": "Must state 15 consecutive calendar days under HR-208 Section 2.2.",
        "taxonomy_mode": "regional_policy_jurisdiction_mismatch",
        "source_trace_id": "trace_w5_13",
        "expected_status": "answered",
        "expected_policy_id": "HR-208",
        "expected_section": "2.2",
        "required_terms": ["15", "consecutive calendar days"],
        "region": "LATAM"
    },
    {
        "case_id": "CASE-14",
        "question": "What is the secondary caregiver entitlement in North America under HR-208?",
        "expected_behavior": "Must state 4 consecutive weeks of fully paid leave after 90 calendar days of service under Section 2.2.",
        "taxonomy_mode": "regional_policy_jurisdiction_mismatch",
        "source_trace_id": "trace_w5_14",
        "expected_status": "answered",
        "expected_policy_id": "HR-208",
        "expected_section": "2.2",
        "required_terms": ["4 consecutive weeks", "90 calendar days"],
        "region": "NA"
    },
    {
        "case_id": "CASE-15",
        "question": "What documentation is required for unplanned personal leave exceeding 2 consecutive working days in ANZ?",
        "expected_behavior": "Must state medical certificate or statutory declaration under HR-209 Section 2.2.",
        "taxonomy_mode": "regional_policy_jurisdiction_mismatch",
        "source_trace_id": "trace_w5_15",
        "expected_status": "answered",
        "expected_policy_id": "HR-209",
        "expected_section": "2.2",
        "required_terms": ["medical certificate", "statutory declaration", "2 consecutive"],
        "region": "ANZ"
    },

    # Mode 4: ungrounded_policy_hallucination (Out of Corpus Refusals)
    {
        "case_id": "CASE-16",
        "question": "What is the corporate sabbatical policy for employees with 5+ years of tenure?",
        "expected_behavior": "Must refuse with exact refusal string because sabbatical policy is not defined in any addenda.",
        "taxonomy_mode": "ungrounded_policy_hallucination",
        "source_trace_id": "trace_w5_16",
        "expected_status": "refused",
        "expected_policy_id": "NONE",
        "expected_section": "NONE",
        "required_terms": ["don't have enough information", "not have sufficient information"]
    },
    {
        "case_id": "CASE-17",
        "question": "What is the monthly home internet and phone stipend reimbursement rate for remote APAC workers?",
        "expected_behavior": "Must refuse with exact refusal string because remote work stipends are not defined in the addenda.",
        "taxonomy_mode": "ungrounded_policy_hallucination",
        "source_trace_id": "trace_w5_17",
        "expected_status": "refused",
        "expected_policy_id": "NONE",
        "expected_section": "NONE",
        "required_terms": ["don't have enough information", "not have sufficient information"]
    },
    {
        "case_id": "CASE-18",
        "question": "Under HR-999 section 1.0, what is the executive equity vesting schedule upon acquisition?",
        "expected_behavior": "Must refuse with exact refusal string because HR-999 does not exist in the corpus.",
        "taxonomy_mode": "ungrounded_policy_hallucination",
        "source_trace_id": "trace_w5_18",
        "expected_status": "refused",
        "expected_policy_id": "NONE",
        "expected_section": "NONE",
        "required_terms": ["don't have enough information", "not have sufficient information"]
    },
    {
        "case_id": "CASE-19",
        "question": "How many days of paid bereavement leave are provided for extended family members in EMEA?",
        "expected_behavior": "Must refuse with exact refusal string because bereavement leave is not defined in HR-207 EMEA.",
        "taxonomy_mode": "ungrounded_policy_hallucination",
        "source_trace_id": "trace_w5_19",
        "expected_status": "refused",
        "expected_policy_id": "NONE",
        "expected_section": "NONE",
        "required_terms": ["don't have enough information", "not have sufficient information"]
    },
    {
        "case_id": "CASE-20",
        "question": "What is the annual education assistance budget for software engineers in North America?",
        "expected_behavior": "Must refuse with exact refusal string because tuition assistance is not in the corpus.",
        "taxonomy_mode": "ungrounded_policy_hallucination",
        "source_trace_id": "trace_w5_20",
        "expected_status": "refused",
        "expected_policy_id": "NONE",
        "expected_section": "NONE",
        "required_terms": ["don't have enough information", "not have sufficient information"]
    },

    # Mode 5: incomplete_citation_resolution
    {
        "case_id": "CASE-21",
        "question": "What is the chronic health support entitlement for specialist medical consultations in the UK under HR-209?",
        "expected_behavior": "Must state up to 5 paid discretionary working days per calendar year under Section 2.2.",
        "taxonomy_mode": "incomplete_citation_resolution",
        "source_trace_id": "trace_w5_21",
        "expected_status": "answered",
        "expected_policy_id": "HR-209",
        "expected_section": "2.2",
        "required_terms": ["5 paid discretionary", "calendar year"],
        "region": "UK"
    },
    {
        "case_id": "CASE-22",
        "question": "What is the general carry-over expiration deadline for confirmed EMEA staff under HR-207?",
        "expected_behavior": "Must state June 30th expiration deadline for max 5 carry-over days under Section 3.1 / 3.2.",
        "taxonomy_mode": "incomplete_citation_resolution",
        "source_trace_id": "trace_w5_22",
        "expected_status": "answered",
        "expected_policy_id": "HR-207",
        "expected_section": "3.1",
        "required_terms": ["June 30th", "5 days"],
        "region": "EMEA"
    },
    {
        "case_id": "CASE-23",
        "question": "What is the standard carry-over forfeiture date for confirmed employees in APAC under HR-207 Section 3.1?",
        "expected_behavior": "Must state March 31st automatic forfeiture date for carry-over exceeding 10 days.",
        "taxonomy_mode": "incomplete_citation_resolution",
        "source_trace_id": "trace_w5_23",
        "expected_status": "answered",
        "expected_policy_id": "HR-207",
        "expected_section": "3.1",
        "required_terms": ["March 31st", "10 unused"],
        "region": "APAC"
    },
    {
        "case_id": "CASE-24",
        "question": "In North America under HR-208 Section 2.1, what is the paid leave duration for a Standard tenure employee (12-36 months)?",
        "expected_behavior": "Must state 14 weeks full pay with 6 weeks unpaid extension allowed.",
        "taxonomy_mode": "incomplete_citation_resolution",
        "source_trace_id": "trace_w5_24",
        "expected_status": "answered",
        "expected_policy_id": "HR-208",
        "expected_section": "2.1",
        "required_terms": ["14 weeks", "6 weeks"],
        "region": "NA"
    },
    {
        "case_id": "CASE-25",
        "question": "What sick pay is provided during weeks 1 to 3 of illness in the UK under HR-209 Section 2.1?",
        "expected_behavior": "Must state 100% salary with self-certification under HR-209 Section 2.1.",
        "taxonomy_mode": "incomplete_citation_resolution",
        "source_trace_id": "trace_w5_25",
        "expected_status": "answered",
        "expected_policy_id": "HR-209",
        "expected_section": "2.1",
        "required_terms": ["100% salary", "Self-certification"],
        "region": "UK"
    },
    {
        "case_id": "CASE-26",
        "question": "What is the effective date of the ANZ Sick & Medical Leave Policy Addendum HR-209?",
        "expected_behavior": "Must state 2026-04-01 under HR-209 Section 1.",
        "taxonomy_mode": "incomplete_citation_resolution",
        "source_trace_id": "trace_w5_26",
        "expected_status": "answered",
        "expected_policy_id": "HR-209",
        "expected_section": "1",
        "required_terms": ["2026-04-01", "April 1"],
        "region": "ANZ"
    }
]

def get_eval_cases() -> List[Dict]:
    return EVAL_DATASET
