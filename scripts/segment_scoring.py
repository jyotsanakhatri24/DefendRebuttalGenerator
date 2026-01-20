import json
from scripts.llm_call import model_calling
from scripts.prompts import segment_scoring_prompt
import os

MODEL_NAME = os.environ.get("MODEL_NAME")

def score_review_rebuttal_segment(
    paper_title,
    paper_content,
    review_segment,
    rebuttal_segment,
    rag_context=None
):
    prompt = segment_scoring_prompt.format(
        PAPER_TITLE=paper_title,
        PAPER_CONTENT=paper_content,
        REVIEW_SEGMENT=review_segment,
        REBUTTAL_SEGMENT=rebuttal_segment,
        RAG_CONTEXT=rag_context or "None"
    )

    response = model_calling(prompt, MODEL_NAME)

    try:
        scores = response.split("|")
        factual_correctness = float(scores[0].split(":")[1].strip())
        strength_of_refutation = float(scores[1].split(":")[1].strip())
        overall_quality = float(scores[2].split(":")[1].strip())
    except Exception:
        # fallback to safe defaults
        scores = {
            "factual_correctness": 0.5,
            "strength_of_refutation": 0.5,
            "overall_quality": 0.5
        }

    return scores
