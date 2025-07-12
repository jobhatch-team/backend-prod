from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.models import db, Job, Profile, CoverLetter
from .aws_helpers import upload_pdf_bytes_to_s3
from openai import OpenAI
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from fpdf import FPDF
import os
import datetime

ai_cover_letter_routes = Blueprint('ai_cover_letter', __name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_pdf(content, title="Cover Letter"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    paragraphs = content.split('\n')
    for para in paragraphs:
        if para.strip() == "":
            story.append(Spacer(1, 12))
        else:
            story.append(Paragraph(para, styles["Normal"]))
            story.append(Spacer(1, 12))  

    doc.build(story)
    buffer.seek(0)
    return buffer

@ai_cover_letter_routes.route('/generate/job/<int:job_id>', methods=['POST'])
@login_required
def generate_cover_letter_for_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    prompt = f"""
You are a professional career advisor. Write a tailored cover letter for the following job information:

Job Title: {job.title}
Job Description: {job.description}
Required Skills: {job.skills}
Location: {job.location}

Make sure the letter is professional, concise, and structured. Please keep it within 200 words if possible. 
Please surround all keywords that should be replaced later (such as job title, skills, location) with double curly braces like {{Job Title}}, {{Skills}}, {{Location}}, so they can be easily identified.

Respond only with the cover letter text.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        letter_text = response.choices[0].message.content.strip()
        pdf_buffer = generate_pdf(letter_text, title=f"Cover Letter for {job.title}")
        upload_result = upload_pdf_bytes_to_s3(pdf_buffer, filename=f"cover_letter_job_{job_id}_{datetime.datetime.utcnow().isoformat()}.pdf")

        if "url" not in upload_result:
            return jsonify({"error": upload_result.get("errors", "Upload failed")}), 500
        new_cl = CoverLetter(
            user_id=current_user.id,
            file_url=upload_result["url"],
            title=f"Cover Letter for {job.title}",
            extracted_text=letter_text
        )
        db.session.add(new_cl)
        db.session.commit()
        return jsonify({"message": "Cover letter generated", "cover_letter": new_cl.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_cover_letter_routes.route('/generate/profile', methods=['POST'])
@login_required
def generate_cover_letter_from_profile():
    profile = current_user.profile
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
    prompt = f"""
You are a professional career advisor. Write a general-purpose cover letter based on the following candidate profile:

Bio: {profile.bio}
Experience Years: {profile.experience_years}
Preferred Roles: {profile.preferred_roles}
Open To Roles: {profile.open_to_roles}
Achievements: {profile.achievements}
Location: {profile.location}

Make sure the letter is professional, concise, and structured. Please keep it within 200 words if possible. 
Please surround all keywords that should be replaced later (such as job title, skills, location) with double curly braces like {{Job Title}}, {{Skills}}, {{Location}}, so they can be easily identified.

Respond only with the cover letter text.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        letter_text = response.choices[0].message.content.strip()
        pdf_buffer = generate_pdf(letter_text, title="General Cover Letter")
        upload_result = upload_pdf_bytes_to_s3(
            pdf_buffer,
            filename=f"cover_letter_profile_{datetime.datetime.utcnow().isoformat()}.pdf"
        )

        if "url" not in upload_result:
            return jsonify({"error": upload_result.get("errors", "Upload failed")}), 500
        new_cl = CoverLetter(
            user_id=current_user.id,
            file_url=upload_result["url"],
            title="Cover Letter from Profile",
            extracted_text=letter_text
        )
        db.session.add(new_cl)
        db.session.commit()
        return jsonify({"message": "Cover letter generated", "cover_letter": new_cl.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
