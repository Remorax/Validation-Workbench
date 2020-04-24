from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from . import db, admins

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

@main.route('/fileupload', methods=['POST'])
def upload():
    print ("yup")
    print (request.files)
