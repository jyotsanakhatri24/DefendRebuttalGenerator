from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from flask import session
from uuid import uuid4
from scripts.rebuttal_generation import *
from scripts.pipeline_rebuttal_generation import *
import sys
from scripts.segment_scoring import score_review_rebuttal_segment

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store review and rebuttal pairs
rebuttal_segments = []
accepted_segments = []
paper_title = ""
paper_content = ""
review_text = ""
error_type_done_once = False
rebuttal_action_done_once = False
chat_sessions = {}  # session_id: {index: [chat_history]}
rag_query = None
rag_context = None
used_rag = False

NO_CHATBOX_KEYWORDS = [
        "valid in interms of factuality",
        "valid", 
        "no deficiency"
    ]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    global rebuttal_segments, accepted_segments, paper_title, paper_content, review_text, error_type_done_once, rebuttal_action_done_once, chat_sessions
    session_id = request.cookies.get('session_id') or str(uuid4())
    chat_sessions = {}
    rebuttal_segments = []
    accepted_segments = []

    paper_title = request.form['title']
    review_text = request.form['review']
    segments = get_segments_from_review(review_text)
    
    pdf_file = request.files['pdf']
    if pdf_file:
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(pdf_file.filename))
        pdf_file.save(pdf_path)

    paper_content = extract_pdf_content(pdf_path)
    rebuttals = direct_rebuttal_generation_segment(segments, paper_title, paper_content, review_text)

    
    for i in range(len(segments)):
        rebuttal_segments.append({
            "review": segments[i],
            "rebuttal": rebuttals[i]
        })
    review_rebuttal = ""
    for i in rebuttal_segments:
        review_rebuttal = review_rebuttal + "Review segment: " + i["review"] + "\n Rebuttal segment:" + i["rebuttal"] + "\n\n"
    
    consolidated = consolidate_rebuttal_llm(paper_title, paper_content, review_rebuttal)
    return jsonify({
         "segments": rebuttal_segments,
        "final_rebuttal": consolidated
        })

@app.route('/accept/<int:index>', methods=['POST'])
def accept(index):
    global rebuttal_segments, accepted_segments, paper_title, paper_content, review_text, error_type_done_once, rebuttal_action_done_once
    session_id = request.cookies.get('session_id') or str(uuid4())
    chat_sessions[session_id][index] = []
    accepted_segments.append(rebuttal_segments[index])
    return '', 204

@app.route('/reject/<int:index>', methods=['POST'])
def reject(index):
    global rebuttal_segments, accepted_segments, paper_title, paper_content, review_text, chat_sessions, error_type_done_once, rebuttal_action_done_once
    session_id = request.cookies.get('session_id') or str(uuid4())
    chat_sessions[session_id][index] = []
    segment = rebuttal_segments[index]
    query = deficiency_prediction(segment["review"], paper_title, paper_content, review_text)
    return jsonify({
        "query": query
    })

@app.route('/editAgain/<int:index>', methods=['POST'])
def editAgain(index):
    global rebuttal_segments, accepted_segments, paper_title, paper_content, review_text, chat_sessions, error_type_done_once, rebuttal_action_done_once
    session_id = request.cookies.get('session_id') or str(uuid4())
    chat_sessions[session_id][index] = []
    segment = rebuttal_segments[index]
    query = deficiency_prediction(segment["review"], paper_title, paper_content, review_text)
    return jsonify({
        "query": query
    })

@app.route('/consolidate', methods=['GET', 'POST'])
def consolidate():
    global rebuttal_segments, accepted_segments, paper_title, paper_content, review_text, error_type_done_once, rebuttal_action_done_once
    review_rebuttal = ""
    if request.method == 'POST':
        segments = request.json.get("segments", [])
    else:
        # fallback to global storage
        segments = rebuttal_segments
    for i in segments:
        review_rebuttal = review_rebuttal + "Review segment: " + i["review"] + "\n Rebuttal segment:" + i["rebuttal"] + "\n\n"
    consolidated = consolidate_rebuttal_llm(paper_title, paper_content, review_rebuttal)
    return jsonify({"final_rebuttal": consolidated})

@app.route('/chat/<int:index>', methods=['POST'])
def chat(index):
    global rebuttal_segments, accepted_segments, paper_title, paper_content, review_text, deficiency, error_type, rebuttal_action, generated_rebuttal, error_type_done_once, rebuttal_action_done_once, rag_query, rag_context, used_rag
    user_input = request.json.get('message')
    session_id = request.cookies.get('session_id') or str(uuid4())
    response = ''
    segment = rebuttal_segments[index]['review']
    rebuttal = rebuttal_segments[index]['rebuttal']
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {}
    if index not in chat_sessions[session_id]:
        chat_sessions[session_id][index] = []

    response, rag_query, rag_context, used_rag, chat_history, paper_title, paper_content, review_text, deficiency, error_type, rebuttal_action, generated_rebuttal, error_type_done_once, rebuttal_action_done_once = pipeline(segment, rebuttal, paper_title, paper_content, review_text, chat_sessions[session_id][index], user_input, deficiency, error_type, rebuttal_action, generated_rebuttal, error_type_done_once, rebuttal_action_done_once, rag_query, rag_context, used_rag)
    chat_sessions[session_id][index] = chat_history
    
    return jsonify({
    "reply": response,
    "rag_context": rag_context,
    "rag_query": rag_query,
    "used_rag": rag_context is not None
    })

    res.set_cookie("session_id", session_id)
    return res

if __name__ == '__main__':
    app.run(debug=True)
