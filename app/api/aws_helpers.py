import boto3
import botocore
import os
import uuid
from werkzeug.utils import secure_filename

BUCKET_NAME = os.environ.get("S3_BUCKET")
S3_LOCATION = f"https://{BUCKET_NAME}.s3.amazonaws.com/" if BUCKET_NAME else None
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif", "doc", "docx", "rtf", "wp", "txt"}

# Check if AWS is configured
AWS_CONFIGURED = bool(os.environ.get("S3_KEY") and os.environ.get("S3_SECRET") and BUCKET_NAME)

if AWS_CONFIGURED:
    s3 = boto3.client(
       "s3",
       aws_access_key_id=os.environ.get("S3_KEY"),
       aws_secret_access_key=os.environ.get("S3_SECRET")
    )
else:
    s3 = None
    # Create local upload directory if it doesn't exist
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)


def get_unique_filename(filename):
    ext = filename.rsplit(".", 1)[1].lower()
    unique_filename = uuid.uuid4().hex
    return f"{unique_filename}.{ext}"


def upload_file_to_s3(file, acl="public-read"):
    if not AWS_CONFIGURED:
        # Local storage fallback
        return upload_file_locally(file)
    
    unique_filename = get_unique_filename(file.filename)
    try:
        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            unique_filename, 
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print(f"AWS S3 upload error: {str(e)}")
        # Fallback to local storage if AWS fails
        return upload_file_locally(file)

    return {"url": f"{S3_LOCATION}{unique_filename}", "storage_type": "s3"} 


def upload_file_locally(file):
    """Fallback function for local file storage"""
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        unique_filename = get_unique_filename(filename)
        
        # Save file locally
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Return local URL
        return {"url": f"/uploads/{unique_filename}", "storage_type": "local"}
    except Exception as e:
        return {"errors": f"Local storage error: {str(e)}"}


def remove_file_from_s3(file_url):
    if not AWS_CONFIGURED or not s3:
        # Local storage cleanup
        return remove_file_locally(file_url)
    
    key = file_url.rsplit("/", 1)[1]
    print(f"Removing S3 file: {key}")
    try:
        s3.delete_object(
        Bucket=BUCKET_NAME,
        Key=key
        )
    except Exception as e:
        print(f"S3 delete error: {str(e)}")
        return {"errors": str(e)}
    return True


def remove_file_locally(file_url):
    """Remove file from local storage"""
    try:
        if file_url.startswith('/uploads/'):
            filename = file_url.replace('/uploads/', '')
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        return True
    except Exception as e:
        print(f"Local file delete error: {str(e)}")
        return {"errors": str(e)}