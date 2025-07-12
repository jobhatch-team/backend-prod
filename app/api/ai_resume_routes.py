from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Resume, ResumeScore, ResumeJobMatch, Job, db
from openai import OpenAI
import os
import fitz
import boto3
import re
import json
from docx import Document
from io import BytesIO

ai_resume_routes = Blueprint('ai_resume', __name__)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('S3_KEY'),
    aws_secret_access_key=os.getenv('S3_SECRET'),
    region_name='us-east-1'
)

def get_file_bytes_from_s3(s3_url):
    match = re.match(r"https://(.+)\.s3\.amazonaws\.com/(.+)", s3_url)
    if not match:
        return None
    bucket_name, key = match.groups()
    obj = s3.get_object(Bucket=bucket_name, Key=key)
    return obj['Body'].read()

def extract_text_from_pdf_bytes(pdf_bytes, max_pages=3):
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc[:max_pages]:
            text += page.get_text()
    return text

def extract_text_from_docx_bytes(docx_bytes):
    doc = Document(BytesIO(docx_bytes))
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_resume_text(file_url):
    file_bytes = get_file_bytes_from_s3(file_url)
    if not file_bytes:
        return None, "Failed to download resume file"
    ext = file_url.rsplit('.', 1)[-1].lower()
    if ext == 'pdf':
        text = extract_text_from_pdf_bytes(file_bytes)
    elif ext == 'docx':
        text = extract_text_from_docx_bytes(file_bytes)
    else:
        return None, f"Unsupported file type: {ext}"
    return text, None

@ai_resume_routes.route('/chat', methods=['POST'])
@login_required
def chat_with_ai():
    data = request.get_json()
    messages = data.get('messages')

    if not messages or not isinstance(messages, list):
        return jsonify({'error': 'Invalid or missing messages'}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
        )
        ai_reply = response.choices[0].message.content
        return jsonify({'reply': ai_reply}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_resume_routes.route('/resumes/<int:resume_id>/analyze', methods=['POST'])
@login_required
def analyze_resume(resume_id):
    resume = Resume.query.get(resume_id)
    if not resume or resume.user_id != current_user.id:
        return jsonify({"error": "Resume not found or permission denied"}), 404

    text, error = extract_resume_text(resume.file_url)
    if error:
        return jsonify({"error": error}), 400
    if not text.strip():
        return jsonify({"error": "No text extracted from resume file"}), 400

    prompt = f"""
You are an expert HR professional and AI resume analyst.

Please analyze the following resume text and provide a JSON response with the following fields:
- score_overall: float between 0 and 10
- score_format: float between 0 and 10
- score_skills: float between 0 and 10
- score_experience: float between 0 and 10
- strengths: a concise description of the candidate's strengths
- weaknesses: a concise description of the candidate's weaknesses
- suggestions: concrete suggestions for improvement

Respond ONLY with valid JSON.

Resume text:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes resumes and returns JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        analysis_json_str = response.choices[0].message.content
        analysis_data = json.loads(analysis_json_str)

        new_score = ResumeScore(
            resume_id=resume.id,
            ai_model="gpt-4",
            score_overall=analysis_data.get("score_overall"),
            score_format=analysis_data.get("score_format"),
            score_skills=analysis_data.get("score_skills"),
            score_experience=analysis_data.get("score_experience"),
            strengths=analysis_data.get("strengths"),
            weaknesses=analysis_data.get("weaknesses"),
            suggestions=analysis_data.get("suggestions"),
        )

        db.session.add(new_score)
        db.session.commit()

        return jsonify({"analysis": analysis_data, "score_id": new_score.id}), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse AI analysis JSON"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_resume_routes.route('/resumes/<int:resume_id>/jobs/<int:job_id>/match', methods=['POST'])
@login_required
def match_resume_to_job(resume_id, job_id):
    resume = Resume.query.get(resume_id)
    if not resume or resume.user_id != current_user.id:
        return jsonify({"error": "Resume not found or permission denied"}), 404

    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    resume_text, error = extract_resume_text(resume.file_url)
    if error:
        return jsonify({"error": error}), 400
    if not resume_text.strip() or len(resume_text.strip()) < 20:
        return jsonify({"error": "Resume text too short or empty"}), 400

    prompt = f"""
You are a recruitment AI assistant. Given the resume text and the job description below,
analyze the candidate's fit for the job. Return a JSON with:
- match_score: a float from 0 to 1, indicating the suitability
- match_summary: a brief summary highlighting strengths and weaknesses for this job.

Job Title: {job.title}
Job Description: {job.description}

Resume Text:
{resume_text[:3000]}

Respond ONLY with a valid JSON object.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI recruitment assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0]
        elif '```' in content:
            content = content.split('```')[1]

        ai_result = json.loads(content)

        match_score = ai_result.get("match_score")
        match_summary = ai_result.get("match_summary")

        if match_score is None or match_summary is None:
            return jsonify({"error": "AI response missing required fields"}), 500

        existing_match = ResumeJobMatch.query.filter_by(resume_id=resume_id, job_id=job_id).first()
        if existing_match:
            existing_match.match_score = match_score
            existing_match.match_summary = match_summary
        else:
            new_match = ResumeJobMatch(
                resume_id=resume_id,
                job_id=job_id,
                match_score=match_score,
                match_summary=match_summary
            )
            db.session.add(new_match)

        db.session.commit()

        return jsonify({
            "resume_id": resume_id,
            "job_id": job_id,
            "match_score": match_score,
            "match_summary": match_summary
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500

