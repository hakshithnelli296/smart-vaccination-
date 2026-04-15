import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from models import db, User, Child, VaccineRecord
from vaccine_data import generate_vaccine_records

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Database Initialization ---
with app.app_context():
    db.create_all()

# --- Auth Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        flash('Account created successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check username and password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Main Routes ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    children = Child.query.filter_by(user_id=current_user.id).all()
    today = datetime.date.today()
    
    total_vaccines = 0
    completed_vaccines = 0
    pending_vaccines = 0
    overdue_vaccines = 0
    
    upcoming_list = []
    
    for child in children:
        records = VaccineRecord.query.filter_by(child_id=child.id).all()
        for r in records:
            total_vaccines += 1
            if r.completed:
                completed_vaccines += 1
            else:
                pending_vaccines += 1
                if r.due_date < today:
                    overdue_vaccines += 1
                elif (r.due_date - today).days <= 30:
                    upcoming_list.append(r)
    
    # Sort upcoming by due date
    upcoming_list.sort(key=lambda x: x.due_date)
    upcoming_list = upcoming_list[:5] # Top 5
    
    stats = {
        'total': total_vaccines,
        'completed': completed_vaccines,
        'pending': pending_vaccines,
        'overdue': overdue_vaccines,
        'completion_percentage': int((completed_vaccines / total_vaccines) * 100) if total_vaccines > 0 else 0
    }
    
    return render_template('dashboard.html', children=children, stats=stats, upcoming=upcoming_list, today=today)

@app.route('/children', methods=['GET', 'POST'])
@login_required
def manage_children():
    if request.method == 'POST':
        name = request.form.get('name')
        dob_str = request.form.get('dob')
        gender = request.form.get('gender')
        
        dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()
        
        new_child = Child(name=name, dob=dob, gender=gender, user_id=current_user.id)
        db.session.add(new_child)
        db.session.flush() # To get the new_child.id
        
        # Generate vaccine records automatically
        records = generate_vaccine_records(new_child)
        db.session.add_all(records)
        db.session.commit()
        
        flash('Child profile added successfully!', 'success')
        return redirect(url_for('manage_children'))
        
    children = Child.query.filter_by(user_id=current_user.id).all()
    return render_template('children.html', children=children)

@app.route('/child/<int:child_id>/timeline')
@login_required
def timeline(child_id):
    child = Child.query.get_or_404(child_id)
    if child.user_id != current_user.id:
        return "Unauthorized", 403
        
    records = VaccineRecord.query.filter_by(child_id=child.id).order_by(VaccineRecord.due_date).all()
    today = datetime.date.today()
    
    return render_template('timeline.html', child=child, records=records, today=today)

@app.route('/vaccine/<int:record_id>/update', methods=['POST'])
@login_required
def update_vaccine(record_id):
    record = VaccineRecord.query.get_or_404(record_id)
    child = Child.query.get(record.child_id)
    
    if child.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    completed = data.get('completed', False)
    
    record.completed = completed
    if completed:
        record.completed_date = datetime.date.today()
    else:
        record.completed_date = None
        
    db.session.commit()
    return jsonify({"success": True})

# --- API for AI Chatbot ---
@app.route('/api/chat', methods=['POST'])
def chat():
    # Simple rule-based chatbot endpoint
    data = request.get_json()
    user_message = data.get('message', '').lower()
    
    response = "I'm a simple AI assistant. Please ask about vaccines, schedules, or side effects."
    
    if "fever" in user_message or "side effect" in user_message:
        response = "A mild fever or redness at the injection site is common after vaccination. If the fever is high or lasts more than a few days, please consult your pediatrician."
    elif "when" in user_message and "flu" in user_message:
        response = "The Influenza (flu) vaccine is recommended yearly for everyone 6 months and older."
    elif "hpv" in user_message:
        response = "The HPV vaccine is typically given in a 2-dose series starting at age 11-12 years."
    elif "schedule" in user_message or "how many" in user_message:
        response = "The standard schedule involves several vaccines in the first 18 months, with boosters around age 4-6 and 11-12. Please check your child's timeline for specifics."
        
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
