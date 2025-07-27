import os
from flask import Flask, redirect, url_for, session, request, render_template_string, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID', 'your-google-client-id'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', 'your-google-client-secret'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    profile_pic = db.Column(db.String(250))

class UserInteraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    image_title = db.Column(db.String(200))
    interaction_type = db.Column(db.String(20), nullable=False)  # 'like', 'favorite', 'comment'
    content = db.Column(db.Text)  # For comments
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    user = db.relationship('User', backref=db.backref('interactions', lazy=True))

def get_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

@app.route('/')
def index():
    user = get_user()
    if user:
        # Serve the main application with user data
        return render_template_string(open('index.html').read(), user=user, logged_in=True)
    # Serve the main application without user data
    return render_template_string(open('index.html').read(), user=None, logged_in=False)

@app.route('/styles.css')
def styles():
    return send_from_directory('.', 'styles.css')

@app.route('/script.js')
def script():
    return send_from_directory('.', 'script.js')

@app.route('/dashboard')
def dashboard():
    user = get_user()
    if not user:
        return redirect(url_for('index'))
    return render_template_string('''
    <html>
    <head>
        <title>Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f6fb; margin: 0; }
            .container { max-width: 600px; margin: 40px auto; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px #ccc; padding: 32px; }
            .profile-pic { border-radius: 50%; width: 120px; margin-bottom: 16px; }
            .logout { color: #fff; background: #e74c3c; padding: 8px 16px; border: none; border-radius: 5px; text-decoration: none; }
            h2 { margin-top: 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <img src="{{user.profile_pic}}" class="profile-pic" alt="Profile Picture">
            <h2>Welcome, {{user.name}}!</h2>
            <p><b>Email:</b> {{user.email}}</p>
            <hr>
            <h3>Dashboard</h3>
            <p>This is your dashboard. More features coming soon!</p>
            <a href="/logout" class="logout">Logout</a>
        </div>
    </body>
    </html>
    ''', user=user)

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/authorize')
def authorize():
    token = oauth.google.authorize_access_token()
    resp = oauth.google.get('userinfo')
    user_info = resp.json()
    email = user_info['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=user_info.get('name'), profile_pic=user_info.get('picture'))
        db.session.add(user)
        db.session.commit()
    session['user_id'] = user.id
    return redirect(url_for('dashboard'))

@app.route('/profile')
def profile():
    user = get_user()
    if not user:
        return redirect(url_for('index'))
    
    # Get user's interactions
    likes = UserInteraction.query.filter_by(user_id=user.id, interaction_type='like').all()
    favorites = UserInteraction.query.filter_by(user_id=user.id, interaction_type='favorite').all()
    comments = UserInteraction.query.filter_by(user_id=user.id, interaction_type='comment').all()
    
    return render_template_string('''
    <html>
    <head>
        <title>{{user.name}}'s Profile</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f6fb; margin: 0; }
            .container { max-width: 800px; margin: 40px auto; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px #ccc; padding: 32px; }
            .profile-header { display: flex; align-items: center; gap: 20px; margin-bottom: 30px; }
            .profile-pic { border-radius: 50%; width: 120px; height: 120px; object-fit: cover; }
            .stats { display: flex; gap: 30px; margin-bottom: 30px; }
            .stat { text-align: center; }
            .stat-number { font-size: 24px; font-weight: bold; color: #2b6cb0; }
            .stat-label { color: #666; }
            .section { margin-bottom: 30px; }
            .section h3 { color: #2b6cb0; border-bottom: 2px solid #2b6cb0; padding-bottom: 10px; }
            .image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
            .image-item { border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px #ccc; }
            .image-item img { width: 100%; height: 150px; object-fit: cover; }
            .image-item .title { padding: 10px; font-size: 14px; color: #333; }
            .back-link { color: #2b6cb0; text-decoration: none; margin-bottom: 20px; display: inline-block; }
            .back-link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Home</a>
            
            <div class="profile-header">
                <img src="{{user.profile_pic}}" class="profile-pic" alt="Profile Picture">
                <div>
                    <h1>{{user.name}}</h1>
                    <p>{{user.email}}</p>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{{likes|length}}</div>
                    <div class="stat-label">Likes</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{{favorites|length}}</div>
                    <div class="stat-label">Favorites</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{{comments|length}}</div>
                    <div class="stat-label">Comments</div>
                </div>
            </div>
            
            <div class="section">
                <h3>Liked Images</h3>
                <div class="image-grid">
                    {% for like in likes %}
                    <div class="image-item">
                        <img src="{{like.image_url}}" alt="{{like.image_title}}">
                        <div class="title">{{like.image_title or 'Untitled'}}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="section">
                <h3>Favorited Images</h3>
                <div class="image-grid">
                    {% for fav in favorites %}
                    <div class="image-item">
                        <img src="{{fav.image_url}}" alt="{{fav.image_title}}">
                        <div class="title">{{fav.image_title or 'Untitled'}}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="section">
                <h3>Comments</h3>
                {% for comment in comments %}
                <div style="border: 1px solid #eee; padding: 15px; margin-bottom: 10px; border-radius: 5px;">
                    <img src="{{comment.image_url}}" style="width: 100px; height: 75px; object-fit: cover; border-radius: 5px; margin-right: 15px; float: left;">
                    <div>
                        <strong>{{comment.image_title or 'Untitled'}}</strong><br>
                        <em>"{{comment.content}}"</em><br>
                        <small>{{comment.created_at.strftime('%Y-%m-%d %H:%M')}}</small>
                    </div>
                    <div style="clear: both;"></div>
                </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    ''', user=user, likes=likes, favorites=favorites, comments=comments)

@app.route('/api/interact', methods=['POST'])
def interact():
    user = get_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    image_url = data.get('image_url')
    image_title = data.get('image_title', '')
    interaction_type = data.get('type')  # 'like', 'favorite', 'comment'
    content = data.get('content', '')
    
    if not image_url or not interaction_type:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if interaction already exists
    existing = UserInteraction.query.filter_by(
        user_id=user.id,
        image_url=image_url,
        interaction_type=interaction_type
    ).first()
    
    if existing:
        # Remove existing interaction (toggle off)
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'removed', 'interaction_type': interaction_type})
    else:
        # Add new interaction
        interaction = UserInteraction(
            user_id=user.id,
            image_url=image_url,
            image_title=image_title,
            interaction_type=interaction_type,
            content=content
        )
        db.session.add(interaction)
        db.session.commit()
        return jsonify({'status': 'added', 'interaction_type': interaction_type})

@app.route('/api/user/interactions')
def get_user_interactions():
    user = get_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    interaction_type = request.args.get('type')
    query = UserInteraction.query.filter_by(user_id=user.id)
    
    if interaction_type:
        query = query.filter_by(interaction_type=interaction_type)
    
    interactions = query.order_by(UserInteraction.created_at.desc()).all()
    
    return jsonify({
        'interactions': [{
            'id': i.id,
            'image_url': i.image_url,
            'image_title': i.image_title,
            'interaction_type': i.interaction_type,
            'content': i.content,
            'created_at': i.created_at.isoformat()
        } for i in interactions]
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False) 