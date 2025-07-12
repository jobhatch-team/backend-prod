import boto3
import botocore
import os
import uuid
from io import BytesIO

BUCKET_NAME = os.environ.get("S3_BUCKET")
S3_LOCATION = f"https://{BUCKET_NAME}.s3.amazonaws.com/"
ALLOWED_EXTENSIONS = {"pdf","docx"}

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("S3_KEY"),
    aws_secret_access_key=os.environ.get("S3_SECRET")
)


def get_unique_filename(filename):
    ext = filename.rsplit(".", 1)[1].lower()
    unique_filename = uuid.uuid4().hex
    return f"{unique_filename}.{ext}"


def upload_file_to_s3(file, acl="public-read"):
    unique_filename = get_unique_filename(file.filename)

    content_type = file.content_type
    if not content_type or content_type == 'application/octet-stream':
        ext = unique_filename.rsplit(".", 1)[1].lower()
        if ext == 'doc':
            content_type = 'application/msword'
        elif ext == 'docx':
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif ext == 'pdf':
            content_type = 'application/pdf'
        else:
            content_type = 'application/octet-stream'

    try:
        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            unique_filename,
            ExtraArgs={
                "ContentType": content_type,
                # "ACL": acl
            }
        )
    except Exception as e:
        return {"errors": str(e)}

    return {"url": f"{S3_LOCATION}{unique_filename}"}


def upload_pdf_bytes_to_s3(pdf_buffer, filename, acl="public-read"):
    unique_filename = get_unique_filename(filename)

    try:
        s3.upload_fileobj(
            pdf_buffer,
            BUCKET_NAME,
            unique_filename,
            ExtraArgs={
                "ContentType": "application/pdf",
                # "ACL": acl
            }
        )
    except Exception as e:
        return {"errors": str(e)}

    return {"url": f"{S3_LOCATION}{unique_filename}"}



def remove_file_from_s3(file_url):
    key = file_url.rsplit("/", 1)[1]
    print(key)
    try:
        s3.delete_object(
            Bucket=BUCKET_NAME,
            Key=key
        )
    except Exception as e:
        return {"errors": str(e)}
    return True
