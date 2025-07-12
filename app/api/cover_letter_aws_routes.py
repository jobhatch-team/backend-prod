# from flask import Blueprint, request, jsonify
# from flask_login import login_required, current_user
# from app.models import db, CoverLetter
# from .aws_helpers import upload_file_to_s3, remove_file_from_s3

# cover_letter_routes = Blueprint('cover_letters', __name__)

# ALLOWED_EXTENSIONS = {"pdf", "docx"}

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @cover_letter_routes.route('/all', methods=['GET'])
# @login_required
# def get_all_cover_letters():
#     cover_letters = CoverLetter.query.order_by(CoverLetter.uploaded_at.desc()).all()
#     return jsonify({"cover_letters": [cl.to_dict() for cl in cover_letters]}), 200

# @cover_letter_routes.route('', methods=['GET'])
# @login_required
# def get_user_cover_letters():
#     cover_letters = CoverLetter.query.filter_by(user_id=current_user.id).order_by(CoverLetter.uploaded_at.desc()).all()
#     return jsonify({"cover_letters": [cl.to_dict() for cl in cover_letters]}), 200

# @cover_letter_routes.route('/<int:cover_letter_id>', methods=['GET'])
# @login_required
# def get_cover_letter_by_id(cover_letter_id):
#     cl = CoverLetter.query.get(cover_letter_id)
#     if not cl or cl.user_id != current_user.id:
#         return jsonify({"error": "Cover letter not found or no permission"}), 404
#     return jsonify({"cover_letter": cl.to_dict()}), 200



# @cover_letter_routes.route('', methods=['POST'])
# @login_required
# def upload_cover_letter():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     if not allowed_file(file.filename):
#         return jsonify({"error": "File type not allowed. Only PDF and DOCX are supported."}), 400

#     upload_result = upload_file_to_s3(file)
#     if 'url' not in upload_result:
#         return jsonify({"error": upload_result.get('errors', 'Upload failed')}), 500

#     file_url = upload_result['url']
#     title = request.form.get('title')

#     new_cover_letter = CoverLetter(
#         user_id=current_user.id,
#         file_url=file_url,
#         title=title
#     )

#     db.session.add(new_cover_letter)
#     db.session.commit()

#     return jsonify({"message": "Cover letter uploaded", "cover_letter": new_cover_letter.to_dict()}), 201


# @cover_letter_routes.route('/<int:cover_letter_id>', methods=['PUT'])
# @login_required
# def update_cover_letter(cover_letter_id):
#     cl = CoverLetter.query.get(cover_letter_id)

#     if not cl or cl.user_id != current_user.id:
#         return jsonify({"error": "Cover letter not found or no permission"}), 404

#     title = request.form.get('title')
#     if title:
#         cl.title = title

#     if 'file' in request.files:
#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({"error": "No selected file"}), 400
#         if not allowed_file(file.filename):
#             return jsonify({"error": "File type not allowed. Only PDF and DOCX are supported."}), 400

#         remove_file_from_s3(cl.file_url)
#         upload_result = upload_file_to_s3(file)
#         if 'url' not in upload_result:
#             return jsonify({"error": upload_result.get('errors', 'Upload failed')}), 500

#         cl.file_url = upload_result['url']

#     db.session.commit()
#     return jsonify({"message": "Cover letter updated", "cover_letter": cl.to_dict()}), 200


# @cover_letter_routes.route('/<int:cover_letter_id>', methods=['DELETE'])
# @login_required
# def delete_cover_letter(cover_letter_id):
#     cl = CoverLetter.query.get(cover_letter_id)

#     if not cl or cl.user_id != current_user.id:
#         return jsonify({"error": "Cover letter not found or no permission"}), 404

#     remove_file_from_s3(cl.file_url)

#     db.session.delete(cl)
#     db.session.commit()

#     return jsonify({"message": "Cover letter deleted"}), 200


from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, CoverLetter
from .aws_helpers import upload_file_to_s3, remove_file_from_s3

cover_letter_routes = Blueprint('cover_letters', __name__)

ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_COVER_LETTERS_PER_USER = 10
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_size_within_limit(file):
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    return size <= MAX_FILE_SIZE

@cover_letter_routes.route('/all', methods=['GET'])
@login_required
def get_all_cover_letters():
    cover_letters = CoverLetter.query.order_by(CoverLetter.uploaded_at.desc()).all()
    return jsonify({"cover_letters": [cl.to_dict() for cl in cover_letters]}), 200

@cover_letter_routes.route('', methods=['GET'])
@login_required
def get_user_cover_letters():
    cover_letters = CoverLetter.query.filter_by(user_id=current_user.id).order_by(CoverLetter.uploaded_at.desc()).all()
    return jsonify({"cover_letters": [cl.to_dict() for cl in cover_letters]}), 200

@cover_letter_routes.route('/<int:cover_letter_id>', methods=['GET'])
@login_required
def get_cover_letter_by_id(cover_letter_id):
    cl = CoverLetter.query.get(cover_letter_id)
    if not cl or cl.user_id != current_user.id:
        return jsonify({"error": "Cover letter not found or no permission"}), 404
    return jsonify({"cover_letter": cl.to_dict()}), 200

@cover_letter_routes.route('', methods=['POST'])
@login_required
def upload_cover_letter():
    existing_count = CoverLetter.query.filter_by(user_id=current_user.id).count()
    if existing_count >= MAX_COVER_LETTERS_PER_USER:
        return jsonify({"error": f"You can only upload up to {MAX_COVER_LETTERS_PER_USER} cover letters."}), 400

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Only PDF and DOCX are supported."}), 400

    if not file_size_within_limit(file):
        return jsonify({"error": f"File size must be less than {MAX_FILE_SIZE // (1024 * 1024)}MB"}), 400

    upload_result = upload_file_to_s3(file)
    if 'url' not in upload_result:
        return jsonify({"error": upload_result.get('errors', 'Upload failed')}), 500

    file_url = upload_result['url']
    title = request.form.get('title')

    new_cover_letter = CoverLetter(
        user_id=current_user.id,
        file_url=file_url,
        title=title
    )

    db.session.add(new_cover_letter)
    db.session.commit()

    return jsonify({"message": "Cover letter uploaded", "cover_letter": new_cover_letter.to_dict()}), 201

@cover_letter_routes.route('/<int:cover_letter_id>', methods=['PUT'])
@login_required
def update_cover_letter(cover_letter_id):
    cl = CoverLetter.query.get(cover_letter_id)

    if not cl or cl.user_id != current_user.id:
        return jsonify({"error": "Cover letter not found or no permission"}), 404

    title = request.form.get('title')
    if title:
        cl.title = title

    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed. Only PDF and DOCX are supported."}), 400
        if not file_size_within_limit(file):
            return jsonify({"error": f"File size must be less than {MAX_FILE_SIZE // (1024 * 1024)}MB"}), 400

        remove_file_from_s3(cl.file_url)
        upload_result = upload_file_to_s3(file)
        if 'url' not in upload_result:
            return jsonify({"error": upload_result.get('errors', 'Upload failed')}), 500

        cl.file_url = upload_result['url']

    db.session.commit()
    return jsonify({"message": "Cover letter updated", "cover_letter": cl.to_dict()}), 200

@cover_letter_routes.route('/<int:cover_letter_id>', methods=['DELETE'])
@login_required
def delete_cover_letter(cover_letter_id):
    cl = CoverLetter.query.get(cover_letter_id)

    if not cl or cl.user_id != current_user.id:
        return jsonify({"error": "Cover letter not found or no permission"}), 404

    remove_file_from_s3(cl.file_url)

    db.session.delete(cl)
    db.session.commit()

    return jsonify({"message": "Cover letter deleted"}), 200
