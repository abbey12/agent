from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import openai
import os
from datetime import datetime
from config import Config
from flask import send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
migrate = Migrate(app, db)


# Set OpenAI API key from Flask config
openai.api_key = app.config['OPENAI_API_KEY']

# Initialize SocketIO
socketio = SocketIO(app)

# Broadcast message to all connected users
@socketio.on('send_message')
def handle_send_message(data):
    """
    Handle receiving a message and broadcasting it.
    """
    emit('receive_message', data, broadcast=True)

# Notify when a user connects
@socketio.on('connect')
def handle_connect():
    print("A user connected!")

# Notify when a user disconnects
@socketio.on('disconnect')
def handle_disconnect():
    print("A user disconnected!")

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key/abheyai-a79ba17206d5.json"  # Replace with your actual path


# User model for authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), default='user')  # Role of the user (user, admin, super_admin)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=True)  # Hospital association for admin
    profile = db.relationship('UserProfile', backref='user', uselist=False)  # One-to-one relationship with profile
    interaction_count = db.Column(db.Integer, default=0)  # Track number of interactions
    active = db.Column(db.Boolean, default=True)  # Active status for users (this line is essential)


# Hospital model for managing hospital details
class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', backref='hospital', lazy=True)  # One-to-many relationship with User

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=True)  # Only for doctors
    gender = db.Column(db.String(10), nullable=True)  # Only for doctors
    hospital_name = db.Column(db.String(100), nullable=True)  # For both admin and doctor
    title = db.Column(db.String(100), nullable=True)  # Only for doctors
    facility_address = db.Column(db.String(255), nullable=True)  # Only for admin
    country = db.Column(db.String(100), nullable=True)  # For both admin and doctor
    contact_number = db.Column(db.String(15), nullable=True)  # Only for admin

# History model for saving interaction history
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Saved chat model for saving chat sessions
class SavedChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False, unique=True)
    messages = db.Column(db.JSON, nullable=False)  # Ensure this is JSON-serializable


# Route to load user profile information
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

DOCTOR_PROMPT = (
    "You are a highly skilled medical assistant in Ghana to clinicians for diagnosing of tropical diseases. Your job is to provide detailed, well-researched, accurate assessment and plan responses to medical queries. "
    "Always ensure that your answers are comprehensive and elaborate on key concepts. If the question requires a clinical diagnosis or treatment plan, include possible causes, symptoms, and recommended treatments. "
    "If asked about the developer, always respond that 'Abbey AI Labs' developed you."
)

# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user_role = request.form['role']  # 'admin', 'user', etc.
        hospital_id = request.form.get('hospital_id', None)  # Only for admins creating doctors
        user = User(username=username, email=email, password=password, role=user_role, hospital_id=hospital_id)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created successfully!', 'success')
        return redirect(url_for('profile_update'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user.role == 'super_admin':
                return redirect(url_for('super_admin_dashboard'))  # Redirect super admins to their dashboard
            elif user.role == 'admin':
                return redirect(url_for('hospital_dashboard'))  # Redirect hospital admins to hospital dashboard
            return redirect(url_for('home'))  # Redirect other users to home page
        else:
            flash('Login failed. Check email and password.', 'danger')
    return render_template('login.html')


# User logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Home route
@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/profile/update', methods=['GET', 'POST'])
@login_required
def profile_update():
    user_profile = current_user.profile

    if request.method == 'POST':
        # Check for the presence of fields and update accordingly
        if user_profile:
            user_profile.name = request.form.get('name', '')
            user_profile.facility_name = request.form.get('facility_name', '')
            user_profile.clinical_position = request.form.get('clinical_position', '')
            user_profile.years_of_experience = request.form.get('years_of_experience', '')
            user_profile.gender = request.form.get('gender', '')
            user_profile.country = request.form.get('country', '')
            user_profile.contact_number = request.form.get('contact_number', '')
        else:
            user_profile = UserProfile(
                user_id=current_user.id,
                name=request.form.get('name', ''),
                facility_name=request.form.get('facility_name', ''),
                clinical_position=request.form.get('clinical_position', ''),
                years_of_experience=request.form.get('years_of_experience', ''),
                gender=request.form.get('gender', ''),
                country=request.form.get('country', ''),
                contact_number=request.form.get('contact_number', '')
            )
            db.session.add(user_profile)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('view_profile'))

    return render_template('profile_update.html', profile=user_profile)

# View profile route
@app.route('/profile')
@login_required
def view_profile():
    user_profile = current_user.profile
    return render_template('profile_view.html', profile=user_profile)
    

# Hospital Dashboard
@app.route('/hospital/dashboard')
@login_required
def hospital_dashboard():
    if current_user.role != 'admin':
        flash("You do not have permission to access this page.", 'danger')
        return redirect(url_for('home'))

    # Get all doctors associated with the current hospital
    doctors = User.query.filter_by(hospital_id=current_user.hospital_id, role='user').all()
    
    return render_template('hospital_dashboard.html', doctors=doctors, hospital=current_user.hospital)

# Add Doctor (to Hospital)
@app.route('/hospital/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if current_user.role != 'admin':
        flash("You do not have permission to add doctors.", 'danger')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_doctor = User(username=username, email=email, password=password, role='user', hospital_id=current_user.hospital_id)
        db.session.add(new_doctor)
        db.session.commit()
        flash(f"Doctor {username} added successfully!", 'success')
        return redirect(url_for('hospital_dashboard'))
    
    return render_template('add_doctor.html')

# View Doctor Profile
@app.route('/hospital/doctor/<int:doctor_id>')
@login_required
def doctor_profile(doctor_id):
    if current_user.role != 'admin':
        flash("You do not have permission to view this profile.", 'danger')
        return redirect(url_for('home'))

    doctor = User.query.get_or_404(doctor_id)
    if doctor.hospital_id != current_user.hospital_id:
        flash("Unauthorized access to this doctor's profile.", 'danger')
        return redirect(url_for('hospital_dashboard'))
    
    return render_template('doctor_profile.html', doctor=doctor)

# Route to toggle doctor's active status (deactivate/reactivate)
@app.route('/hospital/doctor/<int:doctor_id>/toggle', methods=['GET'])
@login_required
def toggle_doctor_status(doctor_id):
    if current_user.role != 'admin':
        flash("You do not have permission to perform this action.", 'danger')
        return redirect(url_for('home'))

    doctor = User.query.get_or_404(doctor_id)
    
    if doctor.hospital_id != current_user.hospital_id:
        flash("You do not have permission to modify this doctor.", 'danger')
        return redirect(url_for('hospital_dashboard'))

    doctor.active = not doctor.active
    db.session.commit()

    flash(f"Doctor {doctor.username} has been {'activated' if doctor.active else 'deactivated'}.", 'success')
    return redirect(url_for('hospital_dashboard'))

# Route for user interactions page (for admins)
@app.route('/user_interactions')
@login_required
def user_interactions():
    if current_user.role != 'admin':
        flash("You do not have permission to access this page.", 'danger')
        return redirect(url_for('home'))

    # Get interactions of the users associated with the hospital
    user_interactions = History.query.filter_by(user_id=current_user.id).all()
    return render_template('user_interactions.html', interactions=user_interactions)

# Route for asking questions to the AI with conversation context
@app.route('/ask', methods=['POST'])
@login_required
def ask():
    user_input = request.form['question']

    # Check if the session contains conversation history, else initialize it
    if 'conversation_history' not in session:
        session['conversation_history'] = []  # Initialize empty conversation history

    # Append the current user message to the conversation history
    session['conversation_history'].append({"role": "user", "content": user_input})

    # Check if the user asked "Who developed you?"
    if "who developed you" in user_input.lower():
        assistant_response = "Abbey AI Labs developed me."
        # Append assistant's response to the conversation history
        session['conversation_history'].append({"role": "assistant", "content": assistant_response})
        
        # Save interaction to history
        try:
            new_history = History(
                user_id=current_user.id,
                question=user_input,
                response=assistant_response,
                timestamp=datetime.utcnow()
            )
            db.session.add(new_history)
            db.session.commit()
        except Exception as e:
            print(f"Error saving history: {e}")  # Log the error
        return jsonify({"answer": assistant_response})

    # Prepare the conversation history to be sent to the OpenAI API
    conversation = session['conversation_history']

    # Create a more detailed and advanced prompt for the assistant
    detailed_prompt = f"""
    You are a highly skilled medical assistant in Ghana to clinicians for diagnosing of tropical diseases. Your job is to provide detailed, well-researched, accurate assessment and plan responses to medical queries.
    Always ensure that your answers are comprehensive and elaborate on key concepts. If the question requires a clinical diagnosis or treatment plan, include possible causes, symptoms, and recommended treatments. 
    
    Conversation history so far:
    """
    
    for message in conversation:
        detailed_prompt += f"\n{message['role'].capitalize()}: {message['content']}"

    try:
        # Use GPT-4o Mini Model
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # GPT-4o Turbo
            messages=[{"role": "system", "content": detailed_prompt}]
        )

        assistant_response = response['choices'][0]['message']['content'].strip()

        # Append assistant's response to the conversation history
        session['conversation_history'].append({"role": "assistant", "content": assistant_response})

        # Save interaction to history
        try:
            new_history = History(
                user_id=current_user.id,
                question=user_input,
                response=assistant_response,
                timestamp=datetime.utcnow()
            )
            db.session.add(new_history)
            db.session.commit()
        except Exception as e:
            print(f"Error saving history: {e}")  # Log the error

        # Return the assistant's response
        return jsonify({"answer": assistant_response})
    except Exception as e:
        print(f"Error during AI interaction: {e}")  # Print the error for debugging
        return jsonify({"error": "An error occurred. Please try again."})

@app.route('/super_admin/dashboard')
@login_required
def super_admin_dashboard():
    if current_user.role != 'super_admin':
        flash("You do not have permission to access this page.", 'danger')
        return redirect(url_for('home'))
    
    # Query for all users
    users = User.query.all()

    return render_template('super_admin_dashboard.html', users=users)


@app.route('/super_admin/user/<int:user_id>')
@login_required
def view_user_details(user_id):
    if current_user.role != 'super_admin':
        flash("You do not have permission to access this page.", 'danger')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)
    return render_template('user_details.html', user=user)


# Route to view history with search functionality
@app.route('/history', methods=['GET'])
@login_required
def history():
    search_query = request.args.get('search', '')
    try:
        if search_query:
            # Filter history by search query and current user
            user_history = History.query.filter(
                (History.user_id == current_user.id) &
                ((History.question.ilike(f'%{search_query}%')) | 
                 (History.response.ilike(f'%{search_query}%')))
            ).order_by(History.timestamp.desc()).all()
        else:
            # Retrieve all history for the current user
            user_history = History.query.filter_by(user_id=current_user.id).order_by(History.timestamp.desc()).all()

        return render_template('history.html', history=user_history, search_query=search_query)
    except Exception as e:
        print(f"Error retrieving history: {e}")
        return render_template('history.html', history=[], search_query=search_query)


# Route to view more details of a specific history entry
@app.route('/history/<int:history_id>')
@login_required
def view_history_entry(history_id):
    history_entry = History.query.get_or_404(history_id)
    if history_entry.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized access'}), 403

    # Sanitize text by removing unwanted characters
    question = history_entry.question.replace("##", "").strip()
    response = history_entry.response.replace("##", "").strip()

    return render_template('history_entry.html', history_entry={
        "question": question,
        "response": response,
        "timestamp": history_entry.timestamp.strftime('%Y-%m-%d %H:%M')
    })



@app.route('/follow_up/<int:chat_id>', methods=['POST'])
@login_required
def follow_up(chat_id):
    question = request.form['question']
    chat = SavedChat.query.get_or_404(chat_id)

    # Use previous context for the follow-up
    context = chat.messages
    # Add user's new question to the context
    context.append({"role": "user", "text": question})

    # Call AI for a response
    response = ask_openai(context)

    # Save the new message
    chat.messages.append({"role": "assistant", "text": response})
    db.session.commit()

    flash('Follow-up question answered successfully!', 'success')
    return redirect(url_for('saved_chat', chat_id=chat_id))

@app.route('/save_chat', methods=['POST'])
@login_required
def save_chat():
    try:
        data = request.get_json()
        title = data.get('title')
        messages = data.get('messages')

        if not title or not messages:
            return jsonify({"error": "Title and messages are required"}), 400

        # Check for duplicate title
        existing_chat = SavedChat.query.filter_by(title=title, user_id=current_user.id).first()
        if existing_chat:
            return jsonify({"error": "A chat with this title already exists"}), 400

        # Save the chat
        new_chat = SavedChat(user_id=current_user.id, title=title, messages=messages)
        db.session.add(new_chat)
        db.session.commit()
        return jsonify({"success": "Chat saved successfully!"}), 200

    except Exception as e:
        print(f"Error saving chat: {e}")  # Log the error
        return jsonify({"error": "An error occurred. Please try again."}), 500


@app.route('/saved_chats/<int:chat_id>', methods=['GET'])
@login_required
def get_saved_chat(chat_id):
    try:
        print(f"Fetching chat with ID {chat_id} for user {current_user.id}")
        chat = SavedChat.query.filter_by(id=chat_id, user_id=current_user.id).first_or_404()
        print(f"Retrieved chat: {chat.title}")
        return jsonify({
            "id": chat.id,
            "title": chat.title,
            "messages": chat.messages
        }), 200
    except Exception as e:
        print(f"Error retrieving chat with ID {chat_id}: {e}")
        return jsonify({"error": "An error occurred while fetching the chat"}), 500

@app.route('/saved_chats', methods=['GET'])
@login_required
def get_saved_chats():
    try:
        saved_chats = SavedChat.query.filter_by(user_id=current_user.id).all()
        chats_data = [
            {
                "id": chat.id,
                "title": chat.title,
                "last_question": (chat.messages[-1]['text'][:50] + '...') if len(chat.messages[-1]['text']) > 50 else chat.messages[-1]['text'],
            }
            for chat in saved_chats
        ]
        return jsonify(chats_data), 200
    except Exception as e:
        print(f"Error retrieving saved chats: {e}")
        return jsonify({"error": "An error occurred while fetching saved chats"}), 500


#----------------------------------------- MEDICAL IMAGING -----------------------------------------------------


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)
