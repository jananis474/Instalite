from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, session, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Uploads'
app.secret_key = 'supersecretkey'  # Set a secret key for session management

# Create uploads folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# DB setup
def init_db():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        bio TEXT,
                        profile_picture TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        image TEXT,
                        caption TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS comments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER,
                        user_id INTEGER,
                        text TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS likes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER,
                        user_id INTEGER
                    )''')
        conn.commit()

@app.route('/')
def index():
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM posts ORDER BY timestamp DESC")
        posts = c.fetchall()
        posts_data = []
        for post in posts:
            c.execute("SELECT COUNT(*) FROM likes WHERE post_id=?", (post[0],))
            like_count = c.fetchone()[0]
            c.execute("SELECT text FROM comments WHERE post_id=?", (post[0],))
            comments = c.fetchall()
            posts_data.append((post, like_count, comments))
    return render_template('index.html', posts=posts_data)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        image = request.files['image']
        caption = request.form['caption']
        path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(path)
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("INSERT INTO posts (image, caption) VALUES (?, ?)", (image.filename, caption))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('post.html')

@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    text = request.form['comment']
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO comments (post_id, text) VALUES (?, ?)", (post_id, text))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/like/<int:post_id>', methods=['POST'])
def like(post_id):
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO likes (post_id) VALUES (?)", (post_id,))
        conn.commit()
    return jsonify({'status': 'success'})

@app.route('/Uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return "Username already taken!"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if not username or not password:
            flash('Username and password cannot be empty.', 'error')
            return render_template('login.html')
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            if user:
                session['user_id'] = user[0]
                session['username'] = username
                flash('Logged in successfully!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid credentials!', 'error')
                return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    username = session['username']

    # Get user's posts
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT bio, profile_picture FROM users WHERE id=?", (user_id,))
        user_info = c.fetchone()
        bio = user_info[0]
        profile_picture = user_info[1]

        # Get user's posts
        c.execute("SELECT * FROM posts WHERE user_id=?", (user_id,))
        posts = c.fetchall()

    return render_template('profile.html', username=username, bio=bio, profile_picture=profile_picture, posts=posts)

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect("database.db") as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('''SELECT posts.id, posts.image, posts.caption, posts.user_id, users.username 
                     FROM posts JOIN users ON posts.user_id = users.id 
                     ORDER BY posts.id DESC''')
        posts = c.fetchall()

    return render_template('home.html', posts=posts)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    with sqlite3.connect("database.db") as conn:
        c = conn.cursor()
        c.execute("SELECT user_id, image FROM posts WHERE id = ?", (post_id,))
        post = c.fetchone()

        if post and post[0] == user_id:
            # Optionally delete the image file too (be careful)
            image_path = post[1]
            try:
                import os
                os.remove(image_path)
            except:
                pass

            c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            conn.commit()

    return redirect(url_for('home'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    if request.method == 'POST':
        bio = request.form['bio']
        profile_picture = request.form['profile_picture']  # You can add an image upload functionality here

        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET bio=?, profile_picture=? WHERE id=?", (bio, profile_picture, user_id))
            conn.commit()
        
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)