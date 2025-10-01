from flask import Flask,render_template,request,redirect,url_for,session,g,flash,jsonify
from flask_mail import Mail,Message
import sqlite3
import hashlib
import os
from itsdangerous import URLSafeTimedSerializer,SignatureExpired,BadSignature
from crop_recomendation import crop_predict
import requests
from Weather import fetch_weather, process_weather_data,get_7_day_weather_average,get_weather_data
from government import government
from market import fetch_market_data
from Community import show_posts,trending_posts,insert_post,add_comment_db,update_reaction_db,fetch_comments_db
app=Flask(__name__)
app.secret_key=os.urandom(42)
DATABASE='agro.db'
s=URLSafeTimedSerializer(app.secret_key)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USERNAME']='agroconnect0978@gmail.com'
app.config['MAIL_PASSWORD']='jlfe fmwf yuer wfiq'
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USE_SSL']=False
crop_images = {
    'barley': 'images/barley.jpg',
    'sunflower': 'images/sunflower.jpg',
    'sweetpotato': 'images/sweetpotato.jpg',
    'rice': 'images/rice.jpg',
    'soyabean': 'images/soyabean.jpg',
    'jowar': 'images/jowar.jpg',
    'potato': 'images/potato.jpg',
    'turmeric': 'images/turmeric.jpg',
    'jute': 'images/jute.jpg',
    'maize': 'images/maize.jpg',
    'moong': 'images/moong.jpg',
    'onion': 'images/onion.jpg',
    'cabbage': 'images/cabbage.jpg',
    'ragi': 'images/ragi.jpg',
    'banana': 'images/banana.jpg',
    'rapeseed': 'images/rapeseed.jpg',
    'wheat': 'images/wheat.jpg',
    'horsegram': 'images/horsegram.jpg',
    'coriander': 'images/coriander.jpg',
    'mango': 'images/mango.jpg',
    'tomato': 'images/tomato.jpg',
    'cotton': 'images/cotton.jpg',
    'brinjal': 'images/brinjal.jpg',
    'garlic': 'images/garlic.jpg',
    'blackgram': 'images/blackgram.jpg',
    'cardamom': 'images/cardamom.jpg',
    'blackpepper': 'images/blackpepper.jpg',
    'orange': 'images/orange.jpg',
    'bittergourd': 'images/bittergourd.jpg',
    'papaya': 'images/papaya.jpg',
    'grapes': 'images/grapes.jpg',
    'ladyfinger': 'images/ladyfinger.jpg',
    'pineapple': 'images/pineapple.jpg',
    'bottlegourd': 'images/bottlegourd.jpg',
    'jackfruit': 'images/jackfruit.jpg',
    'pumpkin': 'images/pumpkin.jpg',
    'cauliflower': 'images/cauliflower.jpg',
    'cucumber': 'images/cucumber.jpg',
    'drumstick': 'images/drumstick.jpg',
    'radish':'images/radish.jpg'}

mail=Mail(app)
def get_db():
    if 'db' not in g:
        g.db=sqlite3.connect(DATABASE)
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS farmers (
                userid varchar,
                email TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                phone_number INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                email VARCHAR(255),
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255),
                description TEXT,
                likes INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email) REFERENCES farmers(email)
            )
        ''')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS comments (
                comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                email TEXT,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(post_id),
                FOREIGN KEY (email) REFERENCES farmers(email)
            )''')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS liked_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_email TEXT NOT NULL,
                UNIQUE(post_id, user_email),
                FOREIGN KEY(post_id) REFERENCES posts(post_id));''')
        conn.commit()
init_db()
@app.route('/')
def index():
    if 'email' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        userid=request.form['user_id']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash("Passwords do not match.", 'error')
            return redirect(url_for('signup'))
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO farmers (userid,email, password, phone_number) VALUES (?,?, ?, ?)",
                           (userid,email, hashed_password, phone_number))
            db.commit()
            flash("Account created successfully!", 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("This email is already registered.", 'error')
            return redirect(url_for('signup'))
    return render_template('signup.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM farmers WHERE email = ? AND password = ?", (email, hashed_password))
        user = cursor.fetchone()
        if user:
            session['email'] = email
            return redirect(url_for('main_page'))
        else:
            flash("Invalid credentials.", 'error')
            return redirect(url_for('login'))
    return render_template('login.html')
@app.route('/main_page')
def main_page():
    if 'email' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('index'))
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT email FROM farmers WHERE email = ?", (email,))
        user = cursor.fetchone()
        if user:
            token = s.dumps(email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message("Password Reset Request", sender='agroconnect0978@gmail.com', recipients=[email])
            msg.body = f'Please click the link to reset your password: {reset_url}'
            mail.send(msg)
            flash('A password reset link has been sent to your email.', 'success')
        else:
            flash('Email not found. Please try again.', 'error')
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        flash('The reset link has expired. Please request a new one.', 'error')
        return redirect(url_for('forgot_password'))
    except BadSignature:
        flash('Invalid reset link. Please try again.', 'error')
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if new_password == confirm_password:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            db = get_db()
            cursor = db.cursor()
            cursor.execute("UPDATE farmers SET password = ? WHERE email = ?", (hashed_password, email))
            db.commit()
            print(f"Password successfully updated for email: {email}")
            flash('Your password has been successfully updated! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('reset_password', token=token))
    return render_template('reset_password.html', token=token)
@app.route('/crop_recommendation', methods=['GET', 'POST'])
def crop_recommendation():
    if request.method == 'POST':
        try:
            N = float(request.form.get('N'))
            P = float(request.form.get('P'))
            K = float(request.form.get('K'))
            ph = float(request.form.get('ph'))
            lati = request.form.get('lat')
            long = request.form.get('lon')
            if not lati or not long:
                flash("Location data is missing. Please try again.", 'error')
                return redirect('/crop_recommendation')
            tem, rain = get_7_day_weather_average(lati, long)
            if tem is None or rain is None:
                flash("Weather data unavailable. Try again later.", 'error')
                return redirect('/crop_recommendation')
            temperature = float(tem)
            rainfall = float(rain)
            input_features = [[N, P, K, ph,rainfall, temperature]]
            recommended_crop = crop_predict(input_features)
            crop_image = url_for('static', filename=crop_images[recommended_crop])
            flash(f"Recommended Crop: {recommended_crop}", 'success')
            return render_template('crop_recommendation.html', result=recommended_crop, crop_image=crop_image)
        except ValueError:
            flash("Please enter valid numerical values.", 'error')
            return redirect('/crop_recommendation')
        except Exception as e:
            flash(f"An error occurred: {e}", 'error')
            return redirect('/crop_recommendation')
    return render_template('crop_recommendation.html', result=None, crop_image=None)
@app.route('/get_cordinates', methods=['GET', 'POST'])
def get_cordinates():
    return render_template('wlocation.html')
@app.route('/weather_forecast')
def weather_forecast():
    global lat,lon
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    location = request.args.get('location', 'Unknown Location')
    if not lat or not lon:
        return "Latitude and Longitude are required.", 400
    try:
        weather_data = fetch_weather(latitude=lat, longitude=lon)
        print(get_7_day_weather_average(lat,lon))
        today_weather, forecast = process_weather_data(weather_data)
        forecast = forecast[1:]
        return render_template(
            'weather.html', 
            today=today_weather, 
            forecast=forecast, 
            location=location
        )
    except Exception as e:
        return f"Error fetching weather data: {e}", 500
@app.route('/hourly_weather')
def hourly_weather():
        weather_data = get_weather_data(lat,lon)
        return render_template("weather2.html", weather_data=weather_data)
@app.route('/schemes', methods=['GET', 'POST'])
def schemes():
    if request.method == 'POST':
        selected_state = request.form['state']
        schemes_data = government(selected_state) 
        return render_template('schemes.html', schemes=schemes_data, selected_state=selected_state)
    return render_template('schemes.html', schemes=None)
@app.route('/community',methods=['GET','POST'])
def community():
    posts=show_posts()
    if posts is None:
        return render_template('community.html',data=None,error="No posts yet")
    return render_template('community.html',data=posts,error=None)
@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        email = session.get('email') 
        if not email:
            return redirect(url_for('login'))
        msg=insert_post(title,description,email)
        return redirect(url_for('community'))
    return render_template('post.html')
@app.route('/trending',methods=['GET','POST'])
def trending():
    posts=trending_posts()
    print(posts)
    if posts is None:
        return render_template('community.html',data=None,error="No posts yet")
    return render_template('community.html',data=posts,error=None)
@app.route('/add_comment', methods=['POST'])
def add_comment():
    if 'email' not in session:
        return jsonify({'error': 'User not logged in'}), 403
    data = request.get_json()
    post_id, comment, user_email = data.get('post_id'), data.get('comment'), session['email']
    result = add_comment_db(post_id, comment, user_email)
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
@app.route('/fetch_comments/<int:post_id>', methods=['GET'])
def fetch_comments(post_id):
    comments = fetch_comments_db(post_id)
    return jsonify(comments)
@app.route('/update_reaction/<int:post_id>', methods=['POST'])
def update_reaction(post_id):
    if 'email' not in session:
        return jsonify({'error': 'User not logged in'}), 403
    user_email = session['email']
    result = update_reaction_db(post_id, user_email)
    if result == "already_liked":
        return jsonify({'error': 'You have already liked this post'}), 400 
    return jsonify({'likes': result})  # Return updated like count
@app.route('/market', methods=['GET', 'POST'])
def market():
    if request.method == 'POST':
        state = request.form.get('State')
        State = state.upper()
        data = fetch_market_data(State)
        if data.empty:
            error_message = f"No market data found for '{State}'."
            return render_template('market.html', data=None, error=error_message)
        data = data.drop(columns=['Arrivals', 'Traded'])
        return render_template('market.html', data=data, error=None)
    return render_template('market.html', data=None, error=None)
if __name__ == "__main__":
    app.run(debug=True)