from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Resume, ResumeScore, db
from openai import OpenAI
import os

import fitz
import boto3
import re
import json

ai_routes = Blueprint('ai', __name__)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Chat with AI (login required)
@ai_routes.route('/chat', methods=['POST'])
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
    

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('S3_KEY'),
    aws_secret_access_key=os.getenv('S3_SECRET'),
    region_name='us-east-1'
)

def get_pdf_bytes_from_s3(s3_url):
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

@ai_routes.route('/resumes/<int:resume_id>/analyze', methods=['POST'])
@login_required
def analyze_resume(resume_id):
    resume = Resume.query.get(resume_id)
    if not resume or resume.user_id != current_user.id:
        return jsonify({"error": "Resume not found or permission denied"}), 404

    pdf_bytes = get_pdf_bytes_from_s3(resume.file_url)
    if not pdf_bytes:
        return jsonify({"error": "Failed to download resume file"}), 500

    text = extract_text_from_pdf_bytes(pdf_bytes)
    if not text.strip():
        return jsonify({"error": "No text extracted from PDF"}), 400

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
