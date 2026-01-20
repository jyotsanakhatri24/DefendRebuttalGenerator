'''
1.Iterate through the review segments
2. For each review segment, check if there is mention of a citation, if yes just retrieve that citation and use the original paper and this citation as reference.
3. If there is no citation, take original deficiency, error-type, and rebuttal action -> as per static table perform retrieval from literature and provide the outputs in the prompt together with the paper.
4. Perform generation with relevant content.
'''
import logging
import requests
from datetime import datetime

# Disable all logging messages below the CRITICAL level (effectively disabling all logs)
logging.disable(logging.CRITICAL)
import json
import time
from tqdm import tqdm
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from scripts.llm_call import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(
    BASE_DIR,
    "..",  # adjust number of ".." depending on where this file lives
    "ai2-scholarqa-lib-main",
    "api"
)

sys.path.insert(0, os.path.abspath(relative_path))

from scholarqa import ScholarQA
from scholarqa.rag.retrieval import PaperFinder, PaperFinderWithReranker
from scholarqa.rag.retriever_base import FullTextRetriever
from scholarqa.rag.reranker.modal_engine import ModalReranker
from scholarqa.rag.reranker.modal_engine import HuggingFaceReranker
from scripts.rag_prompts import *
import os
os.environ['CURL_CA_BUNDLE'] = ''
os.environ["PYTHONHTTPSVERIFY"] = "0"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
S2_API_KEY = os.environ.get("S2_API_KEY")

model = os.environ['MODEL_NAME']
def load_jsonl(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def save_jsonl(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def fetch_semantic_scholar_paper_from_citation(citation):
    return paper_content

def retrieve_paper_publication_key(paper_title):
    search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": paper_title,
        "fields": "title,year,publicationDate",
        "limit": 1
    }
    import os
    S2_API_KEY = os.environ.get("S2_API_KEY")
    headers = {"x-api-key": S2_API_KEY}

    # Step 1: search by title
    res = requests.get(search_url, params=params, headers=headers)
    data = res.json()
    
    if data and data["data"]:
        paper = data["data"][0]
        return paper.get("publicationDate")
    else:
        return date.today() 

def check_if_review_segment_has_citation(review_segment, review, paper_title, paper_content):
    return "no"
    has_citation = review_segment_has_citation_or_link.format(REVIEW_SEGMENT=review_segment)
    if has_citation.lower().strip() == "yes":
        return fetch_semantic_scholar_paper_from_citation(citation)
    else:
        return "no"

def rag_needed(deficiency, error_type, rebuttal_action):
    if deficiency == "no":
        if rebuttal_action in mapping_rag_need_non_deficient:
            return True
    elif deficiency == "yes":
        if error_type+"|"+rebuttal_action in mapping_rag_need_deficient:
            return True
    return False

def make_query(review_segment, review, paper_title, paper_content):
    prompt = construct_semantic_scholar_query.format(REVIEW=review, REVIEW_SEGMENT=review_segment, PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content)
    query = model_calling(prompt, model)
    return query

def pipeline_rag(query, publication_date):
    print("Running the pipeline")
    retriever = FullTextRetriever(n_retrieval=10, n_keyword_srch=10)
    reranker = HuggingFaceReranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2", batch_size=256)
    paper_finder = PaperFinderWithReranker(retriever, reranker=reranker, n_rerank=5, context_threshold=0.1)
    scholar_qa = ScholarQA(paper_finder=paper_finder, llm_model="gemini/gemini-2.0-flash")
    answer = scholar_qa.answer_query(query, publication_date)
    return answer

def retrieve_relevant_literature(review_segment, review, paper_title, paper_content, publication_date):
    query = make_query(review_segment, review, paper_title, paper_content)
    try:
        retrieved_content = pipeline_rag(query, publication_date)
        if retrieved_content and "sections" in retrieved_content:
            retrieved_content = retrieved_content
        else:
            search_results = {"sections": [], "query": query}
            retrieved_content = search_results
            print("No sections found in retrieved content")
    except Exception as e:
        search_results = {"sections": [], "query": query}
        retrieved_content = search_results
        print("Exception in retrieval:" + str(e))
    relevant_content = format_the_retrieved_content(retrieved_content)
    return query, relevant_content

def format_the_retrieved_content(response):
    # Format the retrieved knowledge for the ideation agent
    retrieved_content = []
    for section in response.get("sections", []):
        section_text = f"## {section.get('title', 'Untitled')}\n\n"
        section_text += f"{section.get('text', '')}\n\n"
        
        # Add citations if available
        if section.get("citations"):
            section_text += "### References:\n"
            for citation in section.get("citations", []):
                paper = citation.get("paper", {})
                authors = ", ".join([author.get("name", "") for author in paper.get("authors", [])[:3]])
                if len(paper.get("authors", [])) > 3:
                    authors += " et al."
                section_text += f"- {paper.get('title', 'Untitled')} ({authors}, {paper.get('year', 'n.d.')})\n"
        
        retrieved_content.append(section_text)

    # Join all sections into a single text
    formatted_knowledge = "\n\n".join(retrieved_content)
    print(formatted_knowledge)
    return formatted_knowledge
    
def process_retrieved_content_and_generate(relevant_content):
    prompt = get_final_answer.format(REVIEW=review, REVIEW_SEGMENT=review_segment, PAPER_TITLE=paper_title, PAPER_CONTENT=paper_content, RELEVANT_LITERATURE=relevant_content)
    rebuttal = model_calling(prompt, model)
    return rebuttal

def get_relevant_literature(input_path, output_path):
    f_out = open(output_path+"hh",'w')
    data = load_jsonl(input_path)
    pi = 0
    for paper in tqdm(data, desc="Getting relevant literature"):
        if pi >=2 :
            paper_title = paper.get("title")
            paper_content = paper.get("body_text")
            publication_date = retrieve_paper_publication_key(paper_title)
            ri = 0
            for key in paper:
                if ri >= 0:
                    if not key.startswith("review#"):
                        continue

                    review_block = paper[key]
                    full_review = review_block.get("full_review")
                    segments = review_block.get("semantic", [])["review_segments"]
                    si = 0
                    for seg in segments:
                        print(pi, ri, si)
                        seg_text = seg.get("segment_text").strip()
                        reliability = seg.get("reliability", "yes")
                        if reliability.strip().lower() == "yes":
                            deficiency_status = "no"
                        else:
                            deficiency_status = "yes"
                        error_type = seg.get("error_type", "None")
                        rebuttal_action = seg.get("rebuttal_action_backward")
                        
                        #if rag_needed(deficiency_status, error_type, rebuttal_action):
                        if_citation = "no"#check_if_review_segment_has_citation(seg_text, full_review, full_review, paper_content)
                        if if_citation == "yes":
                            only_retrieve_cited_paper()
                        else:
                            query, relevant_literature = retrieve_relevant_literature(seg_text, full_review, paper_title, paper_content, publication_date)
                            seg["query"] = query #process_retrieved_content_and_generate(relevant_literature)
                            seg["retrieved_literature"] = relevant_literature #process_retrieved_content_and_generate(relevant_literature)
                            f_out.write(str(pi)+"."+str(ri)+"."+str(si))
                            f_out.write("\n")
                            f_out.write(query)
                            f_out.write("\n\n")
                            f_out.write(relevant_literature)
                            f_out.write("\n\n\n") 
                        si = si + 1
                ri = ri + 1
        pi = pi + 1
    save_jsonl(data, output_path)
    f_out.close()

#base = "/home/u2738870/Documents/RebuttalGeneration/git/RebuttalGenerationBenchmarkingNew/"
#input_file = base + "DataNew/SemanticSegmentsTaggingFinal/ss.jsonl"
#output_file = base + "Experiments_AfterMA_RAG_From_Literature/Baselines/Benchmarking/relevant_literature_23.jsonl"

#get_relevant_literature(input_file, output_file)