from scripts.llm_call import *
from scripts.prompts import *
from scripts.pipeline_rebuttal_generation import *
import pymupdf4llm
import fitz


def extract_pdf_content(pdf_file):
    return pymupdf4llm.to_markdown( pdf_file)
    
def get_segments_from_review(review):
    prompt = segment_review.format(Review=review.strip())
    segments = model_calling(prompt, MODEL_NAME)
    final_segments = segments.strip().replace("\n","").split("|")
    return final_segments

def direct_rebuttal_generation_segment(segments, paper_title, paper_content, review):
    rebuttal = []
    for segment in segments:
        prompt = rebuttal_generator_segment_wise.format(PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content, SEGMENT=segment)
        response = model_calling(prompt, MODEL_NAME)
        rebuttal.append(response)
    return rebuttal

def what_question_is_asked(chat_history):
    current_length_chat_history = len(chat_history)
    k = current_length_chat_history
    while k > 0:
        if chat_history[k-2]["assistant"] in deficiency_questions:
            return "deficiency"
        elif chat_history[k-2]["assistant"] in error_type_questions:
            return "error_type"
        elif chat_history[k-2]["assistant"] in rebuttal_action_questions:
            return "rebuttal_action"
        elif chat_history[k-2]["assistant"] in rebuttal_generation_questions:
            return "rebuttal_action"
        k = k-2
    if k == 0:
        return "Not valid"

#Returns based on whether the statement is deficient or not after user feedback
def check_deficient(deficiency_question, answer):
    if deficiency_question == deficiency_false_question and answer == "no":
        return "yes"
    elif deficiency_question == deficiency_false_question and answer == "yes":
        return "no"
    elif deficiency_question == deficiency_true_question and answer == "no":
        return "no"
    elif deficiency_question == deficiency_true_question and answer == "yes":
        return "yes"
    else:
        return "None"         

def append_to_chat_history(chat_history, response, user_input):
    #Append the user reply
    chat_history.append({"role": "user", "content": user_input})
    #Append the assistant for next question
    chat_history.append({"role": "assistant", "content": response})
    return chat_history

def pipeline(segment, rebuttal, paper_title, paper_content, review, chat_history, user_input, deficiency, error_type, rebuttal_action, generated_rebuttal, error_type_done_once, rebuttal_action_done_once, rag_query, rag_context, used_rag):
    current_length_chat_history = len(chat_history)
    response = ""
    #Stage1: Ask about deficiency (first assistant turn)
    if current_length_chat_history == 0:
        deficiency = deficiency_prediction_main(segment, paper_title, paper_content, review)
        if deficiency == "yes":
            response = deficiency_true_question
        else:
            response = deficiency_false_question
        #Append the assistant
        chat_history.append({"role": "assistant", "content": response})
    
    # Stage 2: User answered deficiency question
    elif current_length_chat_history == 1:
        user_answer = user_input.strip().lower()
        if user_answer in ["yes", "no"]:
            is_deficient = check_deficient(chat_history[current_length_chat_history-1]["content"], user_input.lower())
            #if deficient
            if is_deficient == "yes":
                error_type = error_type_prediction(segment, paper_title, paper_content, review, deficiency)
                if error_type.strip() in mapping_error_type_statement:
                    response = mapping_error_type_statement[error_type.strip()]
                else:
                    response = could_not_predict_error_type_statement
                chat_history = append_to_chat_history(chat_history, response, user_input)
            #Non-deficient
            else:
                chat_history.append({"role": "user", "content": "no"})
                chat_history.append({"role": "assistant", "content": "None"})
                #Append the assistant for next question
                rebuttal_action = rebuttal_action_prediction(segment, paper_title, paper_content, review, deficiency, error_type)
                if rebuttal_action.strip() in mapping_rebuttal_action_statement:
                    response = mapping_rebuttal_action_statement[rebuttal_action.strip()]
                else:
                    response = could_not_predict_rebuttal_action_statement
                #chat_history.append({"role": "assistant", "content": response})
                chat_history = append_to_chat_history(chat_history, response, user_input)
        else:
            response = "Please reply in yes/no only."
    
    # STAGE 3: User feedback on error type → move to rebuttal action
    elif current_length_chat_history == 3:
        user_answer = user_input.strip().lower()
        if user_answer in ["yes", "no"]:
            #User accepted the predicted error type
            if user_input.lower() == "yes":
                rebuttal_action = rebuttal_action_prediction(segment, paper_title, paper_content, review, deficiency, error_type)
                rebuttal_action = "_".join(rebuttal_action.strip().lower().split(" "))
                if rebuttal_action in mapping_rebuttal_action_statement:
                    response = mapping_rebuttal_action_statement[rebuttal_action]
                else:
                    response = could_not_predict_rebuttal_action_statement
                chat_history = append_to_chat_history(chat_history, response, user_input)
            # User rejected predicted error type (first time)
            elif user_input.lower() == "no" and error_type_done_once == False: 
                response = could_not_predict_error_type_statement
                chat_history = append_to_chat_history(chat_history, response, user_input)
            # User rejected again → skip error type
            else:
                #Remove the asking of the could not predict errortype and add error type as None
                chat_history = chat_history[0:len(chat_history)-1]
                chat_history.append({"role": "assistant", "content": "None"})
                rebuttal_action = rebuttal_action_prediction(segment, paper_title, paper_content, review, deficiency, error_type)
                if rebuttal_action.strip() in mapping_rebuttal_action_statement:
                    response = mapping_rebuttal_action_statement[rebuttal_action.strip()] 
                else:
                    response = could_not_predict_rebuttal_action_statement
                
                chat_history = append_to_chat_history(chat_history, response, user_input)
        # ---- Free-text feedback branch for error type ----
        elif chat_history[len(chat_history)-1]["content"] == could_not_predict_error_type_statement:
            if error_type_done_once == False:
                error_type = error_type_classifier(segment, paper_title, paper_content, review, user_input)
                if error_type in mapping_error_type_statement:
                    response = mapping_error_type_statement[error_type]
                    chat_history = chat_history[0:len(chat_history)-2]
                    chat_history = append_to_chat_history(chat_history, response, user_input)
                    error_type_done_once = True
                else:
                    #Remove the asking of the could not predict errortype and add error type as None
                    chat_history = chat_history[0:len(chat_history)-1]
                    chat_history.append({"role": "assistant", "content": "None"})
                    rebuttal_action = rebuttal_action_prediction(segment, paper_title, paper_content, review, deficiency, error_type)
                    if rebuttal_action.strip() in mapping_rebuttal_action_statement:
                        response = mapping_rebuttal_action_statement[rebuttal_action.strip()] 
                    else:
                        response = could_not_predict_rebuttal_action_statement
                    
                    chat_history = append_to_chat_history(chat_history, response, user_input)
            #This wont happen
            else:
                # Fallback: skip error type and move on
                chat_history = chat_history[0:len(chat_history)-1]
                chat_history.append({"role": "assistant", "content": "None"})
                rebuttal_action = rebuttal_action_prediction(segment, paper_title, paper_content, review, deficiency, error_type)
                if rebuttal_action.strip() in mapping_rebuttal_action_statement:
                    response = mapping_rebuttal_action_statement[rebuttal_action.strip()] 
                else:
                    response = could_not_predict_rebuttal_action_statement
                #chat_history = chat_history[0:len(chat_history)-2]
                chat_history = append_to_chat_history(chat_history, response, user_input)
        else:
            response = "Please reply in yes/no only."
    #the reply for rebuttal action and generated rebuttal
    # Stage 4: User feedback on rebuttal action → generate rebuttal
    elif current_length_chat_history == 5:
        user_answer = user_input.strip().lower()
        if user_answer in ["yes", "no"]:
            if user_input.lower() == "yes":
                generated_rebuttal, rag_query, rag_context, used_rag = rebuttal_generation_task(segment, paper_title, paper_content, review, deficiency, error_type, rebuttal_action, rag_query, rag_context, used_rag)
                response = generated_rebuttal + "\nDo you agree with the generated rebuttal?"
                chat_history = append_to_chat_history(chat_history, response, user_input)
            elif user_input.lower() == "no" and rebuttal_action_done_once == False:
                #generated_rebuttal, rag_query, rag_context, used_rag = rebuttal_generation_task(segment, paper_title, paper_content, review, deficiency, error_type, rebuttal_action, rag_query, rag_context, used_rag)
                response = could_not_predict_rebuttal_action_statement #generated_rebuttal + "\nDo you agree with the generated rebuttal?"
                chat_history = chat_history[0:len(chat_history)-2]
                chat_history = append_to_chat_history(chat_history, response, user_input)
            else:
                generated_rebuttal, rag_query, rag_context, used_rag = rebuttal_generation_task(segment, paper_title, paper_content, review, deficiency, error_type, rebuttal_action, rag_query, rag_context, used_rag )
                response = generated_rebuttal + "\nDo you agree with the generated rebuttal?"
                chat_history = append_to_chat_history(chat_history, response, user_input)
        elif chat_history[len(chat_history)-1]["content"] == could_not_predict_rebuttal_action_statement:
            if rebuttal_action_done_once == False:
                rebuttal_action = rebuttal_action_classifier(segment, paper_title, paper_content, review, user_input, deficiency, error_type)
                if rebuttal_action.strip() in mapping_rebuttal_action_statement:
                    response = mapping_rebuttal_action_statement[rebuttal_action.strip()]
                    chat_history = chat_history[0:len(chat_history)-2]
                    chat_history = append_to_chat_history(chat_history, response, user_input)
                    rebuttal_action_done_once = True
                else:
                    generated_rebuttal, rag_query, rag_context, used_rag = rebuttal_generation_task(segment, paper_title, paper_content, review, deficiency, error_type, rebuttal_action, )
                    response = generated_rebuttal + "\nDo you agree with the generated rebuttal?"
                    chat_history = append_to_chat_history(chat_history, response, user_input)
            else:
                generated_rebuttal, rag_query, rag_context, used_rag = rebuttal_generation_task(segment, paper_title, paper_content, review, deficiency, error_type, rebuttal_action, )
                response = generated_rebuttal + "\nDo you agree with the generated rebuttal?"
                chat_history = append_to_chat_history(chat_history, response, user_input)
        else:
            response = "Please reply in yes/no only."
    #the reply for generated rebuttal and question for editing the rebuttal
    elif current_length_chat_history == 7:
        if user_input.lower() == "yes" or user_input.lower() == "no":
            if user_input.lower() == "yes":
                response = "Final rebuttal:\n" + generated_rebuttal
                chat_history = append_to_chat_history(chat_history, response, user_input)
            else:
                response = could_not_generate_rebuttal_question
                chat_history = append_to_chat_history(chat_history, response, user_input)
        else:
            response = "Please reply in yes/no only."
    elif current_length_chat_history == 9:
        chat_history = chat_history[0:len(chat_history)-2]
        chat_history = append_to_chat_history(chat_history, response, user_input)
        response = "Final rebuttal:\n" + user_input
    else:
        response = "Please reply in yes/no only."
    return response, rag_query, rag_context, used_rag, chat_history, paper_title, paper_content, segment, deficiency, error_type, rebuttal_action, generated_rebuttal, error_type_done_once, rebuttal_action_done_once 

