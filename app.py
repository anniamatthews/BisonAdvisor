
from flask import Flask, session, render_template, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
import pyrebase
import firebase_admin
import uuid
import os
from firebase_admin import firestore, credentials, db, auth
from flask_wtf import FlaskForm
from config import config

UPLOAD_FOLDER = '/Users/test/bison-swe/uploaded_files'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

app.secret_key = 'secret-key'

@app.route('/')
def index():
    print('sign in link',url_for('sign_in'))
    return render_template('index.html')

@app.route('/register')
def register(): 
    return render_template('/register.html')

'''There's currently an error in this that doesn't catch the session correctly, so it redirects an authenticated user to the landimg page'''
@app.route('/dashboard')
def dashboard(): 
    if 'user' not in session: 
        return redirect(url_for('index'))  # Correct redirect
    return render_template('dashboard.html')

@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in(): 
    unsuccessful = 'Pls check your credentials'
    successful = 'good'
    if request.method == 'POST': 
        try: 
            email = request.form['name']
            password = request.form['pass']
            try:
                auth.sign_in_with_email_and_password(email, password)
                return redirect(url_for('dashboard'))
            except Exception as e: 
                print('login failed', str(e))
                return render_template('sign-in.html', us=unsuccessful)
        except Exception as e: 
            print('failed', str(e))
    return render_template('/sign-in.html')






@app.route('/select_role', methods=['POST', 'GET'])
def select_role():
    if 'user' not in session: 
        return redirect('/')
    if request.method == 'POST':
        role = request.form.get('role')
        print(role)
        if role == 'student':
            return render_template('student_page.html') # Redirect to student page
        elif role == 'advisor':
            return render_template('advisor_page.html') # Redirect to advisor page

    return render_template('select_role.html')


@app.route('/student_page', methods = ['POST', 'GET'])
def student_page():
    if 'user' not in session: 
        return redirect('/')
    if request.method =='POST':
        option = request.form.get('action')
        if option == 'action1':
            return render_template('add_classes.html')
        elif option =='action2':
            return render_template('student_location.html')
        elif option == 'action3':
            return render_template('self_service_resources.html')
    
    return render_template('student_page.html')



@app.route('/advisor_page', methods = ['POST', 'GET'])
def advisor_page():
    if 'user' not in session: 
        return redirect('/')
    if request.method =='POST':
        option = request.form.get('option')
        if option == 'option1':
            return render_template('course_catalog.html')
        elif option =='option2':
            return 'TODO: Check on students'
    return render_template('advisor_page.html')

@app.route("/postskill",methods=["POST","GET"])
def postskill():
    if 'user' not in session: 
        return redirect('/')
    if request.method =='POST':
        # this needs to be a loop or something so that it can be stored into the db
        names = request.form.getlist('name[]')
        credits = request.form.getlist('credit[]')
        grades = request.form.getlist('grade[]')
        

        for i in range(len(names)):
            new_entry_ref = db.child("names").push(data={ # change 'names' to uuid generated token, to be different logins
                
                'class_name': names[i],
                'class_credits': credits[i],
                'class_grade': grades[i]
            })
                 
    return render_template('add_classes.html')





def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/course_catalog', methods=['GET', 'POST'])
def upload_file():
    if request.method =='POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect('course_catalog.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file', name=filename))
    return render_template('course_catalog.html')
        
        
    


def generate_unique_id():
    unique_id = str(uuid.uuid4())
    return unique_id
    

@app.route('/logout')
def logout():
    session.pop('user')
    return(redirect('/'))

if __name__ == '__main__':
    app.run(port = 1111)

