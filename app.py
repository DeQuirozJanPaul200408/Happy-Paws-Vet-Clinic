from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET', 'dev-secret-key')

# ----------------- CHANGE TO MYSQL -----------------
# Make sure you have created a database named 'vetclinic' in MySQL
# Replace 'root', '', and 'localhost' if needed
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/vetclinic'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ---------------------------------------------------

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

csrf = CSRFProtect(app)

# ------------------- MODELS -------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(128), nullable=False)  # change from password_hash to password
    pets = db.relationship('Pet', backref='owner', lazy=True)
    appointments = db.relationship('Appointment', backref='owner', lazy=True)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    breed = db.Column(db.String(80))
    age = db.Column(db.Integer)
    medical_history = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointments = db.relationship('Appointment', backref='pet', lazy=True, cascade="all, delete")

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service = db.Column(db.String(120), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(30), default='Scheduled')

SERVICES = [
    {'title': 'Wellness Checkup', 'desc': 'Routine physical exam and health check.'},
    {'title': 'Vaccination', 'desc': 'Core vaccines and booster shots.'},
    {'title': 'Surgery', 'desc': 'Minor surgical procedures.'},
]

STAFF = [
    {'name': 'Jan Paul E. De Quiroz', 'role': 'Senior Veterinarian', 'bio': 'Expert in animal health and wellness with years of dedicated service.'},
    {'name': 'Danniel John Morales', 'role': 'Veterinarian', 'bio': 'Specializes in surgery and compassionate pet care.'}, 
    {'name': 'Zuriel Pecadero', 'role': 'Help Desk.', 'bio': 'Helps you for your inquiries.'},
]

# ------------------- FORMS -------------------
class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(2, 80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(6, 128)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PetForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    breed = StringField('Breed', validators=[Optional()])
    age = IntegerField('Age', validators=[Optional()])
    medical_history = TextAreaField('Medical History', validators=[Optional()])
    submit = SubmitField('Save')

class AppointmentForm(FlaskForm):
    pet_id = SelectField('Pet', coerce=int, validators=[DataRequired()])
    service = SelectField('Service', choices=[(s['title'], s['title']) for s in SERVICES])
    scheduled_at = DateTimeField('When', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables_once():
    if not getattr(app, 'db_initialized', False):
        db.create_all()
        app.db_initialized = True

# ------------------- ROUTES -------------------
@app.route('/')
def index():
    return render_template('index.html', services=SERVICES, staff=STAFF)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'warning')
            return redirect(url_for('register'))
        user = User(name=form.name.data, email=form.email.data, password=form.password.data)  # store plain password
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # compare directly
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', pets=current_user.pets, appointments=current_user.appointments)

@app.route('/pets')
@login_required
def pets_list():
    return render_template('pets.html', pets=current_user.pets)

@app.route('/pets/new', methods=['GET', 'POST'])
@login_required
def pet_new():
    form = PetForm()
    if form.validate_on_submit():
        pet = Pet(name=form.name.data, breed=form.breed.data, age=form.age.data,
                  medical_history=form.medical_history.data, owner=current_user)
        db.session.add(pet)
        db.session.commit()
        flash('Pet added successfully.', 'success')
        return redirect(url_for('pets_list'))
    return render_template('pet_form.html', form=form, title='Add Pet', form_action=url_for('pet_new'))

@app.route('/pets/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def pet_edit(id):
    pet = Pet.query.get_or_404(id)
    if pet.owner != current_user:
        abort(403)
    form = PetForm(obj=pet)
    if form.validate_on_submit():
        pet.name = form.name.data
        pet.breed = form.breed.data
        pet.age = form.age.data
        pet.medical_history = form.medical_history.data
        db.session.commit()
        flash('Pet updated successfully!', 'success')
        return redirect(url_for('pets_list'))
    return render_template('pet_form.html', form=form, title='Edit Pet', form_action=url_for('pet_edit', id=id))

@app.route('/pets/<int:id>/delete', methods=['POST'])
@login_required
@csrf.exempt
def pet_delete(id):
    pet = Pet.query.get_or_404(id)
    if pet.owner != current_user:
        abort(403)
    db.session.delete(pet)
    db.session.commit()
    flash('Pet deleted successfully!', 'info')
    return redirect(url_for('pets_list'))

@app.route('/appointments')
@login_required
def appointments_list():
    appts = Appointment.query.filter_by(owner_id=current_user.id).all()
    return render_template('appointments.html', appointments=appts)

@app.route('/appointments/new', methods=['GET', 'POST'])
@login_required
def appointment_new():
    form = AppointmentForm()
    form.pet_id.choices = [(p.id, p.name) for p in current_user.pets]
    if not form.pet_id.choices:
        flash('Add a pet first.', 'warning')
        return redirect(url_for('pet_new'))

    if form.validate_on_submit():
        appt = Appointment(
            pet_id=form.pet_id.data,
            owner_id=current_user.id,
            service=form.service.data,
            scheduled_at=form.scheduled_at.data,
            notes=form.notes.data
        )
        db.session.add(appt)
        db.session.commit()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointments_list'))

    return render_template('appointment_form.html', form=form, title='Book Appointment',
                           form_action=url_for('appointment_new'))

@app.route('/appointments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def appointment_edit(id):
    appt = Appointment.query.get_or_404(id)
    if appt.owner != current_user:
        abort(403)

    form = AppointmentForm(obj=appt)
    form.pet_id.choices = [(p.id, p.name) for p in current_user.pets]

    if request.method == 'GET':
        form.scheduled_at.data = appt.scheduled_at

    if form.validate_on_submit():
        appt.pet_id = form.pet_id.data
        appt.service = form.service.data
        appt.scheduled_at = form.scheduled_at.data
        appt.notes = form.notes.data
        db.session.commit()
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('appointments_list'))

    return render_template('appointment_form.html', form=form, title='Edit Appointment',
                           form_action=url_for('appointment_edit', id=id))

@app.route('/appointments/<int:id>/delete', methods=['POST'])
@login_required
@csrf.exempt
def appointment_delete(id):
    appt = Appointment.query.get_or_404(id)
    if appt.owner != current_user:
        abort(403)
    db.session.delete(appt)
    db.session.commit()
    flash('Appointment deleted successfully!', 'info')
    return redirect(url_for('appointments_list'))

@app.route('/services')
def services():
    return render_template('services.html', services=SERVICES)

@app.route('/staff')
def staff():
    return render_template('staff.html', staff=STAFF)

if __name__ == '__main__':
    app.run(debug=True)
