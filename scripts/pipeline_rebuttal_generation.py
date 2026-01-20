from scripts.llm_call import *
from scripts.prompts import *
from scripts.error_type_definition import *
from scripts.rag import *
import pymupdf4llm
import fitz


rebuttal_generation_questions = ["Generated Rebuttal: "]
deficiency = ""
error_type = "None"
rebuttal_action = "None"
generated_rebuttal = "None"
show_accept_button = False
error_type_done_once = False
rebuttal_action_done_once = False
rag_query = None
rag_context = None

def error_type_classifier(segment, paper_title, paper_content, review, user_input):
    prompt = error_type_classifier_prompt.format(DEFICIENT=DEFICIENT, ERROR_TYPES_DEFINITIONS=ERROR_TYPES_DEFINITIONS, PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content, REVIEW=review, SEGMENT=segment, USER_INPUT=user_input)
    error_type = model_calling(prompt, MODEL_NAME)
    error_type_done_once = True
    return error_type

def rebuttal_action_classifier(segment, paper_title, paper_content, review, user_input, deficiency_status, error_type):
    if error_type == "None":
        subset_rebuttal_actions = rebuttal_actions_deficient + rebuttal_actions_nondeficient
    else:
        subset_rebuttal_actions = get_possible_rebuttal_actions_from_mapping(deficiency, error_type)
    prompt = rebuttal_action_classifier_prompt.format(DEFICIENT=DEFICIENT, ERROR_TYPES=ERROR_TYPES_DEFINITIONS, REBUTTAL_ACTIONS_DEFINITIONS=REBUTTAL_ACTIONS_DEFINITIONS, PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content, REVIEW=review, SEGMENT_TO_BE_PREDICTED=segment, USER_INPUT=user_input, DEFICIENCY_STATUS=deficiency, ERROR_TYPE=error_type, SUBSET_REBUTTAL_ACTIONS=subset_rebuttal_actions)
    rebuttal_action = model_calling(prompt, MODEL_NAME)
    rebuttal_action_done_once = True
    return rebuttal_action

def deficiency_prediction(segment, paper_title, paper_content, review):
    error_type_done_once = False
    rebuttal_action_done_once = False
    deficiency = deficiency_prediction_main(segment, paper_title, paper_content, review)
    if deficiency == "yes":
        return deficiency_true_question
    else:
        return deficiency_false_question

def deficiency_prediction_main(segment_text, paper_title, paper_content, review):
    final_refinement_prompt = deficiency_prompt_zeroshot.format(DEFICIENT=DEFICIENT, ERROR_TYPES=ERROR_TYPES_DEFINITIONS, PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content, REVIEW=review, SEGMENT_TO_BE_PREDICTED=segment_text)
    deficiency = model_calling(final_refinement_prompt, MODEL_NAME).strip().lower()
    if deficiency == "yes" or deficiency == "no":
        return deficiency
    else:
        return "None"

def get_error_type_list(error_type_list_true_false):
    true_error_types = []
    error_type_list = ["incorrect_references", "less_rigor_in_reviewing_methodology_and_experiment", "misinterpretation_of_claims_and_ideas_presented_in_the_paper", "superficial_and_vague_review", "incomplete,_incorrect,_or_copied_summary", "syntactic,_structural,_or_semantic_issues_in_the_review:", "misidentification_of_syntactic_or_structural_issues_in_the_paper"]
    for i in range(0,len(error_type_list_true_false)):
        if error_type_list_true_false[i] == True:
            true_error_types.append(error_type_list[i])
    return true_error_types

def error_type_prediction(segment, paper_title, paper_content, review, deficiency_status):
    prompt = error_type_prediction_prompt.format(DEFICIENT=DEFICIENT, ERROR_TYPES_DEFINITIONS=ERROR_TYPES_DEFINITIONS, PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content, REVIEW=review, SEGMENT=segment, DEFICIENCY_STATUS=deficiency_status)
    error_type = model_calling(prompt, MODEL_NAME)
    return error_type

'''def error_type_prediction_with_pipeline(segment, paper_title, paper_content, review):
    initial_prompt = first_prompt.format(PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content, SEGMENTED_REVIEW=review, CURRENT_SEGMENT=st)
    if deficiency == "yes":
        error_type_1 = str(incorrect_references(segment, initial_prompt, model, paper_title))
        error_type_2 = str(less_rigor_review_method_experiments_zeroshot_force(segment, initial_prompt, model))
        error_type_3 = str(misinterpretation_of_claims_ideas_in_the_paper_force(segment, initial_prompt, model))
        error_type_4 = str(superficial_and_vague_review_zeroshot_force(segment, initial_prompt, model))
        error_type_5 = str(incomplete_incorrect_or_copied_summary_updated(segment, initial_prompt, model))
        error_type_6 = str(syntactic_structural_and_semantic_issue_in_the_paper(segment, initial_prompt, model))
        error_type_list_true_false = [error_type_1, error_type_2, error_type_3, error_type_4, error_type_5, error_type_6]
        true_error_types = get_error_type_list(error_type_list_true_false)
        if true_error_types == []:
            return ["none"]
        else:
            return true_error_types
    else:
        return ["none"]'''
    
def get_possible_rebuttal_actions_from_mapping(deficiency_status, error_types):
    if deficiency_status == "yes":
        subset_rebuttal_actions = []
        for error_type in error_types:
            if error_type.lower().strip() in mapping_error_type_rebuttal_action.keys():
                subset_rebuttal_actions.append(mapping_error_type_rebuttal_action[error_type.lower().strip()])
        if subset_rebuttal_actions == []:
            return rebuttal_actions_deficient
        else:
            return subset_rebuttal_actions
    else:
        return rebuttal_actions_nondeficient
   
def rebuttal_action_prediction(segment, paper_title, paper_content, review, deficiency, error_type):
    if error_type == "None":
        subset_rebuttal_actions = rebuttal_actions_deficient + rebuttal_actions_nondeficient
    else:
        subset_rebuttal_actions = get_possible_rebuttal_actions_from_mapping(deficiency, error_type)
    final_refinement_prompt = rebuttal_action_prediction_prompt.format(DEFICIENCY_STATUS=deficiency, ERROR_TYPE=error_type, SUBSET_REBUTTAL_ACTIONS=subset_rebuttal_actions, DEFICIENT=DEFICIENT, ERROR_TYPES=ERROR_TYPES_DEFINITIONS, REBUTTAL_ACTIONS_DEFINITIONS=REBUTTAL_ACTIONS_DEFINITIONS, PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content, REVIEW=review, SEGMENT_TO_BE_PREDICTED=segment)
    rebuttal_action = model_calling(final_refinement_prompt, MODEL_NAME)
    if rebuttal_action in rebuttal_actions_deficient + rebuttal_actions_nondeficient:
        return rebuttal_action
    else:
        return "None"

def rebuttal_action_prediction_without_error_types(segment, paper_title, paper_content, review, deficiency, error_type):
    subset_rebuttal_actions = rebuttal_actions_deficient + rebuttal_actions_nondeficient
    final_refinement_prompt = rebuttal_action_prediction_prompt.format(DEFICIENCY=deficiency, ERROR_TYPE=error_type, SUBSET_REBUTTAL_ACTIONS=subset_rebuttal_actions, DEFICIENT=DEFICIENT, ERROR_TYPES=ERROR_TYPES_DEFINITIONS, REBUTTAL_ACTIONS_DEFINITIONS=REBUTTAL_ACTIONS_DEFINITIONS, PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content, SEGMENTED_REVIEW=review, SEGMENT_TO_BE_PREDICTED=segment)
    rebuttal_action = model_calling(final_refinement_prompt, MODEL_NAME)
    if rebuttal_action in subset_rebuttal_actions:
        return rebuttal_action
    else:
        return "None"

def rag_needed(deficiency, error_type, rebuttal_action):
    if deficiency == "no":
        if rebuttal_action in mapping_rag_need_non_deficient:
            return True
    elif deficiency == "yes":
        if error_type+"|"+rebuttal_action in mapping_rag_need_deficient:
            return True
    return False
    
def rebuttal_generation_task(segment, paper_title, paper_content, review, deficiency, error_type, rebuttal_action, rag_query, rag_context, used_rag):
    rag_context = "None"
    rag_query = "None"
    used_rag = False
    if rag_needed(deficiency, error_type, rebuttal_action) == False:
        final_refinement_prompt = rebuttal_generation_prompt.format(DEFICIENCY=deficiency, ERROR_TYPE=error_type, REBUTTAL_ACTION=rebuttal_action, DEFICIENT=DEFICIENT, ERROR_TYPES=ERROR_TYPES_DEFINITIONS, REBUTTAL_ACTIONS_DEFINITIONS=REBUTTAL_ACTIONS_DEFINITIONS, PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content, SEGMENTED_REVIEW=review, SEGMENT_TO_BE_PREDICTED=segment)
        generated_rebuttal = model_calling(final_refinement_prompt, MODEL_NAME)
        rag_context = "Additional evidence was not needed"
        return generated_rebuttal, rag_query, rag_context, used_rag
    else:
        generated_rebuttal, rag_query, rag_context, used_rag = rebuttal_generation_with_rag(segment, paper_title, paper_content, review, deficiency, error_type, rebuttal_action, publication_date)
        return generated_rebuttal, rag_query, rag_context, used_rag

def consolidate_rebuttal_llm(paper_title, paper_content, review_rebuttal):
    prompt = consolidate_rebuttal_prompt.format(PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content, REVIEW_REBUTTAL=review_rebuttal)
    generated_rebuttal = model_calling(prompt, MODEL_NAME)
    return generated_rebuttal

def rebuttal_generation_with_rag(segment, paper_title, paper_content, review, deficiency, error_type, rebuttal_action, publication_date):
    rag_context = None
    rag_query = None
    used_rag = True
    # Decide whether RAG is needed
    rag_query, rag_context = retrieve_relevant_literature(
                review_segment=segment,
                review=review,
                paper_title=paper_title,
                paper_content=paper_content,
                publication_date=publication_date
            )
    prompt = rebuttal_generator_segment_wise_rag_pipeline(DEFICIENCY=deficiency, ERROR_TYPE=error_type, REBUTTAL_ACTION=rebuttal_action, DEFICIENT=DEFICIENT, ERROR_TYPES=ERROR_TYPES_DEFINITIONS, REBUTTAL_ACTIONS_DEFINITIONS=REBUTTAL_ACTIONS_DEFINITIONS, PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content, SEGMENTED_REVIEW=review, SEGMENT_TO_BE_PREDICTED=segment, RELEVANT_LITERATURE_CONTENT=rag_context)
    generated_rebuttal = model_calling(prompt, MODEL_NAME)

    return generated_rebuttal, rag_query, rag_context, used_rag
    '''return {
        "rebuttal": rebuttal_text,
        "rag_query": rag_query,
        "rag_context": rag_context,
    }'''


