# backend/app.py
import boto3
import os
from flask import Flask, request, jsonify, Response
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Allow requests from the frontend (running on a different origin)
CORS(app)

# S3 Client Configuration from environment variables
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')


def get_s3_objects_logic(filter_term=None, sort_by='Key', sort_order='asc'):
    """Helper function to list, filter, and sort S3 objects."""
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
        files = response.get('Contents', [])
        if not files:
            return []

        if filter_term:
            files = [f for f in files if filter_term.lower()
                     in f['Key'].lower()]

        # Convert LastModified to string for JSON serialization
        for f in files:
            f['LastModified'] = f['LastModified'].isoformat()

        reverse = sort_order == 'desc'
        if sort_by == 'Size':
            files.sort(key=lambda x: x['Size'], reverse=reverse)
        elif sort_by == 'LastModified':
            files.sort(key=lambda x: x['LastModified'], reverse=reverse)
        else:
            files.sort(key=lambda x: x['Key'].lower(), reverse=reverse)

        return files
    except ClientError as e:
        app.logger.error(f"Error listing S3 objects: {e}")
        return None  # Return None to indicate an error occurred


@app.route('/api/files', methods=['GET'])
def list_files():
    if not S3_BUCKET_NAME:
        return jsonify({"error": "S3_BUCKET_NAME is not configured"}), 500

    filter_term = request.args.get('filter_term', '')
    sort_by = request.args.get('sort_by', 'Key')
    sort_order = request.args.get('sort_order', 'asc')

    files = get_s3_objects_logic(filter_term, sort_by, sort_order)

    if files is None:
        return jsonify({"error": "Could not retrieve files from S3."}), 500

    return jsonify(files)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    filename = secure_filename(file.filename)

    try:
        s3_client.upload_fileobj(file, S3_BUCKET_NAME, filename)
        return jsonify({"message": f"File '{filename}' uploaded successfully!"}), 200
    except ClientError as e:
        return jsonify({"error": f"Error uploading file: {str(e)}"}), 500


@app.route('/api/download/<path:filename>')
def download_file(filename):
    try:
        file_obj = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=filename)
        return Response(
            file_obj['Body'].read(),
            mimetype=file_obj.get('ContentType', 'application/octet-stream'),
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return jsonify({"error": "File not found"}), 404
        return jsonify({"error": f"Error downloading file: {str(e)}"}), 500


@app.route('/api/delete/<path:filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=filename)
        return jsonify({"message": f"File '{filename}' deleted successfully."}), 200
    except ClientError as e:
        return jsonify({"error": f"Error deleting file: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
