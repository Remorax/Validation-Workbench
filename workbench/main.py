import os
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from . import db, admins, UPLOAD_FOLDER
from .models import Validation
from werkzeug.utils import secure_filename
from collections import Counter

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
    is_admin = current_user.email in admins
    return render_template('dashboard.html', is_admin=is_admin)

@main.route('/dashboard', methods=["POST"])
@login_required
def write_decisions():
    filename = list(request.form.values())[-1]
    is_admin = current_user.email in admins
    if not is_admin:
        response_str = ",".join(list(request.form.values())[:-1])
        prev_response = Validation.query.filter(Validation.email==current_user.email, Validation.file==filename).first()
        if prev_response:
            prev_response.response = response_str
        else:
            new_response = Validation(email=current_user.email, name=current_user.name, response=response_str, file=filename)
            db.session.add(new_response)
        db.session.commit()
    return render_template('dashboard.html', is_admin=is_admin)


@main.route('/responses', methods=["GET"])
@login_required
def show_response():
    file_idx = request.args.get('file')
    files = [os.path.join(UPLOAD_FOLDER, file) for file in os.listdir(UPLOAD_FOLDER)]
    files.sort(key=os.path.getmtime, reverse=True)
    file_path = files[int(file_idx)]
    file = [l.split("\t") for l in open(file_path).read().split("\n")][1:]
    is_admin = current_user.email in admins
    if not is_admin:
        responses = ["1" for n in range(len(file))]
        prev_response = Validation.query.filter(Validation.email==current_user.email, Validation.file==file_idx).first()
        if prev_response:
            responses = prev_response.response.split(",")
        return render_template('responses.html', file=list(zip(file, responses)))
    else:
        all_responses = [el.response.split(",") for el in Validation.query.filter(Validation.file==file_idx).all()]
        all_responses = list(zip(*all_responses))
        responses = [Counter({"0": 0, "1": 0}) for resp in file]
        for i,resp in enumerate(all_responses):
            responses[i].update(resp)
        responses = [[el[1] for el in sorted(resp.items(), key=lambda x:int(x[0]))] for resp in responses]
        return render_template('summary.html', file=list(zip(file,responses)))    
    
    

@main.route('/load-files', methods=["GET"])
@login_required
def load_files():
    files = [os.path.join(UPLOAD_FOLDER, file) for file in os.listdir(UPLOAD_FOLDER)]
    files.sort(key=os.path.getmtime, reverse=True)
    files_str = ""
    # print (files)
    for i,file in enumerate(files):
        # print (file.split("/"), file.split("/")[-1])
        file_id = str(int(i/3)) + "_" + str(i%3)
        td_str = ("<td id=\'" + file_id +  "\'>" +
                    "<a href=\'/responses?file=" + str(i) + "\'>" + 
                        "<div id=\'" + file_id + "_name\' class=\'filename\'>" + 
                            file.split("/")[-1] +
                    "</div></a></td>")
        if i%3 == 0:
            files_str += "<tr>" + td_str
        elif i%3 == 2:
            files_str += td_str + "</tr>"
        else:
            files_str += td_str
    extra = (2 - i%3)
    for j in range(extra):
        idx = i+j+1
        file_id = str(int(idx/3)) + "_" + str(idx%3)
        files_str += ("<td id=\'" + file_id +  "\' style=\'visibility: hidden;\'>" +
                        "<a href=\'/responses?file=" + str(idx) + "\'>" + 
                            "<div id=\'" + file_id + "_name\' class=\'filename\'>" + 
                        "</div></a></td>")

    return jsonify({"files": files_str, "count": len(files)})

@main.route('/upload-file', methods=['POST'])
def upload():
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
