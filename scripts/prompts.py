DEFICIENT='''
1. Sentences that contain factual errors or misinterpretations of the submission.
2. Sentences lacking constructive feedback.
3. Sentences that express overly subjective, emotional, or offensive judgments, such as “I don’t like
this work because it is written like by a middle school student.”
4. Sentences that describe the downsides of the submission without supporting evidence, for example, “This work misses some related work.”
'''

ERROR_TYPES_DEFINITIONS='''
1. incorrect_references: The reviewer cites non peer-reviewed sources of blogs which is not appropriate for academic validation. The reviewer requests comparisons with work conducted concurrently, which may not have been considered by the authors.
2. less_rigor_in_reviewing_methodology_and_experiment: The reviewer suggests additional methods, design of experiments, experimental results, or analyses that are beyond the scope of the paper or impractical or trivial.
3. misinterpretation_of_claims_and_ideas_presented_in_the_paper: The reviewer misinterprets claims or ideas presented in the paper or overlools some of the details or misunderstand certain concepts because of lack of domain knowledge.
4. superficial_and_vague_review: The reviewer questions different parts of the paper without substantiating their claims with relevant citations or a proper explanation for the same. The reviewer lacks specificity when presenting certain limitations of the paper. The comments are very generic.
5. incomplete,_incorrect,_or_copied_summary: The reviewer is summarizing the paper superficially.
6. syntactic,_structural,_or_semantic_issues_in_the_review: The review contains typographical errors that may affect clarity or understanding. The review has certain contradictions in itself. The review is stating the same information again and again.
7. misidentification_of_syntactic_or_structural_issues_in_the_paper: The reviewer has misidentified some of the syntactic and structural issues in the paper.
'''

REBUTTAL_ACTIONS_DEFINITIONS='''
reject_request: Reject a request from a reviewer
accept_for_future_work: Express approval for a suggestion, but for future work
reject_criticism: Reject the validity of a negative eval. statement
refute_question: Reject the validity of a question
contradict_assertion: Contradict a statement presented as a fact
mitigate_criticism: Mitigate the importance of a negative eval. statement
answer_question: Answer a question
the_task_is_done: Claim that a requested task has been completed
the_task_will_be_done: Promise a change by camera ready deadline
concede_criticism: Concede the validity of a negative eval. statement
mitigate_criticism: Mitigate the importance of a negative eval. statement
accept_praise: Thank reviewer for positive statements
no_rebuttal: No response needs to be given to reviewer
'''

deficiency_prompt_zeroshot='''
Given a paper submission and its corresponding review, your job is to assess the deficiency of a given segment.
You need to assess if each segment/sentence of the review is "deficient" or not.

The criteria for deficiency are:
{DEFICIENT}

Deficient segments can have following error types (All possible error types with definitions are given below):
{ERROR_TYPES}

Paper title: {PAPER_TITLE}
Paper content: {PAPER_CONTENT}
Review: {REVIEW}

Segment to be predicted: {SEGMENT_TO_BE_PREDICTED}

You are supposed to predict whether the given segment is deficient or not. 
Please take care of the following while predicting for the given segment
1. You answer should only contain [Yes/No] and nothing else.
2. Please consider paper title, paper content, content of the entire review, criteria for deficiency, definition of error-types and general domain knowledge.
'''

error_type_classifier_prompt = '''
Given a paper submission, its corresponding review your job is to identify the error-type of a segment based on the input from the user.
Some important information is provided below

The criteria for deficiency are:
{DEFICIENT}

Deficient statements can have following error types (All error types with definitions are given below):
{ERROR_TYPES_DEFINITIONS}

Paper title: {PAPER_TITLE}
Paper content: {PAPER_CONTENT}
Review: {REVIEW}

Current segment: {SEGMENT}
User feedback about which error type is applicable: {USER_INPUT}
Deficiency status: yes
Strictly select from the list of error-types and show error-type only and nothing else.
If there is no valid error type or the review segment is not deficient return None and nothing else'''

error_type_prediction_prompt = '''
Given a paper submission, its corresponding review your job is to identify the error-type of a segment.
Some important information is provided below

The criteria for deficiency are:
{DEFICIENT}

Deficient statements can have following error types (All error types with definitions are given below):
{ERROR_TYPES_DEFINITIONS}

Paper title: {PAPER_TITLE}
Paper content: {PAPER_CONTENT}
Review: {REVIEW}

Current segment: {SEGMENT}
Deficiency status: {DEFICIENCY_STATUS}
Strictly select from the list of error-types and show error-type only and nothing else.
If there is no valid error type or the review segment is not deficient return None and nothing else'''

rebuttal_actions_deficient = ["reject_request", "accept_for_future_work", "reject_criticism", "refute_question", "contradict_assertion", "mitigate_criticism",]
rebuttal_actions_nondeficient = ["answer_question", "the_task_is_done", "the_task_will_be_done", "concede_criticism", "mitigate_criticism", "accept_praise", "no_rebuttal"]

mapping_error_type_rebuttal_action = {
    "incorrect_references": ["reject_request"], 
    "less_rigor_in_reviewing_methodology_and_experiment": ["accept_for_future_work", "reject_criticism", "refute_question"], 
    "misinterpretation_of_claims_and_ideas_presented_in_the_paper": ["contradict_assertion", "refute_question", "reject_criticism"], 
    "superficial_and_vague_review": ["refute_question"], 
    "incomplete,_incorrect,_or_copied_summary": [], 
    "syntactic,_structural,_or_semantic_issues_in_the_review": ["mitigate_criticism"], 
    "misidentification_of_syntactic_or_structural_issues_in_the_paper": [],
    "non_deficient": ["answer_question", "the_task_is_done", "the_task_will_be_done", "concede_criticism", "mitigate_criticism", "accept_praise"]
}

rebuttal_action_classifier_prompt ='''
Given a paper submission, its corresponding review, and feedback from the author for predicting rebuttal action, your job is to predict a rebuttal action for a particular segment.

The criteria for deficiency are:
{DEFICIENT}

Deficient statements can have following error types (All error types with definitions are given below):
{ERROR_TYPES}

Definition of rebuttal actions:
{REBUTTAL_ACTIONS_DEFINITIONS}

Paper title: {PAPER_TITLE}
Paper content: {PAPER_CONTENT}
Review: {REVIEW}

Current segment to be predicted: {SEGMENT_TO_BE_PREDICTED}

User feedback about which rebuttal action is applicable: {USER_INPUT}
Deficiency status of the current segment: {DEFICIENCY_STATUS}
Error type of the current segment: {ERROR_TYPE}
Subset of the rebuttal actions applicable for the particular segment: {SUBSET_REBUTTAL_ACTIONS}

Please select an appropriate rebuttal action for the current segment.
Please take care of the following while predicting for the given segment
1. Only output one rebuttal action from the subset of the rebuttal actions provided and nothing else.
2. Consider paper title, paper content, content of the entire review, criteria for deficiency, definition of error-types, deficiency status, and error-types for the current segment, and general domain knowledge.
'''

rebuttal_action_prediction_prompt ='''
Given a paper submission, its corresponding review your job is to predict a rebuttal action for a particular segment.

The criteria for deficiency are:
{DEFICIENT}

Deficient statements can have following error types (All error types with definitions are given below):
{ERROR_TYPES}

Definition of rebuttal actions:
{REBUTTAL_ACTIONS_DEFINITIONS}

Paper title: {PAPER_TITLE}
Paper content: {PAPER_CONTENT}
Review: {REVIEW}

Current segment to be predicted: {SEGMENT_TO_BE_PREDICTED}

Deficiency status of the current segment: {DEFICIENCY_STATUS}
Error type of the current segment: {ERROR_TYPE}
Subset of the rebuttal actions applicable for the particular segment: {SUBSET_REBUTTAL_ACTIONS}

Please select an appropriate rebuttal action for the current segment.
Please take care of the following while predicting for the given segment
1. Only output one rebuttal action from the subset of the rebuttal actions provided and nothing else.
2. Consider paper title, paper content, content of the entire review, criteria for deficiency, definition of error-types, deficiency status, and error-types for the current segment, and general domain knowledge.
'''

first_prompt = '''
The information about the paper and review is given below:

Paper title: 
{PAPER_TITLE} 

Paper content: 
{PAPER_CONTENT}

Full review:
{REVIEW}
'''

error_type_base_prompt ='''
Given a paper submission and its corresponding review, your job is to assess the deficiency error-type of a given segment.
You need to assess the type of error-type for a deficient review segment.

The criteria for deficiency are:
{DEFICIENT}

Deficient segment have following error types (All error types with definitions are given below):
{ERROR_TYPES}

Following is the information about the paper, and review:

Paper title: 
{PAPER_TITLE} 

Paper content: 
{PAPER_CONTENT}

Full eview:
{REVIEW}

Current segment:
{CURRENT_SEGMENT}

What is the deficiency error type for the current segment? Take care of the following while predicting the error-type.
1. Select from the list of error-types only. If no error-type is valid return "None".
2. Consider the definition of error-types, rest of the review, paper title, paper content while predicting for current segment.
3. Output only the name of the error-type or None and nothing else.
'''

system_prompt_error_type_prediction = '''
Assume you are a deficiency error type predictor for segments of a peer-review of a paper of an NLP conference.
'''

ERROR_TYPES_FINEGRAINED='''
Misunderstanding: The reviewer misinterprets claims or ideas presented in the paper, leading to inaccurate or irrelevant comments.
Neglect: The reviewer overlooks important details explicitly stated in the paper, resulting in unwarranted questions or critiques.
Vague Critique: The review lacks specificity, claiming missing components without clearly identifying what is missing.
Inaccurate Summary: The summary in the review misrepresents the main content or contributions of the paper.
Out-of-scope: The reviewer suggests additional methods, experiments, or analyses that are beyond the intended scope of the paper.
Misunderstanding of the Submission Rule: The reviewer believes the submission format violates conference rules, but this is not actually the case.
Subjective: The review makes assertions about the paper’s clarity or quality without providing sufficient justification or evidence.
Invalid Criticism: The reviewer’s criticism is considered invalid, especially when suggesting impractical experiments or trivializing results.
Misinterpret Novelty: The reviewer questions the novelty of the work without substantiating their claims with relevant references
Superficial Review: The reviewer appears to have only skimmed the paper, providing generic or unsupported comments about the presence or absence of weaknesses.
Writing: Discrepancies arise when the reviewer praises the writing, while our annotator suggests it needs more clarity or explicitness.
Inexpert Statement: The reviewer exhibits a lack of domain knowledge, leading to unnecessary or irrelevant concerns.
Missing Reference: The reviewer proposes alternative frameworks or methods without providing justification or citing relevant references
Experiment: Conflicting opinions about the design of experiments; the reviewer praises them while our annotator suggests adding more baselines or tests.
Misplaced attributes: Strengths are incorrectly listed as weaknesses or vice versa.
Invalid Reference: The reviewer cites non-peer-reviewed sources or blogs, which is not appropriate for academic validation.
Unstated statement: Statements made in the review are not supported by content in the paper.
Summary Too Short: The provided summary is excessively brief, offering little to no insight into the actual content of the paper.
Contradiction: The reviewer contradicts themselves within the review, such as criticizing the paper’s experiments while later stating that the experiments are comprehensive.
Typo: The review contains typographical errors that may affect clarity or understanding.
Copy-pasted Summary: The summary is directly copied from the submission.
Concurrent work: The reviewer requests comparisons with work conducted concurrently, which may not have been considered by the authors.
Duplication: The review segment is a repetition or duplication of a previous segment within the same review.
'''

error_type_mapping_dict = {"Invalid Reference":"Incorrect references",
"Concurrent work":"Incorrect references",
"Out-of-scope":"Less rigor in reviewing methodlogy and experiments",
"Invalid Criticism":"Less rigor in reviewing methodlogy and experiments",
"Experiment":"Less rigor in reviewing methodlogy and experiments",
"Misunderstanding":"Misinterpretation of claims and ideas presented in the paper",
"Neglect":"Misinterpretation of claims and ideas presented in the paper",
"Inexpert Statement":"Misinterpretation of claims and ideas presented in the paper",
"Unstated statement":"Misinterpretation of claims and ideas presented in the paper",
"Misinterpret Novelty":"Superficial and vague review",
"Vague Critique":"Superficial and vague review",
"Subjective":"Superficial and vague review",
"Superficial Review":"Superficial and vague review",
"Missing Reference":"Superficial and vague review",
"Inaccurate Summary":"Incomplete, incorrect, or copied summary",
"Summary Too Short":"Incomplete, incorrect, or copied summary",
"Copy-pasted Summary":"Incomplete, incorrect, or copied summary",
"Typo":"Syntactic, structural, or semantic issues in the review",
"Contradiction":"Syntactic, structural, or semantic issues in the review",
"Misplaced attributes":"Syntactic, structural, or semantic issues in the review",
"Duplication":"Syntactic, structural, or semantic issues in the review",
"Writing":"Misidentification of Syntactic or structural issues in the paper",
"Misunderstanding of the Submission Rule":"Misidentification of Syntactic or structural issues in the paper",
"none": "none",
"None": "none"}

rebuttal_generator_segment_wise = '''
You are assisting in academic peer-review rebuttal writing.

Given the current review segment, paper title, and paper content generate a rebuttal segment specifically for the current review segment.

Paper Title: {PAPER_TITLE}
Paper Content: {PAPER_CONTENT}
Current review segment to be predicted: {SEGMENT}

Please generate a rebuttal segment for the current review segment. If no rebuttal is needed output "No rebuttal needed".

Please take care of the following while generating the rebuttal segment:
1. A part of the rebuttal is to be generated only for the current review segment to be predicted.
2. Generate a rebuttal in fluent academic professional tone addressing the concerns and suggestions in the review. It should not contain any offensive terms.
3. Avoid generic statements. Be precise and point-wise.
4. The rebuttal segment generated should not use verbose or confusing language.
5. The rebuttal segment should be complete. Please take care of covering all the required points from the review segment that needs to be answered.
6. All the responses should be factually and logically correct, detailed, and supported by evidence.
7. The rebuttal segment generated should be relevant to the points in the review segment.
8. The rebuttal segment generated should be constructive, either it should foster discussion or offer solutions. It should provide actionable feedback.
9. The rebuttal segment generated should help the author in getting their scores increased and should help in increasing the chances of acceptance.
10. The rebuttal segment generated should be consistent and coherent and should not have any contradicting statements.
11. Consider paper title, paper content, and general domain knowledge while generating a rebuttal segment for the current review segment.
12. Be very-very concise in generating a rebuttal segment. Try to provide a concise, short and complete answer.
13. If the review segment is a summary or just a statement about the paper, the rebuttal segment will be "No rebuttal needed".
14. For the review segments where there is no need to respond, please provide the output as no rebuttal needed.
'''

#baseline3 
rebuttal_generation_prompt = '''
You are assisting in academic peer-review rebuttal writing.

Given the current review segment, paper title, and paper content generate a rebuttal segment specifically for the current review segment.

The criteria for deficiency are:
{DEFICIENT}

Deficient statements can have following error types (All error types with definitions are given below):
{ERROR_TYPES}

Definition of rebuttal actions:
{REBUTTAL_ACTIONS_DEFINITIONS}

Paper title: {PAPER_TITLE}
Paper content: {PAPER_CONTENT}

Current review segment to be predicted: {SEGMENT_TO_BE_PREDICTED}

Deficiency status of the current segment: {DEFICIENCY}
Error type of the current segment: {ERROR_TYPE}
Rebuttal action for the current segment: {REBUTTAL_ACTION}

Please generate a rebuttal segment for the current review segment. If no rebuttal is needed output "No rebuttal needed".

Please take care of the following while generating the rebuttal sentence:
1. A part of the rebuttal is to be generated only for the current review segment to be predicted.
2. Generate a rebuttal in fluent academic professional tone addressing the concerns and suggestions in the review. It should not contain any offensive terms.
3. Avoid generic statements. Be precise and point-wise if needed.
4. The rebuttal segment generated should not use verbose or confusing language.
5. The rebuttal segment should be complete. Please take care of covering all the required points from the review segment that needs to be answered.
6. All the responses should be factually and logically correct, detailed, and supported by evidence.
7. The rebuttal segment generated should be relevant to the points in the review segment.
8. The rebuttal segment generated should be constructive, either it should foster discussion or offer solutions. It should provide actionable feedback.
9. The rebuttal segment generated should help the author in getting their scores increased and should help in increasing the chances of acceptance.
10. The rebuttal segment generated should be consistent and coherent and should not have any contradicting statements.
11. Consider paper title, paper content, criteria for deficiency, definition of error-types, deficiency status, error-types, rebuttal action for the current segment, and general domain knowledge.
12. Be very concise in generating a rebuttal segment.
13. If the review segment is a summary or just a statement about the paper, the rebuttal segment will be "No rebuttal needed".
14. For the review segments where there is no need to respond, please provide the output as no rebuttal needed.'''

CONSOLIDATE_PROMPT = '''
Given a paper title, paper content, review, and rebuttal segments for each review segment.

Paper title: {PAPER_TITLE}
Paper content: {PAPER_CONTENT}
Review and rebuttal information for each segment: {REVIEW_REBUTTAL}

Please consolidate the entire rebuttal in a structured format replying to each review segment to send back to the reviewer to increase chances of acceptance.

While consolidating please take care of the following:
1. Consider the provided review segment with their rebuttal and use them to construct a coherent rebuttal.
2. Do not provide strategy to construct a rebuttal in the rebuttal but provide the rebuttal only. Do not write Review Segment 1 etc in the final rebuttal. Just the review segment in bold is sufficient. 
3. Do not include segments with No Rebuttal Needed in consolidating the final rebuttal.
4. Provide a single statement for thanking the reviewers for their valuable feedback. Do not provide a thanking statement with each and every rebuttal segment.
5. The consolidated rebuttal should look like an original author's response without any redundant thanking statements or repetitions.
6. Provide a single statement for thanking the reviewers for their valuable feedback in the start of the rebuttal.
7. The generated rebuttal should be in markdown format.
8. The rebuttal generated should not use verbose or confusing language.
9. The rebuttal generated should be relevant to the points in the review.'''

consolidate_rebuttal_prompt = '''

Given a paper title, paper content, review, and rebuttal segments for each review segment.

Paper title: {PAPER_TITLE}
Paper content: {PAPER_CONTENT}
Review and rebuttal information for each segment: {REVIEW_REBUTTAL}

Please consolidate the entire rebuttal in a structured format replying to each review segment to send back to the reviewer to increase the chances of acceptance.

While consolidating please take care of the following:
1. The consolidated rebuttal should be coherent and should not have any repetition.
2. Do not provide strategy to construct a rebuttal in the consolidated rebuttal but provide the rebuttal only. 
3. Provide a single statement for thanking the reviewers for their valuable feedback in the start of the rebuttal.
4. The consolidated rebuttal should look like an original author's response without any redundant thanking statements or repetitions.
5. Do not include segments with No Rebuttal Needed in consolidating the rebuttal.
6. Do not write "Review Segment 1 etc in the final consolidated rebuttal. Do not include phrases like "here's a detailed rebuttal addressing the reviewer's comments", Rebuttal to Reviewer Comments etc. in the rebuttal. Directly start from a thanking statement.
7. Do not include lines like here is the rebuttal or here is the consolidation, directly start providing the consolidated rebuttal without any irrelevant sentences.
8. The consolidated rebuttal should be factually and logically correct, detailed, and supported by evidence.
9. The rebuttal generated should be relevant to the points in the review.
10. The rebuttal generated should help the author in getting their scores increased and should help in increasing the chances of acceptance.
11. The rebuttal generated should be consistent and coherent and should not have any contradicting statements.
12. Avoid generic statements. Be precise and point-wise if needed.
13. The rebuttal generated should not use verbose or confusing language.
14. The rebuttal should be complete. Please take care of covering all the required points from the review that needs to be answered.
15. Please consider paper title, paper content, and entire review. while generating the rebuttal.
16. The generated rebuttal should be in markdown format.
17. It should follow the format of **<Review segment>** \n <Rebuttal segment>, without headings, review segment should be bold.
'''

segment_review = '''
Create partition/segments of the review based on different sections or meaningful units.

Review: {Review}
While generating please take care of the following:
- Segments are a meaningful continuous part from the review.
- Segments should be from the review itself, no content should be added extra in the segments.
- There should be no overlap of sentences between two segments.
- The segments should be separated by | character.
- Summary should be in one single segment.
- Each component of strengths and weaknesses should be separate segments.
- Each question should be a separate segment.
- All segments combined should constitute the complete review.
'''

mapping_error_type_statement = {
    "incorrect_references":"The reviewer is not citing the appropriate sources (non peer-reviewed or concurrent work) in the current statement (Incorrect references). Do you agree?",
    "less_rigor_in_reviewing_methodology_and_experiment":"In the current statement, the reviewer is suggesting things beyond the scope of the paper or the reviewer's criticism is invalid (Less rigor in reviewing methodology and experiment). Do you agree?",
    "superficial_and_vague_review":"In the current statement, the reviewer has misinterpreted novelty or the reviewer is lacking specificity of the components (Superficial and vague review). Do you agree?",
    "misinterpretation_of_claims_and_ideas_presented_in_the_paper":"In the current statement, the reviewers is misinterpreting the claims and ideas presented in the paper and overlooked important details of the paper or the reviewer is exhibiting lack of domain knowledge or not supported by the content of the paper (Misinterpretation of claims and ideas presented in the paper). Do you agree?",
    "incomplete,_incorrect,_or_copied_summary":"In the current statement, the summary is misrepresenting the content of the paper, or too short or directly copied from the paper (Incomplete, incorrect, or copied summary). Do you agree?",
    "syntactic,_structural,_or_semantic_issues_in_the_review":"The current review statement has typological errors that are affecting the clarity (Syntactic, structural, or semantic issues in the review). Do you agree?",
    "misidentification_of_syntactic_or_structural_issues_in_the_paper":"In the current review statement, the reviewer has misidentified the structural issues in the paper (Misidentification of syntactic or structural issues in the paper). Do you agree?"
}

mapping_error_type_rebuttal_action = {
    "incorrect_references": ["reject_request"], 
    "less_rigor_in_reviewing_methodology_and_experiment": ["accept_for_future_work", "reject_criticism", "refute_question"], 
    "misinterpretation_of_claims_and_ideas_presented_in_the_paper": ["contradict_assertion", "refute_question", "reject_criticism"], 
    "superficial_and_vague_review": ["refute_question"], 
    "incomplete,_incorrect,_or_copied_summary": [], 
    "syntactic,_structural,_or_semantic_issues_in_the_review": ["mitigate_criticism"], 
    "misidentification_of_syntactic_or_structural_issues_in_the_paper": [],
    "non_deficient": ["answer_question", "the_task_is_done", "the_task_will_be_done", "concede_criticism", "mitigate_criticism", "accept_praise"]
}

mapping_deficiency_statement = {
    "deficient": "The review statement is not valid. It contains either contain factual errors or lacking constructive feedback or subjective or without evidence.",
    "non-deficient": "The review statement is valid in in-terms of factuality and constructive feedback."
}

mapping_rebuttal_action_statement = {
"reject_request": "The request needs to be rejected (Reject request). Do you agree?",
"accept_for_future_work": "The suggested things needs to be accepted as future work (Accept for future work). Do you agree?",
"reject_criticism": "The criticism needs to be rejected (Reject Criticism). Do you agree?",
"refute_question": "The question needs to be disproved (Refute criticism). Do you agree?",
"contradict_assertion": "The statement needs to be contradicted (Contradict assertion). Do you agree?",
"mitigate_criticism": "The rebuttal statement needs to be generated in a manner that represents the statement is not important (Mitigate criticism). Do you agree?",
"answer_question": "The question needs to be answered (Answer question). Do you agree?",
"the_task_is_done": "The rebuttal statement needs to specify the task has already been done and pinpoint where (The task is done). Do you agree?",
"the_task_will_be_done": "The rebuttal statement needs to specify the task will be done in camera ready (The task will be done). Do you agree?",
"concede_criticism": "The rebuttal statement needs to admit to the provided criticism (Concede criticism). Do you agree?",
"accept_praise": "The rebuttal statement needs to accept the praise (Accept praise). Do you agree?",
"no_rebuttal": "No rebuttal needed (No Rebuttal). Do you agree?"
}

mapping_rag_need_deficient = {
"superficial_and_vague_review|refute_question",
"superficial_and_vague_review|reject_criticism",
"superficial_and_vague_review|contradict_assertion"
}

mapping_rag_need_non_deficient = {
"answer_question",
"the_task_will_be_done",
"concede_criticism",
"mitigate_criticism"
}

deficiency_true_question = "The review statement is not valid. It contains either contain factual errors or lacking constructive feedback or subjective or without evidence (Deficient). Do you agree? Reply in Yes/No"
deficiency_false_question = "The review statement is valid in interms of factuality and constructive feedback (Non-deficient). Do you agree? Reply in Yes/No." 
could_not_predict_error_type_statement = "Please provide feedback on what kind of deficiency the review segment has."
could_not_predict_rebuttal_action_statement = "Please provide feedback on what kind of rebuttal action is to be taken."
could_not_generate_rebuttal_question = "Please provide the edited rebuttal."
deficiency_questions = [deficiency_true_question, deficiency_false_question]
error_type_questions = mapping_error_type_statement
rebuttal_action_questions = mapping_rebuttal_action_statement
