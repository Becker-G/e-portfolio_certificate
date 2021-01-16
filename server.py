# coding=utf-8
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eportfoliocredential'
Bootstrap(app)

class SigninForm(FlaskForm):
    student_id = StringField('student_id', validators=[InputRequired(), Length(min=5, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=5, max=80)])
    remember = BooleanField('remember me')

class SignupForm(FlaskForm):
    student_id = StringField('student_id', validators=[InputRequired(), Length(min=5, max=15)])
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=15)])
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    role = StringField('role', validators=[InputRequired(), Length(min=2, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=5, max=80)])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()

    if form.validate_on_submit():
        return '<h1>' + form.student_id.data + '</h1>' 
    return render_template('signin.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm() 

    if form.validate_on_submit():
        return '<h1>' + form.student_id.data + '</h1>' 
    return render_template('signup.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9527 , debug=True)










