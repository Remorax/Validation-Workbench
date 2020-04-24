import os
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from . import db, admins, UPLOAD_FOLDER
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['tsv'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.email in admins:
        return render_template('admin_dashboard.html')
    return render_template('user_dashboard.html', name=current_user.name)

@main.route('/upload-file', methods=['POST'])
def upload():
    print ("yup")
    if "file" not in request.files:
        resp = jsonify({'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files.get("file")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        resp = jsonify({'message' : 'Files successfully uploaded'})
        resp.status_code = 201
    else:
        resp = jsonify({'message' : 'File type is not allowed'})
        resp.status_code = 400
    return resp
