from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Resume
from .aws_helpers import upload_file_to_s3, remove_file_from_s3, aws_configured
import traceback

resume_routes = Blueprint('resumes', __name__)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif", "doc", "docx", "rtf", "wp", "txt"}

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@resume_routes.route('', methods=['GET'])
@login_required
def get_user_resumes():
    try:
        resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
        return jsonify({"resumes": [resume.to_dict() for resume in resumes]}), 200
    except Exception as e:
        print(f"Error getting resumes: {e}")
        return jsonify({"error": "Failed to retrieve resumes"}), 500

@resume_routes.route('', methods=['POST'])
@login_required
def upload_resume():
    try:
        print(f"Resume upload request from user {current_user.id}")
        
        # Check if file is in request
        if 'file' not in request.files:
            print("No file part in request")
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        print(f"File received: {file.filename}")
        
        if file.filename == '':
            print("No file selected")
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            print(f"File type not allowed: {file.filename}")
            return jsonify({"error": f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

        # Get title from form data
        title = request.form.get('title', file.filename)
        print(f"Upload title: {title}")
        
        # Check AWS configuration status
        if aws_configured():
            print("AWS configured, attempting S3 upload")
        else:
            print("AWS not configured, will use local storage fallback")

        # Upload file
        upload_result = upload_file_to_s3(file)
        print(f"Upload result: {upload_result}")
        
        if 'url' not in upload_result:
            error_msg = upload_result.get('errors', 'Upload failed')
            print(f"Upload failed: {error_msg}")
            return jsonify({"error": error_msg}), 500

        file_url = upload_result['url']
        print(f"File uploaded to: {file_url}")

        # Save to database
        new_resume = Resume(user_id=current_user.id, file_url=file_url, title=title)
        db.session.add(new_resume)
        db.session.commit()
        
        print(f"Resume saved to database with ID: {new_resume.id}")

        return jsonify({
            "message": "Resume uploaded successfully", 
            "resume": new_resume.to_dict(),
            "storage_type": "s3" if aws_configured() else "local"
        }), 201

    except Exception as e:
        print(f"Unexpected error during upload: {e}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@resume_routes.route('/<int:resume_id>', methods=['PUT'])
@login_required
def update_resume(resume_id):
    try:
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

            # Remove old file
            if resume.file_url:
                remove_file_from_s3(resume.file_url)

            # Upload new file
            upload_result = upload_file_to_s3(file)
            if 'url' not in upload_result:
                return jsonify({"error": upload_result.get('errors', 'Upload failed')}), 500

            resume.file_url = upload_result['url']

        db.session.commit()
        return jsonify({"message": "Resume updated", "resume": resume.to_dict()}), 200
        
    except Exception as e:
        print(f"Error updating resume: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to update resume"}), 500

@resume_routes.route('/<int:resume_id>', methods=['DELETE'])
@login_required
def delete_resume(resume_id):
    try:
        resume = Resume.query.get(resume_id)
        if not resume or resume.user_id != current_user.id:
            return jsonify({"error": "Resume not found or no permission"}), 404

        # Remove file
        if resume.file_url:
            remove_file_from_s3(resume.file_url)

        # Remove from database
        db.session.delete(resume)
        db.session.commit()

        return jsonify({"message": "Resume deleted"}), 200
        
    except Exception as e:
        print(f"Error deleting resume: {e}")
        db.session.rollback()
        return jsonify({"error": "Failed to delete resume"}), 500

@resume_routes.route('/test', methods=['GET'])
def test_upload_config():
    """Test endpoint to check upload configuration"""
    return jsonify({
        "aws_configured": aws_configured(),
        "allowed_extensions": list(ALLOWED_EXTENSIONS),
        "storage_type": "s3" if aws_configured() else "local"
    }), 200

