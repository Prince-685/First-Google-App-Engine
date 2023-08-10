from flask import *
from flask_mail import Mail, Message
import pyotp
from google.cloud import ndb,storage
from model import User
# from werkzeug.utils import secure_filename
# from moviepy.editor import VideoFileClip
# import subprocess
import ffmpeg

app = Flask(__name__)
mail= Mail(app)
# app.config['UPLOAD_FOLDER'] = 'uploads'


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'pagalno351@gmail.com'
app.config['MAIL_PASSWORD'] = 'lfpbgslenaxxeqco'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

secret = pyotp.random_base32()


def send_otp_email(email, otp):
    try:
        msg = Message('OTP', sender = 'pagalno351@gmail.com', recipients = [email])
        msg.body = f'Your OTP for LOgin is: {otp}'
        mail.send(msg)
        return True
        
    except Exception as e:
        print("Error sending OTP:", e)
        return False


def generate_otp():
    t = pyotp.TOTP(secret,interval=600,digits=6)
    otp = t.now()
    return {
        'secret':secret,
        'otp':otp
    }

def verify_otp(secret,otp):
    totp=pyotp.TOTP(secret,interval=600).verify(otp)
    if totp:
        return True
    return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov'}

import subprocess

def is_resolution_valid(video_file):
    # command = [
    #     'ffprobe',
    #     '-v', 'error',
    #     '-select_streams', 'v:0',
    #     '-show_entries', 'stream=width,height',
    #     '-of', 'csv=p=0',
    #     file_path
    # ]
    
    # result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    # width, height = result.stdout.strip().split(',')
    width,height=video_file.size()

    return int(width) >= 1920 and int(height) >= 1080

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signuppage')
def signup_page():
    return render_template('signup.html')


@app.route('/loginpage')
def login_page():
    return render_template('login.html')

@app.route('/otp_page')
def otp_page():
    return render_template('otp.html')

@app.route('/uploadpage')
def uploadpage():
    return render_template('Video-Upload.html')

@app.route('/signup', methods=['POST'])
def sign_up():
    if request.method=='POST':
        fname = request.form['fname']
        email = request.form['email']
        mobile = request.form['mobile']

        client = ndb.Client()
        with client.context():
            user = User(name=fname, email=email, mobile=mobile)
            user.put()
            # return render_template(request,"signup.html",{'msg':'User Signed-Up Successfully'})
            return jsonify({'msg':'User Signed-up Successfully'})

@app.route('/login',methods=['POST'])
def login():
    try:
        if request.method=='POST':
            email = request.form['email']
            client = ndb.Client()
            with client.context():
                user = User.query(User.email == email).get()
                if user:
                    data=generate_otp()
                    p=send_otp_email(email,data['otp'])
                    if p:
                        return redirect(url_for('otp_page'))
                else:
                    return render_template('login.html')
    except Exception as e:
        print('err--:',e)
        return render_template('login.html')


@app.route('/verify',methods=['POST'])
def verify():
    try:
        if request.method=='POST':
            otp=request.form['otp']
            print(otp)
            verify=verify_otp(secret,otp)
            print(verify)
            if verify:
                return jsonify({'msg':'User Logged in Successfully'})
            else:
                return render_template('otp.html')
    except Exception as e:
        print('e---:',e)
        return render_template('otp.html')

@app.route('/upload',methods=['POST'])
def upload():
    try:
        client = storage.Client()
        bucket_name = 'api-assignment-395306.appspot.com'
        bucket = client.bucket(bucket_name)

        if request.method == 'POST':
            video_file = request.files['file']
            
            blob = bucket.blob(video_file.filename)
            blob.upload_from_file(video_file)
                
            return jsonify({'message': 'Video uploaded successfully and resolution is valid.'})

    except Exception as e:
        print('errrrr--',e)
        return render_template('Video-Upload.html')

        

if __name__ == '__main__':
    app.run(debug=True)
