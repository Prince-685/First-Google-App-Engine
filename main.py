from flask import *
import pyotp
from google.cloud import ndb
from model import User
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)


def send_otp_email(email, otp):
    from_email = 'pagalno351@gmail.com'  
    password = 'Prince@123'       

    subject = 'Your OTP for Login'
    message = f'Your OTP is: {otp}'

    msg = MIMEText(message)
    msg['From'] = from_email
    msg['To'] = email
    msg['Subject'] = subject

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, [email], msg.as_string())
        server.quit()
        print("OTP sent successfully")
    except Exception as e:
        print("Error sending OTP:", e)


def generate_otp():
    secret = pyotp.random_base32()
    t = pyotp.TOTP(secret,interval=60,digits=6)
    otp = t.now()
    return {
        'secret':secret,
        'otp':otp
    }

def verify_otp(secret,otp):
    totp=pyotp.TOTP(secret,interval=60).verify(otp)
    if totp:
        return True
    return False

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signuppage')
def signup_page():
    return render_template('signup.html')


@app.route('/loginpage')
def login_page():
    return render_template('login.html')


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
    if request.method=='POST':
        email = request.form['email']

        user = User.query(User.email == email).get()
        if user:
            data=generate_otp()
            send_otp_email(email,data['otp'])
            return redirect(url_for('verify_otp',**data))
        else:
            return render_template('login.html',{'msg':'Email is not registered...'})


@app.route('/verify_otp',methods=['POST'])
def verify_otp():
    secret = request.args.get('secret')
    if request.method=='POST':
        otp=request.form['otp']
        verify=verify_otp(secret,otp)
        if verify:
            return jsonify({'msg':'User Logged in Successfully'})
        else:
           return render_template('otp.html',{'msg':'Enter a valid otp...'})


if __name__ == '__main__':
    app.run(debug=True)
