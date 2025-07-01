from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Resume, ResumeScore, ResumeJobMatch, Job, db
from openai import OpenAI
import os
import fitz
import re
import json
import random

ai_routes = Blueprint('ai', __name__)

# Initialize OpenAI client only when needed
def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your-openai-api-key-here':
        return None  # Return None if not configured
    return OpenAI(api_key=api_key)

# Chat with AI (login required)
@ai_routes.route('/chat', methods=['POST'])
@login_required
def chat_with_ai():
    data = request.get_json()
    messages = data.get('messages')

    if not messages or not isinstance(messages, list):
        return jsonify({'error': 'Invalid or missing messages'}), 400

    try:
        client = get_openai_client()
        if not client:
            return jsonify({'error': 'OpenAI API not configured'}), 500
            
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
        )
        ai_reply = response.choices[0].message.content
        return jsonify({'reply': ai_reply}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_text_from_local_pdf(file_path, max_pages=5):
    """Extract text from local PDF file"""
    try:
        text = ""
        print(f"Attempting to extract text from: {file_path}")
        
        with fitz.open(file_path) as doc:
            print(f"PDF has {len(doc)} pages")
            for page_num, page in enumerate(doc[:max_pages]):
                page_text = page.get_text()
                text += page_text + "\n"
                print(f"Page {page_num + 1}: {len(page_text)} characters extracted")
        
        print(f"Total text extracted: {len(text)} characters")
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def get_pdf_text_from_url(file_url):
    """Get PDF text from either local storage or S3"""
    try:
        print(f"Getting PDF text from URL: {file_url}")
        
        # Check if it's a local file
        if file_url.startswith('/uploads/'):
            # Local file
            filename = file_url.replace('/uploads/', '')
            file_path = os.path.join(os.getcwd(), 'uploads', filename)
            print(f"Looking for local file at: {file_path}")
            
            if os.path.exists(file_path):
                print(f"File exists, size: {os.path.getsize(file_path)} bytes")
                return extract_text_from_local_pdf(file_path)
            else:
                print(f"Local file not found: {file_path}")
                return None
        else:
            # Could be S3 or other - for now just return None
            print(f"Non-local file URL not supported: {file_url}")
            return None
    except Exception as e:
        print(f"Error getting PDF text: {e}")
        return None

def extract_name_from_resume(text):
    """Extract the candidate's name from resume text"""
    if not text:
        return "there"
    
    lines = text.strip().split('\n')
    
    # Common patterns for names at the beginning of resumes
    import re
    
    # Look in first few lines for name patterns
    for line in lines[:5]:
        line = line.strip()
        if not line:
            continue
            
        # Skip common headers/sections
        if any(header in line.lower() for header in ['resume', 'cv', 'curriculum', 'contact', 'email', 'phone', 'address']):
            continue
            
        # Look for name patterns (typically 2-4 words, capitalized)
        # Handle cases like "SIMON (JIAHE) TIAN" or "John Smith"
        # Pattern: Handles all caps, parentheses, and mixed case
        name_pattern = r'^([A-Z]+(?:\s*\([A-Z]+\))?\s+[A-Z]+(?:\s+[A-Z]+)?)\s*$'
        match = re.match(name_pattern, line)
        
        if match:
            full_name = match.group(1)
            # Extract first name
            first_name = full_name.split()[0]
            # Remove parentheses if present (like "SIMON (JIAHE)")
            if '(' in first_name:
                first_name = first_name.split('(')[0].strip()
            return first_name.title()
            
        # Also try mixed case pattern
        mixed_pattern = r'^([A-Z][a-z]+(?:\s+\([A-Z][a-z]+\))?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*$'
        match = re.match(mixed_pattern, line)
        
        if match:
            full_name = match.group(1)
            # Extract first name
            first_name = full_name.split()[0]
            # Remove parentheses if present
            if '(' in first_name:
                first_name = first_name.split('(')[0].strip()
            return first_name.title()
    
    # Fallback: look for capitalized words that might be names
    for line in lines[:3]:
        words = line.strip().split()
        if len(words) >= 2:
            # Check if first two words are capitalized and look like names
            if all(word[0].isupper() and word[1:].islower() for word in words[:2] if word.isalpha()):
                first_name = words[0]
                if '(' in first_name:
                    first_name = first_name.split('(')[0].strip()
                return first_name.title()
    
    return "there"  # Default greeting

def analyze_resume_text(text):
    """Analyze resume text without OpenAI - basic text processing"""
    if not text or len(text.strip()) < 100:
        return generate_basic_mock_analysis()
    
    text_lower = text.lower()
    words = text_lower.split()
    
    # Extract name for personalization
    candidate_name = extract_name_from_resume(text)
    
    # Calculate scores based on text analysis
    scores = {}
    
    # Skills score - look for technical terms, programming languages, tools
    skill_keywords = [
        'python', 'java', 'javascript', 'react', 'node', 'sql', 'database',
        'machine learning', 'ai', 'data science', 'analytics', 'aws', 'cloud',
        'docker', 'kubernetes', 'git', 'agile', 'scrum', 'tensorflow', 'pytorch',
        'html', 'css', 'mongodb', 'postgresql', 'api', 'rest', 'microservices',
        'c++', 'c#', 'golang', 'rust', 'swift', 'kotlin', 'vue', 'angular'
    ]
    
    skill_count = sum(1 for skill in skill_keywords if skill in text_lower)
    scores['score_skills'] = min(10, 3 + (skill_count * 0.3))
    
    # Experience score - look for years, companies, positions
    experience_indicators = [
        'years', 'year', 'experience', 'worked', 'developed', 'managed',
        'led', 'created', 'implemented', 'designed', 'built', 'architect',
        'engineer', 'developer', 'analyst', 'consultant', 'specialist'
    ]
    
    experience_count = sum(1 for exp in experience_indicators if exp in text_lower)
    # Look for year patterns (2020, 2021, etc.)
    year_matches = len(re.findall(r'20[0-9]{2}', text))
    
    scores['score_experience'] = min(10, 4 + (experience_count * 0.1) + (year_matches * 0.2))
    
    # Format score - based on structure, length, sections
    format_indicators = [
        'education', 'experience', 'skills', 'projects', 'achievements',
        'contact', 'summary', 'objective', 'certifications', 'awards'
    ]
    
    format_count = sum(1 for fmt in format_indicators if fmt in text_lower)
    text_length_score = min(3, len(text) / 1000)  # Bonus for longer, detailed resumes
    
    scores['score_format'] = min(10, 4 + format_count * 0.4 + text_length_score)
    
    # Overall score - average with some weighting
    scores['score_overall'] = (scores['score_skills'] * 0.4 + 
                              scores['score_experience'] * 0.4 + 
                              scores['score_format'] * 0.2)
    
    # Generate personalized feedback based on content
    strengths = []
    weaknesses = []
    suggestions = []
    
    # Analyze specific skills and experience
    found_skills = [skill for skill in skill_keywords if skill in text_lower]
    
    if skill_count > 8:
        strengths.append(f"You showcase an impressive technical toolkit with expertise in {', '.join(found_skills[:5])}, demonstrating versatility across multiple domains")
    elif skill_count > 5:
        strengths.append(f"Your technical foundation is solid, featuring key skills like {', '.join(found_skills[:3])} that are highly relevant in today's market")
    else:
        weaknesses.append("Your technical skills section could be more comprehensive")
        suggestions.append("Expand your skills section with specific technologies, programming languages, and tools you've used")
    
    if year_matches > 3:
        strengths.append("You've maintained excellent chronological clarity with well-documented career progression that's easy to follow")
    else:
        weaknesses.append("Your work timeline needs clearer date formatting")
        suggestions.append("Include specific start and end dates (month/year) for all positions to show career progression")
    
    if 'project' in text_lower or 'achievement' in text_lower:
        strengths.append("You've effectively highlighted concrete projects and achievements that demonstrate real-world impact")
    else:
        suggestions.append("Add 2-3 specific projects with quantifiable results to showcase your practical experience")
    
    if format_count > 5:
        strengths.append("Your resume structure is professional and comprehensive, covering all essential sections")
    else:
        weaknesses.append("Your resume organization could be more structured")
        suggestions.append("Reorganize into clear sections: Summary, Experience, Skills, Projects, and Education")
    
    # Check for education
    if any(edu in text_lower for edu in ['degree', 'university', 'college', 'bachelor', 'master', 'phd']):
        strengths.append("Your educational background provides a strong foundation for your career goals")
    else:
        suggestions.append("Include your educational background with relevant coursework and achievements")
    
    return {
        "score_overall": round(scores['score_overall'], 1),
        "score_format": round(scores['score_format'], 1),
        "score_skills": round(scores['score_skills'], 1),
        "score_experience": round(scores['score_experience'], 1),
        "candidate_name": candidate_name,
        "strengths": ". ".join(strengths) if strengths else f"You have a solid professional background with relevant experience that positions you well for your target roles",
        "weaknesses": ". ".join(weaknesses) if weaknesses else "Your resume could benefit from enhanced presentation and more detailed descriptions",
        "suggestions": ". ".join(suggestions) if suggestions else "Focus on quantifying your achievements and highlighting specific results you've delivered"
    }

def generate_basic_mock_analysis():
    """Generate basic mock analysis when no text is available"""
    return {
        "score_overall": 5.5,
        "score_format": 6.0,
        "score_skills": 5.0,
        "score_experience": 5.5,
        "candidate_name": "there",
        "strengths": "We couldn't fully analyze your resume content. Please ensure your PDF is readable and contains text.",
        "weaknesses": "Your resume content couldn't be extracted for detailed analysis.",
        "suggestions": "Try uploading a clearer PDF or ensure your resume contains text (not just images)."
    }

def generate_job_matches_from_text(text):
    """Generate job matches based on actual resume content"""
    if not text:
        return generate_basic_job_matches()
    
    text_lower = text.lower()
    
    # Define job categories with their keywords and base info
    job_categories = {
        'ml_engineer': {
            'keywords': ['machine learning', 'ml', 'ai', 'tensorflow', 'pytorch', 'data science', 'python', 'neural'],
            'title': 'ML Engineer',
            'company': 'TechCorp',
            'description': 'Looking for an ML engineer with strong Python and machine learning experience.',
            'requirements': ['Python', 'Machine Learning', 'TensorFlow', 'Data Science']
        },
        'software_engineer': {
            'keywords': ['software', 'programming', 'development', 'code', 'engineer', 'java', 'python', 'javascript'],
            'title': 'Software Engineer',
            'company': 'DevSolutions',
            'description': 'Software engineer position for building scalable applications.',
            'requirements': ['Programming', 'Software Development', 'Problem Solving', 'Team Work']
        },
        'data_scientist': {
            'keywords': ['data', 'analytics', 'statistics', 'sql', 'analysis', 'scientist'],
            'title': 'Data Scientist',
            'company': 'DataInsights',
            'description': 'Data scientist role focusing on predictive analytics and insights.',
            'requirements': ['Python', 'Statistics', 'SQL', 'Machine Learning']
        },
        'web_developer': {
            'keywords': ['web', 'html', 'css', 'javascript', 'react', 'frontend', 'backend', 'full stack'],
            'title': 'Full Stack Developer',
            'company': 'WebSolutions',
            'description': 'Full stack developer needed for modern web applications.',
            'requirements': ['React', 'Node.js', 'JavaScript', 'MongoDB']
        },
        'cybersecurity': {
            'keywords': ['security', 'cyber', 'network', 'penetration', 'incident', 'vulnerability'],
            'title': 'Cybersecurity Engineer',
            'company': 'SecureFlow',
            'description': 'Seeking a cybersecurity professional with network security expertise.',
            'requirements': ['Network Security', 'Penetration Testing', 'Incident Response']
        }
    }
    
    matches = []
    
    for job_key, job_info in job_categories.items():
        # Calculate match score based on keyword presence
        keyword_matches = sum(1 for keyword in job_info['keywords'] if keyword in text_lower)
        total_keywords = len(job_info['keywords'])
        
        # Base score with some randomization for realism
        base_score = (keyword_matches / total_keywords) * 0.8
        random_factor = random.uniform(0.1, 0.3)
        match_score = min(0.95, base_score + random_factor)
        
        matches.append({
            'title': job_info['title'],
            'company': job_info['company'],
            'match_score': round(match_score, 2),
            'description': job_info['description'],
            'requirements': job_info['requirements']
        })
    
    # Sort by match score and return top 4
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches[:4]

def generate_basic_job_matches():
    """Generate basic job matches when no text is available"""
    return [
        {
            "title": "Software Engineer",
            "company": "TechCorp",
            "match_score": 0.45,
            "description": "General software engineering position.",
            "requirements": ["Programming", "Problem Solving", "Team Work"]
        },
        {
            "title": "Data Analyst",
            "company": "DataCorp",
            "match_score": 0.35,
            "description": "Entry-level data analysis role.",
            "requirements": ["Excel", "SQL", "Analytics"]
        }
    ]

@ai_routes.route('/resumes/<int:resume_id>/analyze', methods=['POST'])
@login_required
def analyze_resume(resume_id):
    try:
        print(f"Starting analysis for resume {resume_id}")
        
        resume = Resume.query.get(resume_id)
        if not resume or resume.user_id != current_user.id:
            return jsonify({"error": "Resume not found or permission denied"}), 404

        print(f"Resume file URL: {resume.file_url}")

        # Try to extract text from PDF
        text = get_pdf_text_from_url(resume.file_url)
        
        if text and len(text.strip()) > 50:
            print(f"Successfully extracted {len(text)} characters from resume")
            print(f"First 200 characters: {text[:200]}")
        else:
            print("No text extracted or text too short")
        
        # Check if OpenAI is configured
        client = get_openai_client()
        
        if client and text and len(text.strip()) > 100:
            # Use real OpenAI analysis
            print("Using OpenAI for analysis")
            analysis_data = analyze_with_openai(client, text)
            ai_model = "gpt-4"
        elif text and len(text.strip()) > 50:
            # Use text-based analysis without OpenAI
            print("Using text-based analysis (OpenAI not available)")
            analysis_data = analyze_resume_text(text)
            ai_model = "text-analysis"
        else:
            # Use basic mock data
            print("Using basic analysis (no text extracted)")
            analysis_data = generate_basic_mock_analysis()
            ai_model = "mock"

        print(f"Analysis results: {analysis_data}")

        # Save analysis to database
        new_score = ResumeScore(
            resume_id=resume.id,
            ai_model=ai_model,
            score_overall=analysis_data.get("score_overall"),
            score_format=analysis_data.get("score_format"),
            score_skills=analysis_data.get("score_skills"),
            score_experience=analysis_data.get("score_experience"),
            strengths=analysis_data.get("strengths"),
            weaknesses=analysis_data.get("weaknesses"),
            suggestions=analysis_data.get("suggestions"),
        )

        db.session.add(new_score)

        # Generate job matches based on resume content
        if text and len(text.strip()) > 50:
            job_matches = generate_job_matches_from_text(text)
        else:
            job_matches = generate_basic_job_matches()

        print(f"Generated {len(job_matches)} job matches")

        db.session.commit()

        return jsonify({
            "analysis": analysis_data,
            "score_id": new_score.id,
            "job_matches": job_matches,
            "text_extracted": bool(text and len(text.strip()) > 50),
            "analysis_method": ai_model
        }), 200

    except Exception as e:
        print(f"Analysis error: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

def analyze_with_openai(client, text):
    """Perform analysis using OpenAI"""
    
    # Extract candidate name first
    candidate_name = extract_name_from_resume(text)
    
    prompt = f"""
You are an expert HR professional and AI resume analyst.

Please analyze the following resume text and provide a JSON response with the following fields:
- score_overall: float between 0 and 10 (overall quality)
- score_format: float between 0 and 10 (formatting and structure)
- score_skills: float between 0 and 10 (technical and relevant skills)
- score_experience: float between 0 and 10 (work experience quality)
- candidate_name: "{candidate_name}" (keep this exact value)
- strengths: detailed description of the candidate's main strengths (2-3 sentences, use second-person "you/your")
- weaknesses: constructive description of areas for improvement (2-3 sentences, use second-person "you/your")
- suggestions: concrete, actionable suggestions for improvement (2-3 sentences, use second-person "you/your")

Important instructions:
- Write ALL feedback in SECOND-PERSON (use "you", "your", "you've", etc.)
- Be personal, concise, descriptive, and informative
- Be specific about technologies, tools, and experiences mentioned
- Provide constructive, professional feedback directly to the candidate
- Base analysis on actual content provided
- Make it feel like personal coaching advice

Example style: "You demonstrate strong Python skills..." instead of "The candidate has Python skills..."

Respond ONLY with valid JSON.

Resume text:
{text[:3000]}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume analyst. Analyze resumes and provide detailed feedback in clear English. Return only valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        analysis_json_str = response.choices[0].message.content
        
        # Clean up the response to ensure it's valid JSON
        if '```json' in analysis_json_str:
            analysis_json_str = analysis_json_str.split('```json')[1].split('```')[0]
        elif '```' in analysis_json_str:
            analysis_json_str = analysis_json_str.split('```')[1]
        
        analysis_data = json.loads(analysis_json_str)
        
        # Ensure candidate_name is properly set
        if not analysis_data.get("candidate_name") or analysis_data["candidate_name"] == "":
            analysis_data["candidate_name"] = candidate_name
            
        return analysis_data
        
    except Exception as e:
        print(f"OpenAI analysis error: {e}")
        # Fall back to text analysis if OpenAI fails
        return analyze_resume_text(text)

@ai_routes.route('/resumes/<int:resume_id>/analysis', methods=['GET'])
@login_required
def get_resume_analysis(resume_id):
    """Get existing analysis for a resume"""
    try:
        resume = Resume.query.get(resume_id)
        if not resume or resume.user_id != current_user.id:
            return jsonify({"error": "Resume not found or permission denied"}), 404

        # Get the latest analysis
        latest_score = ResumeScore.query.filter_by(resume_id=resume_id).order_by(ResumeScore.evaluated_at.desc()).first()
        
        if not latest_score:
            return jsonify({"error": "No analysis found"}), 404

        # Get job matches based on the resume
        text = get_pdf_text_from_url(resume.file_url)
        if text and len(text.strip()) > 50:
            job_matches = generate_job_matches_from_text(text)
        else:
            job_matches = generate_basic_job_matches()

        return jsonify({
            "analysis": latest_score.to_dict(),
            "job_matches": job_matches
        }), 200

    except Exception as e:
        print(f"Error getting analysis: {e}")
        return jsonify({"error": str(e)}), 500
