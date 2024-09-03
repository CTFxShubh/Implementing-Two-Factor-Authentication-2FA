from flask import Flask, request, render_template, redirect, url_for, session
import pyotp
import qrcode
import io
from base64 import b64encode

app = Flask(__name__)
app.secret_key = 'supersecretkey'
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return 'Username already exists!'
        secret = pyotp.random_base32()
        users[username] = {'password': password, 'secret': secret}
        return 'Registered successfully!'
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users or users[username]['password'] != password:
            return 'Invalid credentials!'
        session['username'] = username
        return redirect(url_for('two_factor'))
    return render_template('login.html')

@app.route('/2fa', methods=['GET', 'POST'])
def two_factor():
    if request.method == 'POST':
        token = request.form['token']
        username = session.get('username')
        if username:
            totp = pyotp.TOTP(users[username]['secret'], digits=6)
            print(f"Expected OTP: {totp.now()}")  # Debug print
            if totp.verify(token):
                return 'Login successful!'
            else:
                return 'Invalid OTP!'
        return 'Invalid session!'
    return render_template('2fa.html', qr_code=generate_qr_code())

def generate_qr_code():
    username = session['username']
    secret = users[username]['secret']
    uri = pyotp.TOTP(secret, digits=6).provisioning_uri(name=username, issuer_name="MyApp")
    qr = qrcode.make(uri)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    img_str = b64encode(buf.getvalue()).decode('ascii')
    return img_str

if __name__ == '__main__':
    app.run(debug=True)
