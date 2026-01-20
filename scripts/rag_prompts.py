review_segment_has_citation_or_link = '''
You are given a review segment. Determine whether it contains any citation or link, such as references to papers, URLs, DOIs, inline citations (e.g., “[1]”, “(Smith et al., 2020)”), or hyperlink text (e.g., “https://…”, “doi.org/...”, “arXiv:…”).

Instructions:
Respond with "Yes" if the segment includes any kind of citation or hyperlink.
Respond with "No" if there are no citations or links.

Review segment: {REVIEW_SEGMENT}

Your output should only contain the Yes/No and nothing else.
'''

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

construct_semantic_scholar_query = '''
Your task is to analyze a review segment and construct a natural language query which is relevant in retrieving the literature which can help in resolving the doubts/questions/statements provided in the review segment 

Below is the review segment, paper title, and paper content. Take help of all three and construct the query helpful in retrieving the literature which can help in handling doubts/questions/statement in the review segment.

Review segment:
{REVIEW_SEGMENT}

Review:
{REVIEW}

Paper title:
{PAPER_TITLE}

Paper content:
{PAPER_CONTENT}

Your output should only contain the query and nothing else.
'''

baseline1 = '''
You are a rebuttal writing assistant for academic peer reviews.

Given the full review, paper title, and paper content, generate a complete rebuttal addressing all the reviewer comments.

Paper tttle: {PAPER_TITLE}
Paper content: {PAPER_CONTENT}

Review: {FULL_REVIEW}

Relevant content from the literature:
{RELEVANT_LITERATURE}

Please take care of the following while generating rebuttal:
1. Generate a rebuttal in fluent academic professional tone addressing the concerns and suggestions in the review. It should not contain any offensive terms.
2. Avoid generic statements. Be precise and point-wise.
3. The rebuttal generated should not use verbose or confusing language.
4. The rebuttal should be complete. Please take care of covering all the required points from the review that needs to be answered.
5. All the responses should be factually and logically correct, detailed, and supported by evidence.
6. The rebuttal generated should be relevant to the points in the review.
7. The rebuttal generated should be constructive, either it should foster discussion or offer solutions. It should provide actionable feedback.
8. The rebuttal generated should help the author in getting their scores increased and should help in increasing the chances of acceptance.
9. The rebuttal generated should be consistent and coherent and should not have any contradicting statements.
10. Consider paper title, paper content, and general domain knowledge while generating a rebuttal for the review.
11. Be very concise in generating the rebuttal.
12. For a review segment which is summary of the paper or just a statement about the paper, there is no rebuttal needed for those review segments.
13. Do not include phrases like "here's a detailed rebuttal addressing the reviewer's comments", Rebuttal to Reviewer Comments etc. in the rebuttal. Directly start from a thanking statement.
'''

baseline2 = '''
You are assisting in academic peer-review rebuttal writing.

Given the current review segment, paper title, and paper content generate a rebuttal segment specifically for the current review segment.

Paper Title: {PAPER_TITLE}
Paper Content: {PAPER_CONTENT}
Current review segment to be predicted: {SEGMENT}
Relevant content from the literature: {RELEVANT_LITERATURE}

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
12. Be very concise in generating a rebuttal segment.
13. If the review segment is a summary or just a statement about the paper, the rebuttal segment will be "No rebuttal needed".
14. For the review segments where there is no need to respond, please provide the output as no rebuttal needed.'''

baseline3 = '''
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
Relevant content from the literature: {RELEVANT_LITERATURE}

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



get_final_answer = '''
Given following review segment, paper title, paper content, relevant content from the literature to provide a rebuttal for the review segment. Provide a rebuttal sentence to provide a reply to the reviewer for the review sentence.

Review segment:
{REVIEW_SEGMENT}

Review:
{REVIEW}

Paper title:
{PAPER_TITLE}

Full Paper:
{PAPER_CONTENT}

Relevant content from the literature and llm:
{RELEVANT_LITERATURE}

Your output should only contain the rebuttal sentence and nothing else.
'''
