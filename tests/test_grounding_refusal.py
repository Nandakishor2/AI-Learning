import pytest
from src.generation.rag_pipeline import RAGPipeline, REFUSAL_STRING
from src.generation.citation_validator import CitationValidator
from src.config import STRUCTURE_COLLECTION

def test_grounded_answer_and_citation_validation():
    pipeline = RAGPipeline(collection_name=STRUCTURE_COLLECTION, use_hybrid=True)
    res = pipeline.generate_answer(
        "What is the carry-over cap for Tier 1 staff in APAC under HR-207?",
        region="APAC"
    )
    assert res.status == "answered"
    assert len(res.citations) > 0
    
    validator = CitationValidator(collection_name=STRUCTURE_COLLECTION)
    val_res = validator.validate_citations(res.citations, res.answer)
    assert val_res.is_valid is True
    assert val_res.invalid_citations == 0

def test_out_of_corpus_refusal():
    pipeline = RAGPipeline(collection_name=STRUCTURE_COLLECTION, use_hybrid=True)
    res = pipeline.generate_answer("What is the company sabbatical policy for engineers with 10 years of service?")
    assert res.status == "refused"
    assert REFUSAL_STRING in res.answer
    assert len(res.citations) == 0
