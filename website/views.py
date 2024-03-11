from flask import Blueprint,render_template,request,redirect,url_for
from flask import flash
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import update
import datetime
from website.models import Register
from website import db
from flask_login import  login_required , current_user
import google.generativeai as genai
import PIL.Image    
import os
import shutil
from PIL import Image
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import fitz


views = Blueprint('views',__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

image_path = os.path.join(os.getcwd(), 'answer.jpeg')

genai.configure(api_key="AIzaSyDMkylfV_O9Tpd7cELHZ_G4hx3dMg3A4tU")
model = genai.GenerativeModel('gemini-pro-vision')
def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower()
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def clear_upload_folder():
    folder_path = os.path.join(os.getcwd(), UPLOAD_FOLDER)
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
def clear_upload_folder1(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
def convert_pdf_to_jpg(pdf_path, output_folder):
    try:
        clear_upload_folder1(output_folder)
        
        pdf_document = fitz.open(pdf_path)

      
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)


        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            image = page.get_pixmap()
            image.save(os.path.join(output_folder, f"converted_page_{page_number + 1}.png"))
        pdf_document.close()
        
        print(f"PDF converted to JPG and saved in '{output_folder}'")
        return True
    except Exception as e:
        print(f"Error converting PDF to JPG: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


@views.route('/')
def home():
    return render_template("home.html")



@views.route('/teachereditdashboard',methods=['GET','POST'])
@login_required
def teachereditdashboard():
    if request.method == 'POST':
        name = request.form.get("teachername")
        email = request.form.get("teacheremail")
        dob = request.form.get("teacherdob")
        dob1 = datetime.datetime.strptime(dob, "%Y-%m-%d")
        sex =request.form.get("teachersex")
        department = request.form.get("teacherdepartment")

        register = Register.query.filter_by(email=email).first()
        register.name=name
        register.email=email
        register.dob=dob1
        register.sex=sex
        register.department =department

        db.session.commit() 

    return render_template('teachereditdashboard.html',user=current_user)

@views.route('/studenteditdashboard',methods=['GET','POST'])
@login_required
def studenteditdashboard():
    if request.method == 'POST':
        name = request.form.get("studentname")
        regnumber = request.form.get("regnumber")
        email = request.form.get("studentemail")
        dob = request.form.get("studentdob")
        dob1 = datetime.datetime.strptime(dob, "%Y-%m-%d")
        sex =request.form.get("studentsex")
        semester = request.form.get("semester")
        department = request.form.get("studentdepartment")

        register = Register.query.filter_by(email=email).first()
        register.name=name
        register.register_number = regnumber
        register.email=email
        register.dob=dob1
        register.sex=sex
        register.semester = semester
        register.department =department

        db.session.commit() 

    return render_template('studenteditdashboard.html',user=current_user)

@views.route('/studentdashboard')
@login_required
def studentdashboard():
    return render_template('studentdashboard.html',user=current_user)

@views.route('/studentverification')
@login_required
def studentverification():
    students = Register.query.filter_by(status = 0,userrole = 0).all()
    
    return render_template('studentverification.html',user=current_user,students = students)

@views.route('/teacherdashboard')
@login_required
def teacherdashboard():
    return render_template('teacherdashboard.html',user=current_user)

@views.route('/uploadanswersheet',methods = ['GET','POST'])
@login_required
def uploadanswersheet():
    output_parts = []
    if request.method == 'POST':

        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # If the file is allowed and has a valid extension
        if file and allowed_file(file.filename):
            # Secure the filename
            

            
            file_extension = get_file_extension(file.filename)
            unique_filename = "AnswerSheet" + file_extension
            filename = secure_filename(unique_filename)

            clear_upload_folder()

            filepath = os.path.join(UPLOAD_FOLDER,filename)

            if os.path.exists(filepath):
                os.remove(filepath)

            file.save(filepath)
            flash ("uploaded sucessfully")

            pdf_filename = "AnswerSheet.pdf"
            pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
            output_folder = os.path.join(os.getcwd(), 'converted')
            if os.path.exists(pdf_path):
                success = convert_pdf_to_jpg(pdf_path, output_folder)
            if success:
                flash("PDF converted to JPG successfully.")
            else:
                flash("Error converting PDF to JPG. Please check the logs for details.")
            
            converted_folder = os.path.join(os.getcwd(), 'converted')
            for filename in os.listdir(converted_folder):
                if filename.endswith('.png'):
                    image_path = os.path.join(converted_folder, filename)
                    img = Image.open(image_path)
                    response = model.generate_content(["convert hand written to text ", img])
                    candidates = response.candidates
                    for candidate in candidates:
                        content_parts = candidate.content.parts
                        for part in content_parts:
                            #flash(part.text)
                            output_parts.append(part.text)
                    output_text = ' '.join(output_parts) 
                    print(output_text) 
            return redirect(url_for('views.uploadanswersheet'))
    return render_template('uploadanswersheet.html',user=current_user)

@views.route('/admindashboard')
@login_required
def admindashboard():
    return render_template('admindashboard.html',user=current_user)

@views.route('/changeadminpassword',methods = ['GET','POST'])
@login_required
def changeadminpassword():
    if request.method == 'POST':
        password = request.form.get("adminpassword")
        password1 = request.form.get("adminpassword1")
        if(password == password1):
            email = request.form.get("email")
            admin = Register.query.filter_by(email=email).first()
            admin.password=password
            db.session.commit()
            flash('password updated successfully', category='sucess')
        else:
            flash('passwords don\'t match', category='error')

    return render_template('changeadminpassword.html',user=current_user)

@views.route('/teacherverification')
@login_required
def teacherverification():
    teachers = Register.query.filter_by(status = 0,userrole = 1).all()
    
    return render_template('teacherverification.html',user=current_user,teachers = teachers)

@views.route('/addadmin', methods=['GET','POST'])
@login_required
def addadmin():
    if request.method == 'POST':
        name = request.form.get("name")
        password = request.form.get("password")
        sex = request.form.get("sex")
        email = request.form.get("email")
        existing_user = Register.query.filter_by(email=email, userrole=2).first()
        existing_student = Register.query.filter_by(email=email, userrole=0).first()
        existing_teacher = Register.query.filter_by(email=email, userrole=1).first()

        if len(name) < 2:
            flash('Name  must be greater than 1 characters', category='error')
        elif existing_user or existing_student or existing_teacher:
            flash('Email address already exists. Please choose a different email.')
        elif len(password) < 7:
            flash('passwords must be atleast 7 characters', category='error')    
        # elif password != password1:
        #     flash('passwords don\'t match', category='error') 
        elif (sex == "Select"): 
            flash('sex must be filled', category='error')
        
        elif len(email) < 2:
            flash('email must be greater than 5 characters',category='error')                        
     
        else:
            flash('Account created', category='sucess')
            admine = Register(name=name,password=password,sex=sex,email=email,userrole=2)
            db.session.add(admine)
            db.session.commit()
    return render_template('addadmin.html',user=current_user)

@views.route('/<int:id>/approvestudent',methods=['GET','POST'])
@login_required
def approvestudent(id):
    student = Register.query.filter_by(id=id).first() 
    if request.method == 'POST':
        student.status= 1
        db.session.commit() 
        return redirect(url_for('views.studentverification'))

    return render_template('approvestudent.html',student=student,user=current_user)

@views.route('/<int:id>/disapprovestudent',methods=['GET','POST'])
@login_required
def disapprovestudent(id):
    student = Register.query.filter_by(id=id).first()
    if request.method == 'POST':
        if student:
            db.session.delete(student)
            db.session.commit()
            return redirect(url_for('views.studentverification'))
        
    return render_template('disapprovestudent.html',student=student ,user=current_user)

@views.route('/<int:id>/approveteacher',methods=['GET','POST'])
@login_required
def approveteacher(id):
    teacher = Register.query.filter_by(id=id).first() 
    if request.method == 'POST':
        teacher.status= 1
        db.session.commit() 
        return redirect(url_for('views.teacherverification'))

    return render_template('approveteacher.html',teacher=teacher,user=current_user)

@views.route('/<int:id>/disapproveteacher',methods=['GET','POST'])
@login_required
def disapproveteacher(id):
    teacher = Register.query.filter_by(id=id).first()
    if request.method == 'POST':
        if teacher:
            db.session.delete(teacher)
            db.session.commit()
            return redirect(url_for('views.teacherverification'))
        
    return render_template('disapproveteacher.html',teacher = teacher,user=current_user)

@views.route('/admineditdashboard',methods=['GET','POST'])
@login_required
def admineditdashboard():
    if request.method == 'POST':
        adminname = request.form.get("adminname")
        adminemail = request.form.get("adminemail")
        adminsex = request.form.get("adminsex")
        register = Register.query.filter_by(email=adminemail).first()
        register.name=adminname
        register.sex=adminsex
        db.session.commit() 
    return render_template('admineditdashboard.html',user=current_user)


@views.route('/teacherchangepassword',methods=['GET','POST'])
@login_required
def teacherchangepassword():
    if request.method == 'POST':
        teacherpassword = request.form.get("teacherpassword")
        teacherpassword1 = request.form.get("teacherpassword1")
        if(teacherpassword == teacherpassword1):
            email = request.form.get("email")
            teacher = Register.query.filter_by(email=email).first()
            teacher.password=teacherpassword
            db.session.commit()
            flash('password updated successfully', category='sucess')
        else:
            flash('passwords don\'t match', category='error')

    return render_template('teacherchangepassword.html',user=current_user)

@views.route('/studentchangepassword',methods=['GET','POST'])
@login_required
def studentchangepassword():
    if request.method == 'POST':
        studentpassword = request.form.get("studentpassword")
        studentpassword1 = request.form.get("studentpassword1")
        if(studentpassword == studentpassword1):
            email = request.form.get("email")
            student = Register.query.filter_by(email=email).first()
            student.password=studentpassword
            db.session.commit()
            flash('password updated successfully', category='sucess')
        else:
            flash('passwords don\'t match', category='error')

    return render_template('studentchangepassword.html',user=current_user)




@views.route('/studentregister',methods=['GET','POST'])
def studentregister():
    if request.method == 'POST':
        studentname = request.form.get("studentname")
        studentemail = request.form.get("studentemail")
        studentregisternumber = request.form.get("studentregisternumber")
        dob1 = request.form.get("studentdob")
        studentdob = datetime.datetime.strptime(dob1, "%Y-%m-%d")
        studentgender = request.form.get("studentgender")
        studentsemester = request.form.get("studentsemester")
        studentdepartment = request.form.get("studentdepartment")
        studentpassword = request.form.get("studentpassword")
        student = Register.query.filter_by(email=studentemail).first()
        if student:
            flash('Email already exists.', category='error')
        elif len(studentname) < 2:
            flash('Name  must be greater than 1 characters', category='error')
        elif len(studentpassword) < 8:
            flash('passwords must be atleast 8 characters', category='error')    
        elif not dob1: 
            flash('dob must be filled', category='error') 
            return render_template('studentregister.html')    
        elif (studentgender == "Select Gender"): 
            flash('Gender must be filled', category='error')
        elif (studentregisternumber == None): 
            flash('studentregisternumber must be filled' , category ='error') 
        elif (studentdepartment == "Select Department"): 
            flash('Department must be filled' , category='error')  
        elif (studentsemester == "Select Semester"): 
            flash('semester must be filled' ,category='error') 
        elif len(studentemail) < 2:
            flash('email must be greater than 5 characters',category='error')                        
        else:
            flash('Account created', category='sucess')
            student = Register(name=studentname,email=studentemail,register_number=studentregisternumber,dob=studentdob,sex=studentgender,semester=studentsemester,department=studentdepartment,password=studentpassword,status=0,userrole=0)
            db.session.add(student)
            db.session.commit()
            
        return render_template('studentregister.html') 
    return render_template("studentregister.html")      

@views.route('/teacherregister',methods=['GET','POST'])
def teacherregister():
    if request.method == 'POST':
        teachername = request.form.get("teachername")
        teacheremail = request.form.get("teacheremail")
        dob1 = request.form.get("teacherdob")
        dob2 = datetime.datetime.strptime(dob1, "%Y-%m-%d")
        teachergender = request.form.get("teachergender")
        teacherdepartment = request.form.get("teacherdepartment")
        teacherpassword = request.form.get("teacherpassword")
        teacher = Register.query.filter_by(email=teacheremail).first()
        if teacher:
            flash('Email already exists.', category='error')
        elif len(teachername) < 2:
            flash('Name  must be greater than 1 characters', category='error')
        elif len(teacheremail) < 2:
            flash('email must be greater than 5 characters',category='error')
        elif (dob1 == None): 
            flash('dob must be filled', category='error')   
        elif (teachergender == "Select Gender"): 
            flash('Gender must be filled', category='error') 
        elif (teacherdepartment == "Select Department"): 
            flash('Department must be filled' , category ='error')  
        elif len(teacherpassword) < 7:
            flash('password must be atleast 7 characters', category='error')    
        else:
            flash('Account created', category='sucess')
            teacher = Register(name=teachername,email=teacheremail,dob=dob2,sex=teachergender,department=teacherdepartment,password=teacherpassword,status=0,userrole=1)
            db.session.add(teacher)
            db.session.commit()
            
        return render_template('teacherregister.html') 
    return render_template("teacherregister.html")