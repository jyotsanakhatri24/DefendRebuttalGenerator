from datetime import date
import datetime
from scripts.llm_call import *

def fetch_title_segment(segment_text, q2_paper_title_mentioned, first_prompt, model):
    prompt = first_prompt + "\n" + "Current review segment" + segment_text + "\n" + q2_paper_title_mentioned
    return model_calling(prompt, MODEL_NAME)

def make_prompt_with_fewshot(first_prompt, fewshot_prompt, question, review_segment_text, model):
    exp_prompt =  fewshot_prompt + first_prompt + "\n Current review segment" + review_segment_text + "\n" + question
    a2_exp_temp = model_calling(exp_prompt, model).lower()
    final_answer_prompt = [{"role": "user", "content": exp_prompt}]
    final_answer_prompt.append({"role": "assistant", "content": a2_exp_temp})
    exp_to_answer = "Based on above explanation specify the answer in [Yes/No] only:"
    final_answer_prompt.append({"role":"user", "content": exp_to_answer})
    final_answer = model_calling(exp_prompt, model).lower()
    return final_answer

def fetch_submission_date_openreview(paper_title):
    '''client = openreview.api.OpenReviewClient(
        baseurl='https://api2.openreview.net',
        username=<your username>,
        password=<your password>
    )'''
    #submission_date = date.today()
    submission_date = datetime.datetime(2020, 1, 1)
    return submission_date

def incorrect_references(review_segment_text, first_prompt, model, PAPER_TITLE):
    q1 = "Does the review segment mentions additional references? Your response should only contain [yes/no] and nothing else."
    q1_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
    a1 = model_calling(q1_prompt, model).lower().strip()
    
    if a1 == "yes":
        q2 = "Is the reference published?"
        q2_paper_title_mentioned = "Fetch paper title mentioned. Your answer should only contain the paper title mentioned and nothing else"
        q2_title = fetch_title_segment(review_segment_text, q2_paper_title_mentioned, first_prompt, model)
        a2 = is_paper_published(q2_title)
        
        if a2 == "yes":
            q3 = "When was the reference published?"
            public_date = publication_date(q2_paper_title_mentioned)
            #current paper for which the review is being done's publication date if it has already been published
            submission_date = fetch_submission_date_openreview(q2_paper_title_mentioned)
            if public_date > submission_date:
                return 0
            else:
                return 10
        else:
            return 0
    else:
        return 0

def less_rigor_review_method_experiments_zeroshot(review_segment_text, first_prompt, model):
    q1 = "Does the review statement suggests additional methods, experiments or analysis? Your response should only contain [yes/no] and nothing else."
    q1_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
    a1 = model_calling(q1_prompt, model).lower()
    if a1 == "yes":
        # out of scope
        q2 = "Are experiments suggested beyond the scope of the paper? Your response should only contain [yes/no] and nothing else."
        q2_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q2
        a2 = model_calling(q2_prompt, model).lower()
        if a2 == "yes":
            return 10
        else:
            #invalid criticism or experiment
            q3 = "Does experiments suggested add any value to the paper? Your response should only contain [yes/no] and nothing else."
            q3_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q3
            a3 = model_calling(q3_prompt, model).lower()
            if a3 == "yes":
                return 0
            else:
                return 10
    else:
        0

def less_rigor_review_method_experiments_zeroshot_force(review_segment_text, first_prompt, model):
    q1 = "Does the review statement suggests additional methods, experiments or analysis? Your response should only contain [yes/no] and nothing else."
    q1_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
    a1 = model_calling(q1_prompt, model).lower()
    if a1 == "yes":
        # out of scope
        q2 = "Are experiments suggested beyond the scope of the paper? Your response should only contain [yes/no] and nothing else."
        q2_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q2
        a2 = model_calling(q2_prompt, model).lower()
        if a2 == "yes":
            return 10
        else:
            #invalid criticism or experiment
            q3 = "Does experiments suggested add any value to the paper? Your response should only contain [yes/no] and nothing else."
            q3_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q3
            a3 = model_calling(q3_prompt, model).lower()
            if a3 == "yes":
                q4 = "How much value suggested experiments add to the paper? Your answer should contain a number between 0 and 10 and nothing else."
                q4_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q4
                a4 = model_calling(q4_prompt, model).lower()
                if a4.isdigit():
                    return 10-(float)(a4)
                else:
                    0
            else:
                return 10
    else:
        0

def less_rigor_review_method_experiments_cot_fewshot(review_segment_text, first_prompt, model):
    q1 = "Does the review statement suggests additional methods, experiments or analysis? Your response should only contain [yes/no] and nothing else."
    q1_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
    a1 = model_calling(q1_prompt, model).lower()
    if a1 == "yes":
        #cot fewshots
        fewshot_prompt = "Here are a few examples with reasoning:\n" + cot_e2_q2_1
        a2 = make_prompt_with_fewshot(first_prompt, fewshot_prompt, e2_q2_1, review_segment_text, model)
        
        if a2.lower() == "yes":
            return 10
        else:
            fewshot_prompt = "Here are a few examples with reasoning:\n" + cot_e2_q2_2
            a3 = make_prompt_with_fewshot(first_prompt, fewshot_prompt, e2_q2_2, review_segment_text, model)
            if a3 == "yes":
                return 0
            else:
                return 10
    else:
        return 0

def misinterpretation_of_claims_ideas_in_the_paper(review_segment_text, first_prompt, model):
    #inexpert statement
    qmain = "In the current review segment, does it indicate lack of domain knowledge of the reviewer?"
    qmain_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + qmain
    amain = model_calling(qmain_prompt, model).lower()
    if amain == "yes":
        return 10
    else:    
        q1 = "In the current review segment, does the reviewer indicates that he/she is not satisfied with the claims made in the paper? Your response should only contain [yes/no] and nothing else."
        q1_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
        a1 = model_calling(q1_prompt, model).lower()
        if a1 == "yes":
            q2 = "In the current review segment, is the interpretation of claims or ideas in the paper by the reviewer does not match with the actual ideas or claims in the paper?  Your response should only contain [yes/no] and nothing else."
            q2_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q2
            a2 = model_calling(q2_prompt, model).lower()
            if a2 == "yes":
                return 10
            else:
                q3 = "Does the review segment contradicts or comment on something which indicates that the reviewer has missed the contents of the paper? Your response should only contain [yes/no] and nothing else."
                q3_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q3
                a3 = model_calling(q2_prompt, model).lower()
                if a3 == "yes":
                    return 10
                else:
                    False
        else:
            False

def misinterpretation_of_claims_ideas_in_the_paper_force(review_segment_text, first_prompt, model):
    #inexpert statement
    qmain = "In the current review segment, does it indicate lack of domain knowledge of the reviewer?"
    qmain_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + qmain
    amain = model_calling(qmain_prompt, model).lower()
    if amain == "yes":
        return 10
    else:    
        q1 = "In the current review segment, does the reviewer indicates that he/she is not satisfied with the claims made in the paper? Your response should only contain [yes/no] and nothing else."
        q1_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
        a1 = model_calling(q1_prompt, model).lower()
        if a1 == "yes":
            q2 = "In the current review segment, is the interpretation of claims or ideas in the paper by the reviewer does not match with the actual ideas or claims in the paper?  Your response should only contain [yes/no] and nothing else."
            q2_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q2
            a2 = model_calling(q2_prompt, model).lower()
            if a2 == "yes":
                return 10
            else:
                #q3 = "Does the review statement contradicts or comment on something which indicates that the reviewer has missed the contents of the paper? Your response should only contain [yes/no] and nothing else."
                q3 = "How much does the interpretation of claims or ideas in the review are matching the paper?  Your answer should contain a number between 0 and 100 and nothing else."
                q3_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q3
                a3 = model_calling(q2_prompt, model).lower()
                '''if a3 == "yes":
                    return 10
                else:
                    q4 = "How much does the interpretation of claims or ideas in the review are matching the paper?  Your answer should contain a number between 0 and 100 and nothing else."
                    q4_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q4
                    a4 = model_calling(q4_prompt, model).lower()
                    if a4.isdigit():
                        return 10-(float)(a4)
                    else:
                        0'''
                if a3.isdigit() and  0<(int)(a3)<=10:
                    return a3
                else:
                    return 0
        else:
            return 0

def superficial_and_vague_review_zeroshot(review_segment_text, first_prompt, model):
    q11 = "Is the current review segment very generic and not referring to any specific thing from the paper? Your response should only contain [yes/no] and nothing else."
    q11_prompt = first_prompt + "\n Current review segment" + review_segment_text + "\n" + q11
    a11 = model_calling(q11_prompt, model).lower()
    if a11.lower() == "yes":
        return 10      
        
    q12 = "In the current review segment, is the reviewer questioning the novelty of the paper without providing appropriate references?​ Your response should only contain [yes/no] and nothing else."
    q12_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q12
    a12 = model_calling(q12_prompt, model).lower()
    
    if a12.lower() == "yes":
        return 10

    q1 = "Does the current review segment need some justification to make sense? Your response should only contain [yes/no] and nothing else."
    q1_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
    a1 = model_calling(q1_prompt, model).lower()
    
    if a1 == "yes":
        q2 = "To understand the review comments, is referencing from other parts of the paper required? Your response should only contain [yes/no] and nothing else."
        q2_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q2
        a2 = model_calling(q2_prompt, model).lower()
        if a2 == "yes":
            q3 = "Is the review statement making vague statements without referring to appropriate parts of the paper? Your response should only contain [yes/no] and nothing else."
            q3_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q3
            a3 = model_calling(q3_prompt, model).lower()
            if a3 == "yes":
                return 10
            else:
                return 0
        else:
            q4 = "To understand the review comments, is referencing from the external papers/sources required? Your response should only contain [yes/no] and nothing else."
            q4_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q4
            a4 = model_calling(q4_prompt, model).lower()
            if a4 == "yes":
                q5 = "Is the review statement making vague statements without referring to appropriate external sources? Your response should only contain [yes/no] and nothing else."
                q5_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q5
                a5 = model_calling(q5_prompt, model).lower()
                if a5 == "yes":
                    return 10
                else:
                    return 0
    else:
        False

def superficial_and_vague_review_zeroshot_force(review_segment_text, first_prompt, model):
    q11 = "Is the current review segment very generic and not referring to any specific thing from the paper? Your response should only contain [yes/no] and nothing else."
    q11_prompt = first_prompt + "\n Current review segment" + review_segment_text + "\n" + q11
    a11 = model_calling(q11_prompt, model).lower()
    if a11.lower() == "yes":
        return 10      
        
    q12 = "In the current review segment, is the reviewer questioning the novelty of the paper without providing appropriate references?​ Your response should only contain [yes/no] and nothing else."
    q12_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q12
    a12 = model_calling(q12_prompt, model).lower()
    
    if a12.lower() == "yes":
        return 10

    q1 = "Does the current review segment need some justification to make sense? Your response should only contain [yes/no] and nothing else."
    q1_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
    a1 = model_calling(q1_prompt, model).lower()
    
    if a1 == "yes":
        q2 = "To understand the review segment, is referencing from other parts of the paper required? Your response should only contain [yes/no] and nothing else."
        q2_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q2
        a2 = model_calling(q2_prompt, model).lower()
        if a2 == "yes":
            #q3 = "Does the review segment making vague statements without referring to appropriate parts of the paper? Your response should only contain [yes/no] and nothing else."
            q3 = "Does the review segment making vague statements without referring to appropriate parts of the paper? Score between 0-10 indicating the intensity with which the review segment is making vague statement about the paper without refering to appropriate parts of the paper. You answer should contain a number between 0-10 and nothing else."
            q3_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q3
            a3 = model_calling(q3_prompt, model).lower()
            '''if a3 == "yes":
                return 10
            else:
                return 0'''
            if a3.isdigit() and  0<(int)(a3)<=10:
                return a3
            else:
                return 0
        else:
            q4 = "To understand the review segment, is referencing from the external papers/sources required? Your response should only contain [yes/no] and nothing else."
            q4_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q4
            a4 = model_calling(q4_prompt, model).lower()
            if a4 == "yes":
                #q5 = "Does the review segment making vague statements without referring to appropriate external sources? Your response should only contain [yes/no] and nothing else."
                q5 = "Does the review segment making vague statements without referring to appropriate external sources? Score between 0-10 indicating the intensity with which the review segment is making vague statement about the paper without refering to appropriate external references. You answer should contain a number between 0-10 and nothing else."
                q5_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q5
                a5 = model_calling(q5_prompt, model).lower()
                '''if a5 == "yes":
                    return 10
                else:
                    return 0'''
                if a5.isdigit() and 0<(int)(a5)<=10:
                    return a5
                else:
                    return 0
            else:
                return 0
    else:
        0

def superficial_and_vague_review_fewshot(review_segment_text, first_prompt, model):
    #Superficial Review 2
    q11 = "Lets think step by step to understand if the review statement is very generic and not refering to any specific thing from the paper (have unsupported comments)?"
    fewshot_prompt = "Here are a few examples with reasoning:\n" + cot_e4_s2
    a11 = make_prompt_with_fewshot(first_prompt, fewshot_prompt, e4_s2, review_segment_text, model)
    if a11.lower() == "yes":
        return 10
                
    #Misinterpret Novelty 4    
    q12 = "Lets think step by step to understand if the reviewer is questioning the novelty of the paper without providing appropriate references?​"
    q12_prompt = first_prompt + "\n" + fewshot_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q12
    a12 = model_calling(q12_prompt, model).lower()
    
    if a12.lower() == "yes":
        return 10

    #1.3.5.
    q1 = "Does the review statement need some justification to make sense? Your response should only contain [yes/no] and nothing else."
    q1_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
    a1 = model_calling(q1_prompt, model).lower()
    
    if a1 == "yes":
        return 0
    else:
        q2 = "To understand the review comments, is referencing from other parts of the paper required? Your response should only contain [yes/no] and nothing else."
        q2_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q2
        a2 = model_calling(q2_prompt, model).lower()
        if a2 == "yes":
            q3 = "Is the review statement making vague statements without referring to appropriate parts of the paper? Your response should only contain [yes/no] and nothing else."
            q3_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q3
            a3 = model_calling(q3_prompt, model).lower()
            if a3 == "yes":
                return 10
            else:
                return 0
        else:
            q4 = "To understand the review comments, is referencing from the external papers/sources required? Your response should only contain [yes/no] and nothing else."
            q4_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q4
            a4 = model_calling(q4_prompt, model).lower()
            if a4 == "yes":
                q5 = "Is the review statement making vague statements without referring to appropriate external sources? Your response should only contain [yes/no] and nothing else."
                q5_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q5
                a5 = model_calling(q5_prompt, model).lower()
                if a5 == "yes":
                    return 10
                else:
                    return 0

def incomplete_incorrect_or_copied_summary(review_segment_text, first_prompt, model):
    q1 = "Is the review statement talking about the summary of the paper? Your response should only contain [yes/no] and nothing else."
    q1_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
    a1 = model_calling(q1_prompt, model).lower()
    if a1 == "yes":
        q2 = "Does the summary (include other segments which are part of the summary as well provided in the segmented review) cover the paper properly and correctly? Your response should only contain [yes/no] and nothing else."
        q2_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
        a2 = model_calling(q2_prompt, model).lower()
        if a2 == "yes":
            return 10
        else:
            return 0
    else:
        return 0

def incomplete_incorrect_or_copied_summary_updated(review_segment_text, first_prompt, model):
    q1 = "Is the review segment talking about the summary of the paper? Your response should only contain [yes/no] and nothing else."
    q1_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
    a1 = model_calling(q1_prompt, model).lower()
    if a1 == "yes":
        q2 = "Does the review segment inclusive of other segments which are part of the summary cover the paper properly and correctly? Do not consider this particular segment only, consider other segments which are part of the Summary from the specified segmented review. Your response should only contain [yes/no] and nothing else."
        q2_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
        a2 = model_calling(q2_prompt, model).lower()
        if a2 == "yes":
            return 10
        else:
            return 0
    else:
        return 0

def syntactic_structural_and_semantic_issue_in_the_paper(review_segment_text, first_prompt, model):
    q1 = "Does the review statement has typographical errors which makes it difficult to understand? Your response should only contain [yes/no] and nothing else."
    q1_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
    a1 = model_calling(q1_prompt, model).lower()
    if a1 == "yes":
        return 10
    else:
        q2 = "Does the review statement contradicts or duplicates with any other review statement? Your response should only contain [yes/no] and nothing else."
        q2_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
        a2 = model_calling(q2_prompt, model).lower()
        if a2 == "yes":
            return 10
        else:
            #q3 = "Is the review statement placed in the correct attribute section? Consider nearby segments to get information about the attribute section. Your response should only contain [yes/no] and nothing else."
            q3 = "Is the review statement placed in the correct attribute section? Consider nearby segments to get information about the attribute section. Score between 0-10 indicating the intensity with which the review segment is placed in a wrong attribute section. You answer should contain a number between 0-10 and nothing else."
            q3_prompt = first_prompt + "\n" + "Current review segment" + review_segment_text + "\n" + q1
            a3 = model_calling(q2_prompt, model).lower()
            '''if a3 == "yes":
                return 0
            else:
                return 10'''
            if a3.isdigit() and  0<(int)(a3)<=10:
                return a3
            else:
                return 0
