# from flask import Blueprint, request, jsonify
# from flask_login import login_required, current_user
# from app.models import db, Resume
# from .aws_helpers import upload_file_to_s3, remove_file_from_s3

# resume_routes = Blueprint('resumes', __name__)

# ALLOWED_EXTENSIONS = {"pdf", "docx"}

# def allowed_file(filename):
#     """Check if the file has an allowed extension"""
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @resume_routes.route('/all', methods=['GET'])
# @login_required
# def get_all_resumes():
#     resumes = Resume.query.order_by(Resume.uploaded_at.desc()).all()
#     return jsonify({"resumes": [resume.to_dict() for resume in resumes]}), 200


# @resume_routes.route('/<int:resume_id>', methods=['GET'])
# @login_required
# def get_resume_by_id(resume_id):
#     resume = Resume.query.get(resume_id)
#     if not resume or resume.user_id != current_user.id:
#         return jsonify({"error": "Resume not found or no permission"}), 404
#     return jsonify({"resume": resume.to_dict()}), 200


# @resume_routes.route('', methods=['GET'])
# @login_required
# def get_user_resumes():
#     resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
#     return jsonify({"resumes": [resume.to_dict() for resume in resumes]}), 200

# @resume_routes.route('', methods=['POST'])
# @login_required
# def upload_resume():

#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     if not allowed_file(file.filename):
#         return jsonify({"error": "File type not allowed"}), 400

#     upload_result = upload_file_to_s3(file)
#     if 'url' not in upload_result:
#         return jsonify({"error": upload_result.get('errors', 'Upload failed')}), 500

#     file_url = upload_result['url']
#     title = request.form.get('title')

#     new_resume = Resume(user_id=current_user.id, file_url=file_url, title=title)
#     db.session.add(new_resume)
#     db.session.commit()

#     return jsonify({"message": "Resume uploaded", "resume": new_resume.to_dict()}), 201

# @resume_routes.route('/<int:resume_id>', methods=['PUT'])
# @login_required
# def update_resume(resume_id):

#     resume = Resume.query.get(resume_id)
#     if not resume or resume.user_id != current_user.id:
#         return jsonify({"error": "Resume not found or no permission"}), 404

#     title = request.form.get('title')
#     if title:
#         resume.title = title

#     if 'file' in request.files:
#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({"error": "No selected file"}), 400
#         if not allowed_file(file.filename):
#             return jsonify({"error": "File type not allowed"}), 400

#         remove_file_from_s3(resume.file_url)

#         upload_result = upload_file_to_s3(file)
#         if 'url' not in upload_result:
#             return jsonify({"error": upload_result.get('errors', 'Upload failed')}), 500

#         resume.file_url = upload_result['url']

#     db.session.commit()
#     return jsonify({"message": "Resume updated", "resume": resume.to_dict()}), 200

# @resume_routes.route('/<int:resume_id>', methods=['DELETE'])
# @login_required
# def delete_resume(resume_id):
    
#     resume = Resume.query.get(resume_id)
#     if not resume or resume.user_id != current_user.id:
#         return jsonify({"error": "Resume not found or no permission"}), 404

#     remove_file_from_s3(resume.file_url)

#     db.session.delete(resume)
#     db.session.commit()

#     return jsonify({"message": "Resume deleted"}), 200


from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Resume
from .aws_helpers import upload_file_to_s3, remove_file_from_s3

resume_routes = Blueprint('resumes', __name__)

ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_RESUMES_PER_USER = 10
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_size_within_limit(file):
    """Check if the uploaded file size is within the allowed limit"""
    file.seek(0, 2)  # Move pointer to the end of the file
    size = file.tell()
    file.seek(0)  # Reset pointer to the beginning
    return size <= MAX_FILE_SIZE

@resume_routes.route('/all', methods=['GET'])
@login_required
def get_all_resumes():
    resumes = Resume.query.order_by(Resume.uploaded_at.desc()).all()
    return jsonify({"resumes": [resume.to_dict() for resume in resumes]}), 200


@resume_routes.route('/<int:resume_id>', methods=['GET'])
@login_required
def get_resume_by_id(resume_id):
    resume = Resume.query.get(resume_id)
    if not resume or resume.user_id != current_user.id:
        return jsonify({"error": "Resume not found or no permission"}), 404
    return jsonify({"resume": resume.to_dict()}), 200


@resume_routes.route('', methods=['GET'])
@login_required
def get_user_resumes():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.uploaded_at.desc()).all()
    return jsonify({"resumes": [resume.to_dict() for resume in resumes]}), 200

@resume_routes.route('', methods=['POST'])
@login_required
def upload_resume():
    # Check current user resume count limit
    existing_count = Resume.query.filter_by(user_id=current_user.id).count()
    if existing_count >= MAX_RESUMES_PER_USER:
        return jsonify({"error": f"You can only upload up to {MAX_RESUMES_PER_USER} resumes."}), 400

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    if not file_size_within_limit(file):
        return jsonify({"error": f"File size must be less than {MAX_FILE_SIZE // (1024 * 1024)}MB"}), 400

    upload_result = upload_file_to_s3(file)
    if 'url' not in upload_result:
        return jsonify({"error": upload_result.get('errors', 'Upload failed')}), 500

    file_url = upload_result['url']
    title = request.form.get('title')

    new_resume = Resume(user_id=current_user.id, file_url=file_url, title=title)
    db.session.add(new_resume)
    db.session.commit()

    return jsonify({"message": "Resume uploaded", "resume": new_resume.to_dict()}), 201

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
            return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        if not file_size_within_limit(file):
            return jsonify({"error": f"File size must be less than {MAX_FILE_SIZE // (1024 * 1024)}MB"}), 400

        remove_file_from_s3(resume.file_url)

        upload_result = upload_file_to_s3(file)
        if 'url' not in upload_result:
            return jsonify({"error": upload_result.get('errors', 'Upload failed')}), 500

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


