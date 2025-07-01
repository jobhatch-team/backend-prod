import boto3
import botocore
import os
import uuid
from werkzeug.utils import secure_filename

BUCKET_NAME = os.environ.get("S3_BUCKET")
S3_LOCATION = f"https://{BUCKET_NAME}.s3.amazonaws.com/" if BUCKET_NAME else None
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif", "doc", "docx", "rtf", "wp", "txt"}

# Check if AWS credentials are available
def aws_configured():
    return bool(
        os.environ.get("S3_BUCKET") and 
        os.environ.get("S3_KEY") and 
        os.environ.get("S3_SECRET")
    )

def get_s3_client():
    if not aws_configured():
        return None
    
    try:
        return boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("S3_KEY"),
            aws_secret_access_key=os.environ.get("S3_SECRET")
        )
    except Exception as e:
        print(f"Failed to create S3 client: {e}")
        return None

def get_unique_filename(filename):
    ext = filename.rsplit(".", 1)[1].lower() if '.' in filename else 'pdf'
    unique_filename = uuid.uuid4().hex
    return f"{unique_filename}.{ext}"

def save_file_locally(file):
    """Fallback to save file locally when AWS is not configured"""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        unique_filename = get_unique_filename(file.filename)
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.seek(0)  # Reset file pointer
        file.save(file_path)
        
        # Return local URL
        return {"url": f"/uploads/{unique_filename}"}
    except Exception as e:
        return {"errors": f"Local file save failed: {str(e)}"}

def upload_file_to_s3(file, acl="public-read"):
    # Check if AWS is configured
    if not aws_configured():
        print("AWS not configured, falling back to local storage")
        return save_file_locally(file)
    
    s3 = get_s3_client()
    if not s3:
        print("S3 client failed, falling back to local storage")
        return save_file_locally(file)
    
    unique_filename = get_unique_filename(file.filename)
    
    try:
        # Reset file pointer to beginning
        file.seek(0)
        
        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            unique_filename, 
            ExtraArgs={
                "ContentType": file.content_type or "application/octet-stream",
                "ACL": acl
            }
        )
        
        return {"url": f"{S3_LOCATION}{unique_filename}"}
        
    except botocore.exceptions.NoCredentialsError:
        print("AWS credentials not found, falling back to local storage")
        return save_file_locally(file)
    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"AWS S3 error {error_code}: {e}")
        return save_file_locally(file)
    except Exception as e:
        print(f"Upload error: {e}")
        return {"errors": f"Upload failed: {str(e)}"}

def remove_file_from_s3(file_url):
    if not file_url:
        return True
        
    # Handle local files
    if file_url.startswith('/uploads/'):
        try:
            filename = file_url.replace('/uploads/', '')
            file_path = os.path.join(os.getcwd(), 'uploads', filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Local file deletion error: {e}")
            return {"errors": str(e)}
    
    # Handle S3 files
    if not aws_configured():
        return True
        
    s3 = get_s3_client()
    if not s3:
        return True
        
    key = file_url.rsplit("/", 1)[1]
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=key)
        return True
    except Exception as e:
        print(f"S3 deletion error: {e}")
        return {"errors": str(e)}