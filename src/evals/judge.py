import json
import re
from typing import Dict
from src.config import get_gemini_client, JUDGE_MODEL

JUDGE_V1_PROMPT_TEMPLATE = """You are an expert HR Policy Evaluation Judge.
Evaluate whether the generated response accurately and faithfully fulfills the expected policy behavior.

IMPORTANT INSTRUCTION:
Do NOT evaluate citation syntax, chunk IDs, or structural formatting (these are checked deterministically by automated assertions).
Evaluate ONLY semantic correctness: Does the generated answer accurately provide the policy entitlement or correctly refuse when unsupported?

QUESTION:
{question}

EXPECTED POLICY BEHAVIOR:
{expected_behavior}

GENERATED ANSWER:
{generated_answer}

Respond strictly in JSON format:
{{
  "judgment": 1, // 1 for PASS (semantically correct & faithful), 0 for FAIL (incorrect/misleading)
  "reasoning": "<1-2 sentences explaining judgment>"
}}
"""

JUDGE_V2_PROMPT_TEMPLATE = """You are an expert HR Policy Evaluation Judge.
Evaluate whether the generated response accurately and faithfully fulfills the expected policy behavior.

IMPORTANT INSTRUCTION:
Do NOT evaluate citation syntax, chunk IDs, or structural formatting (these are checked deterministically by automated assertions).
Evaluate ONLY semantic correctness: Does the generated answer accurately provide the policy entitlement or correctly refuse when unsupported?

FEW-SHOT EXAMPLES OF TRICKY EVALUATION CASES:
Example 1:
Question: "Under HR-999 section 1.0, what is the executive equity vesting schedule upon acquisition?"
Expected Behavior: "Must refuse because HR-999 is not in the corpus."
Generated Answer: "I don't have enough information in the provided HR policy documents to answer that."
Judgment: 1
Reasoning: "The model correctly and strictly refused to fabricate out-of-corpus policy information."

Example 2:
Question: "What is the carry-over cap for unconfirmed probationary employees in EMEA under HR-207?"
Expected Behavior: "Must state 0 days (unconfirmed probationary employees are prohibited from rolling over leave)."
Generated Answer: "Employees in EMEA can carry over a maximum of 5 days expiring June 30th."
Judgment: 0
Reasoning: "The answer quoted the confirmed employee cap (5 days) instead of the probationary restriction (0 days/prohibited)."

NOW EVALUATE THE FOLLOWING:
QUESTION:
{question}

EXPECTED POLICY BEHAVIOR:
{expected_behavior}

GENERATED ANSWER:
{generated_answer}

Respond strictly in JSON format:
{{
  "judgment": 1, // 1 for PASS (semantically correct & faithful), 0 for FAIL (incorrect/misleading)
  "reasoning": "<1-2 sentences explaining judgment>"
}}
"""

class LLMJudge:
    def __init__(self, version: str = "v1"):
        self.version = version
        self.client = get_gemini_client()
        self.prompt_template = JUDGE_V2_PROMPT_TEMPLATE if version == "v2" else JUDGE_V1_PROMPT_TEMPLATE

    def evaluate_answer(self, question: str, expected_behavior: str, generated_answer: str) -> Dict:
        prompt = self.prompt_template.format(
            question=question,
            expected_behavior=expected_behavior,
            generated_answer=generated_answer
        )
        
        response = self.client.models.generate_content(
            model=JUDGE_MODEL,
            contents=prompt,
            config={"temperature": 0.0}
        )

        raw_text = response.text.strip()
        
        # Parse JSON
        try:
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                return {
                    "judgment": int(data.get("judgment", 0)),
                    "reasoning": data.get("reasoning", raw_text),
                    "raw_output": raw_text
                }
        except Exception:
            pass

        # Fallback
        judgment = 1 if "1" in raw_text and "0" not in raw_text[:20] else 0
        return {
            "judgment": judgment,
            "reasoning": raw_text,
            "raw_output": raw_text
        }
