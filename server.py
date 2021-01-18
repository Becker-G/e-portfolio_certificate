# coding=utf-8
import os
import random, string
import json
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from apps.models import User
from apps.ext import db
from apps.tangle import write_data_to_tangle
from apps.findmessages import findmessages
from apps.account import remove
from datetime import datetime, date


app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
app.config['SECRET_KEY'] = 'eportfoliocredential'
Bootstrap(app)


# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'signin'


class SigninForm(FlaskForm):
    student_id = StringField('student_id', validators=[InputRequired(), Length(min=5, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=5, max=80)])
    remember = BooleanField('remember me')

class SignupForm(FlaskForm):
    student_id = StringField('student_id', validators=[InputRequired(), Length(min=5, max=15)])
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=15)])
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    group = StringField('role', validators=[InputRequired(), Length(min=2, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=5, max=80)])


with app.app_context():
    db.create_all()



# Get user
@login_manager.user_loader
def user_loader(id):
    user = User.query.filter_by(id=id).first()
    #user = User()
    #user.student_id = student_id
    #return User.query.get(user_id)
    #user = User.query.filter_by(student_id=id).first()
    return user


# Index page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm(request.form)

    if form.validate_on_submit():
        user = User.query.filter_by(student_id=form.student_id.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                
                f = open("static/accounts.txt", "r")
                list_content = f.read().splitlines()
                f.close()

                for obj_acc in list_content:
                    obj_json = json.loads(obj_acc)

                    if obj_json["group"] == "admin":
                        return redirect(url_for("admin_dashboard"))
                    elif obj_json["group"] == "teacher":
                        return redirect(url_for("teacher_dashboard"))
                    else:
                        return redirect(url_for("student_dashboard"))
                #return '<h1>hello</h1>'
                
                #return redirect(url_for('dashboard'))

        return '<h1>Bad Login</h1>'

    return render_template('signin.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form) 

    if form.validate_on_submit():

        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(student_id=form.student_id.data, username=form.username.data, 
                        email=form.email.data, group=form.group.data, password=hashed_password, 
                        confirmed_at=datetime.now(), active=True)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'

    return render_template('signup.html', form=form)


# 管理者首頁
# admin_dashboard
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    file_experience = open("static/experience.txt", "r")
    list_raw_experience = file_experience.readlines()
    file_experience.close()

    file_account = open("static/accounts.txt", "r")
    list_raw_account = file_account.readlines()
    file_account.close()

    list_review = []

    for obj_experience in list_raw_experience:
        obj_exp = json.loads(obj_experience)

        # find name
        for obj_account in list_raw_account:
            obj_acc = json.loads(obj_account)

            if obj_exp["student_id"] == obj_acc["student_id"]:
                obj_exp["username"] = obj_acc["username"]

                if "status" not in obj_exp:
                    obj_exp["status"] = "Auditing"

                list_review.append(obj_exp)

    return render_template('admin_dashboard.html', name=current_user.username, list_review = list_review)


# 老師首頁
# teacher_dashboard
@app.route("/teacher_dashboard")
@login_required
def teacher_dashboard():
    file_experience = open("static/experience.txt", "r")
    list_raw_experience = file_experience.readlines()
    file_experience.close()

    file_account = open("static/accounts.txt", "r")
    list_raw_account = file_account.readlines()
    file_account.close()

    list_review = []

    for obj_experience in list_raw_experience:
        obj_exp = json.loads(obj_experience)

        # find name
        for obj_account in list_raw_account:
            obj_acc = json.loads(obj_account)

            if obj_exp["student_id"] == obj_acc["account"]:
                obj_exp["name"] = obj_acc["name"]

                if "status" not in obj_exp:
                    obj_exp["status"] = "Auditing"

                list_review.append(obj_exp)

    return render_template('teacher_dashboard.html', name=current_user.username, list_review = list_review)


# 個人證書列表(學生首頁)
# student_dashboard
@app.route("/student_dashboard",methods=['GET', 'POST'])
@login_required
def student_dashboard():
    list_review = []
    if request.method == 'GET':
        file_experience = open("static/experience_ovrview.txt", "r")
        list_raw_experience = file_experience.readlines()
        file_experience.close()

        for obj_exp_ovrview in list_raw_experience:
            obj_exp_ovr = json.loads(obj_exp_ovrview)
            if obj_exp_ovr["student_id"] == current_user.student_id:
                list_review.append(obj_exp_ovr)
        
        return render_template('student_dashboard.html', name=current_user.username, list_review = list_review)    


'''
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)
'''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# 活動編輯
# Activity information page
@app.route("/activity_info", methods=['GET', 'POST'])
@login_required
def activity_info():
    if request.method == 'GET':
        return render_template('ActivityInformation.html')
    else:
        form_content = request.form
        fp = open("static/activities.txt", "a")
        fp.write(json.dumps(form_content) + "\n")
        fp.close()
        return redirect(url_for("activity_info"))


# 心得填寫
# Page for student
@app.route("/credential_editor", methods=['GET', 'POST'])
@login_required
def credential_editor():
    if request.method == 'GET':
        list_credential = []
        fp = open("static/activities.txt", "r")
        list_content = fp.readlines()
        fp.close()

        for obj in list_content:
            list_credential.append(json.loads(obj))
        
        return render_template('credential_editor.html', list_credential = list_credential)
    
    else:
        fp = open("static/experience.txt", "a")
        form_content = request.form
        exp = form_content.to_dict()
        x = exp["activity_kind"].split("/")
        exp["id"] = ''.join(random.choice(string.ascii_letters) for x in range(4))
        exp["Date"] = x[0]
        exp["ActivityName"] = x[1]
        exp["Credit"] = x[2]
        exp["student_id"] = current_user.id
        del exp["activity_kind"]
        fp.write(json.dumps(exp) + "\n")
        fp.close()

        return redirect(url_for("student_dashboard"))

# 個人證書審查
# credential_apply
@app.route("/credential_apply",methods=['GET', 'POST'])
@login_required
def credential_apply():
    f = open("static/experience.txt", "r")
    content = f.readlines()
    f.close()

    exp_list = []
    for obj_experience in content:
        obj = json.loads(obj_experience)
        if obj["student_id"] == current_user.id:
            exp_list.append(obj)
    return render_template('credential_apply',list_content = exp_list)


# 審核總攬
# verify_list
@app.route("/verify_list")
@login_required
def verify_list():
    file_experience = open("static/experience_ovrview.txt", "r")
    list_raw_experience = file_experience.readlines()
    file_experience.close()

    file_account = open("static/accounts.txt", "r")
    list_raw_account = file_account.readlines()
    file_account.close()

    list_review = []

    for obj_exp_ovr in list_raw_experience:
        obj_exp = json.loads(obj_exp_ovr)

        # find name
        for obj_account in list_raw_account:
            obj_acc = json.loads(obj_account)

            if obj_exp["student_id"] == obj_acc["student_id"]:
                obj_exp["username"] = obj_acc["username"]

                if "status" in obj_exp:
                    if obj_exp["status"] != "aduiting":
                        list_review.append(obj_exp)

    return render_template('verify_list.html',list_review = list_review)


# 後台管理
# backend
@app.route("/backend")
def backend():
    list_user = []
    f = open("static/accounts.txt", "r")
    list_content = f.read().splitlines()
    f.close()

    for obj in list_content:
        list_user.append(json.loads(obj))

    return render_template('backend.html',list_user = list_user)


# delet failed user
@app.route("/backend_account_manage", methods=["GET"])
def backend_account_manage():
    remove_account = request.args.get("remove")

    if remove_account != None:
        remove(remove_account)

    return redirect(url_for("index"))


# 心得審核
@app.route("/admin_dashboard_url",methods=['GET', 'POST'])
@login_required
def admin_dashboard_url():
        if request.method == 'POST':
            form_content = request.form
            dict_obj = form_content.to_dict()
            
            if dict_obj["audit_result"] != "Not_yet":
                list_output = []
                file_experience = open("static/experience.txt", "r")
                list_content = file_experience.readlines()
                file_experience.close()

                # remove old
                obj_keep = {}
                for obj_experience in list_content:
                    obj_json = json.loads(obj_experience)
                    if obj_json["id"] == dict_obj["cre_id"]:
                        obj_keep = obj_json
                        list_content.remove(obj)

                # add new
                if dict_obj["audit_result"] == "pass":
                    # TODO: credential hash
                    result = write_data_to_tangle(str(date.today()))
                    obj_keep["status"] = str(result["bundle"])
                else:
                    obj_keep["status"] = dict_obj["audit_result"]

                # write
                os.remove("static/experience.txt")
                with open('static/experience.txt', 'a') as file_experience:
                    for obj in list_content:
                        obj = json.loads(obj)
                        file_experience.write(json.dumps(obj))
                        file_experience.write("\n")

                if "status" in obj_keep:
                    with open('static/experience_ovrview.txt', 'a') as file_experience:
                        file_experience.write(json.dumps(obj_keep))
                        file_experience.write("\n")

            return redirect(url_for("admin_dashboard"))

        exp = ""
        ActivityName = request.args.get("ActivityName")
        Date = request.args.get("Date")
        student_id = request.args.get("student_id")
        cre_id = request.args.get("id")

        f = open("static/experience.txt", "r")
        content = f.readlines()
        f.close()

        for obj in content:
            obj = json.loads(obj)
            if obj["student_id"] == student_id and obj["ActivityName"] == ActivityName and obj["Date"] == Date:
                exp = obj["experience"]
        
        return render_template('admin_dashboard_url.html',cre_id = cre_id, exp = exp)


# search
@app.route("/search_list")
def search_list():
    f = open("static/history.txt", "r")
    content = f.readlines()
    f.close()   

    return render_template('search_list.html',title=content)

# feedback
@app.route("/feedback", methods=['GET'])
@login_required
def feedback():
    exp = ""
    ActivityName = request.args.get("ActivityName")
    Date = request.args.get("Date")
    f = open("static/experience.txt", "r")
    content = f.readlines()
    f.close()

    for obj_experience in content:
        obj = json.loads(obj_experience)
        if obj["student_id"] == current_user.id and obj["ActivityName"] == ActivityName and obj["Date"] == Date:
            exp = obj["experience"]

    return render_template('feedback.html', exp = exp)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9527)










