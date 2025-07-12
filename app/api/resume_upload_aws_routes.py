from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Resume
from .aws_helpers import upload_file_to_s3, remove_file_from_s3

resume_routes = Blueprint('resumes', __name__)

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "rtf", "wp", "txt"}

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@resume_routes.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to check authentication and upload capability"""
    return jsonify({
        "message": "Resume upload service is running",
        "authenticated": current_user.is_authenticated if current_user else False,
        "user_id": current_user.id if current_user and current_user.is_authenticated else None,
        "supported_file_types": list(ALLOWED_EXTENSIONS)
    }), 200

@resume_routes.route('', methods=['GET'])
@login_required
def get_user_resumes():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    return jsonify({"resumes": [resume.to_dict() for resume in resumes]}), 200

@resume_routes.route('', methods=['POST'])
@login_required
def upload_resume():
    try:
        print(f"Resume upload request from user: {current_user.id if current_user else 'None'}")
        
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

        # Check file size (10MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            return jsonify({"error": "File size must be less than 10MB"}), 400

        print(f"Uploading file: {file.filename} ({file_size} bytes)")
        
        upload_result = upload_file_to_s3(file)
        if 'errors' in upload_result:
            print(f"Upload failed: {upload_result['errors']}")
            return jsonify({"error": upload_result['errors']}), 500

        if 'url' not in upload_result:
            return jsonify({"error": "Upload failed - no URL returned"}), 500

        file_url = upload_result['url']
        storage_type = upload_result.get('storage_type', 'unknown')
        title = request.form.get('title', file.filename)

        print(f"File uploaded successfully: {file_url} (storage: {storage_type})")

        new_resume = Resume(user_id=current_user.id, file_url=file_url, title=title)
        db.session.add(new_resume)
        db.session.commit()

        response_data = {
            "message": "Resume uploaded successfully", 
            "resume": new_resume.to_dict(),
            "storage_type": storage_type
        }
        
        print(f"Resume saved to database with ID: {new_resume.id}")
        return jsonify(response_data), 201

    except Exception as e:
        print(f"Resume upload error: {str(e)}")
        db.session.rollback()
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@resume_routes.route('/<int:resume_id>', methods=['PUT'])
@login_required
def update_resume(resume_id):

    resume = Resume.query.get(resume_id)
    if not resume or resume.user_id != current_user.id:
        return jsonify({"error": "Resume not found or no permission"}), 404

    title = request.form.get('title')
    if title:
        resume.title = title

    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

        remove_file_from_s3(resume.file_url)

        upload_result = upload_file_to_s3(file)
        if 'errors' in upload_result:
            return jsonify({"error": upload_result['errors']}), 500

        if 'url' not in upload_result:
            return jsonify({"error": "Upload failed"}), 500

        resume.file_url = upload_result['url']

    db.session.commit()
    return jsonify({"message": "Resume updated", "resume": resume.to_dict()}), 200

@resume_routes.route('/<int:resume_id>', methods=['DELETE'])
@login_required
def delete_resume(resume_id):
    
    resume = Resume.query.get(resume_id)
    if not resume or resume.user_id != current_user.id:
        return jsonify({"error": "Resume not found or no permission"}), 404

    remove_file_from_s3(resume.file_url)

    db.session.delete(resume)
    db.session.commit()

    return jsonify({"message": "Resume deleted"}), 200

