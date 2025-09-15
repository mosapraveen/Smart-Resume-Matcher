from flask import Flask, render_template, request, jsonify
import os
from PyPDF2 import PdfReader

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
JOB_FOLDER = 'jobs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(JOB_FOLDER, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text.lower()

def keyword_match(job_text, resume_text):
    job_words = set(job_text.split())
    resume_words = set(resume_text.split())
    common_words = job_words.intersection(resume_words)
    # Return percentage of job keywords present in resume
    return round(len(common_words) / len(job_words) * 100, 2) if job_words else 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    resume = request.files['resume']
    resume.save(os.path.join(UPLOAD_FOLDER, resume.filename))
    return f"Resume '{resume.filename}' uploaded successfully!"

@app.route('/add_job', methods=['POST'])
def add_job():
    title = request.form['title']
    description = request.form['description']
    with open(os.path.join(JOB_FOLDER, f"{title}.txt"), 'w', encoding='utf-8') as f:
        f.write(description)
    return f"Job '{title}' added successfully!"

@app.route('/match_resumes', methods=['GET'])
def match_resumes():
    results = {}
    for job_file in os.listdir(JOB_FOLDER):
        with open(os.path.join(JOB_FOLDER, job_file), 'r', encoding='utf-8') as f:
            job_text = f.read().lower()
        matches = []
        for resume_file in os.listdir(UPLOAD_FOLDER):
            resume_text = extract_text_from_pdf(os.path.join(UPLOAD_FOLDER, resume_file))
            score = keyword_match(job_text, resume_text)
            if score > 0:
                matches.append({'resume': resume_file, 'score': score})
        # Sort matches by highest percentage
        matches.sort(key=lambda x: x['score'], reverse=True)
        results[job_file.replace('.txt','')] = matches
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
