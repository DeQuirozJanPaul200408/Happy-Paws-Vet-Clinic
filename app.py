
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

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/vetclinic'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

csrf = CSRFProtect(app)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# ------------------- MODELS -------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    pets = db.relationship('Pet', backref='owner', lazy=True, cascade="all, delete-orphan")
    appointments = db.relationship('Appointment', backref='owner', lazy=True, cascade="all, delete-orphan")


class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    breed = db.Column(db.String(80))
    age = db.Column(db.Integer)
    medical_history = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    appointments = db.relationship('Appointment', backref='pet', lazy=True, cascade="all, delete-orphan")


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id', ondelete='CASCADE'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    service = db.Column(db.String(120), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(30), default='Scheduled')


SERVICES = [
    {
        'title': 'Wellness Checkup',
        'desc': 'Routine physical exam and health check.',
        'price': '₱500'
    },
    {
        'title': 'Vaccination',
        'desc': 'Core vaccines and booster shots.',
        'price': '₱800'
    },
    {
        'title': 'Surgery',
        'desc': 'Minor surgical procedures.',
        'price': '₱3,000'
    },
    {
        'title': 'Deworming',
        'desc': 'Eliminates intestinal worms and parasites.',
        'price': '₱350'
    },
    {
        'title': 'Dental Cleaning',
        'desc': 'Removes tartar and improves oral health.',
        'price': '₱1,200'
    },
    {
        'title': 'Grooming',
        'desc': 'Basic grooming, nail trimming, and bathing.',
        'price': '₱600'
    },
]

STAFF = [
    {
        'name': 'Jan Paul E. De Quiroz', 'role': 'Senior Veterinarian', 'bio': 'Expert in animal health and wellness with years of dedicated service.'
    },

    {
        'name': 'Danniel John Morales', 'role': 'Veterinarian', 'bio': 'Specializes in surgery and compassionate pet care.'
    }, 

    {
        'name': 'Zuriel Pecadero', 'role': 'Help Desk', 'bio': 'Helps you with your inquiries.'
    },

    {
        'name': 'Kim Tomotorgo', 'role': 'Wellness Veterinarian', 'bio': 'Focused on Wellness Checkups and ensuring pets maintain optimal health.'
        
    },

    {
        'name': 'Vanessa Ofrancia', 'role': 'Veterinary Nurse', 'bio': 'Specializes in Vaccination and preventive care to keep pets safe from diseases.'
    },

    {
        'name': 'Irish Rocha', 'role': 'Veterinary Surgical Nurse', 'bio': 'Assists in Surgery and post-operative care with precision and compassion.'
    },

    {
        'name': 'Ellemar Pundavela', 'role': 'Preventive Care Specialist', 'bio': 'Specializes in Deworming and preventive pet treatments.'
    },

    {
        'name': 'Ruffaina Hamsain', 'role': 'Dental Care Specialist', 'bio': 'Expert in Dental Cleaning and oral care for pets.'
    },

    {
        'name': 'Rose Ann Tolentino', 'role': 'Grooming Specialist', 'bio': 'Specializes in Grooming and maintaining pet hygiene.'
    }
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
        # Create default admin user if not exists
        if not User.query.filter_by(email='administrator@gmail.com').first():
            admin_user = User(name='Admin', email='administrator@gmail.com', password='admin123', role='admin')
            db.session.add(admin_user)
            db.session.commit()
        app.db_initialized = True

# ------------------- ROUTES -------------------
@app.route('/')
def index():
    return render_template('index.html', services=SERVICES, staff=STAFF)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request
        form = RegistrationForm()
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                return {'success': False, 'message': 'Email already registered.'}
            user = User(name=form.name.data, email=form.email.data, password=form.password.data)  # store plain password
            db.session.add(user)
            db.session.commit()
            return {'success': True, 'message': 'Registration successful!'}
        else:
            return {'success': False, 'message': 'Please fill in all fields correctly.'}
    else:
        # Regular GET request
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
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.password == form.password.data:  # compare directly
                login_user(user)
                return {'success': True, 'message': 'Login successful!'}
            else:
                return {'success': False, 'message': 'Invalid credentials.'}
        else:
            return {'success': False, 'message': 'Please fill in all fields correctly.'}
    else:
        # Regular GET request
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.password == form.password.data:  # compare directly
                login_user(user)
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
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
    # fetch user's appointments and pets
    appointments = sorted(current_user.appointments, key=lambda x: x.scheduled_at)  # sort by date
    pets = current_user.pets

    # Numeric prices (no currency symbols)
    service_prices = {
        'Wellness Checkup': 500.0,
        'Vaccination': 800.0,
        'Surgery': 3000.0,
        'Deworming': 350.0,
        'Dental Cleaning': 1200.0,
        'Grooming': 600.0
    }

    # Attach a numeric price to each appointment object for use in the template
    for a in appointments:
        # default to 0.0 if service not found
        a.price = float(service_prices.get(a.service, 0.0))

    # Compute subtotal, VAT and total (rounded to 2 decimals)
    subtotal = sum(a.price for a in appointments)
    vat = round(subtotal * 0.12, 2)
    total_payable = round(subtotal + vat, 2)
    subtotal = round(subtotal, 2)

    return render_template(
        'dashboard.html',
        pets=pets,
        appointments=appointments,
        subtotal=subtotal,
        vat=vat,
        total_payable=total_payable,
        title='Dashboard'
    )

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
    appointments = Appointment.query.filter_by(owner_id=current_user.id).order_by(Appointment.scheduled_at).all()

    # Define the service prices (base prices)
    service_prices = {
        'Wellness Checkup': 500.0,
        'Vaccination': 800.0,
        'Surgery': 3000.0,
        'Deworming': 350.0,
        'Dental Cleaning': 1200.0,
        'Grooming': 600.0
    }

    # Attach prices and total payable to each appointment
    for a in appointments:
        a.price = float(service_prices.get(a.service, 0.0))
        a.total_payable = round(a.price * 1.12, 2)

    # Compute subtotal, VAT (12%), and total payable
    subtotal = sum(a.price for a in appointments)
    vat = round(subtotal * 0.12, 2)
    total_payable = round(subtotal + vat, 2)

    return render_template(
        'appointments.html',
        appointments=appointments,
        subtotal=subtotal,
        vat=vat,
        total_payable=total_payable
    )

@app.route('/appointments/new', methods=['GET', 'POST'])
@login_required
def appointment_new():
    form = AppointmentForm()
    form.pet_id.choices = [(p.id, p.name) for p in current_user.pets]
    if not form.pet_id.choices:
        flash('Add a pet first.', 'warning')
        return redirect(url_for('pet_new'))

    if form.validate_on_submit():
        now = datetime.now()
        scheduled_date = form.scheduled_at.data

        # Prevent scheduling for today or past days
        if scheduled_date.date() <= now.date():
            flash('You cannot schedule an appointment for today or past dates. Please choose a future date.', 'danger')
            return render_template('appointment_form.html', form=form, title='Book Appointment',
                                   form_action=url_for('appointment_new'))

        # Validate clinic hours
        weekday = scheduled_date.weekday()  # 0=Mon, 1=Tue, ..., 6=Sun
        time = scheduled_date.time()

        if weekday == 6:  # Sunday
            flash('Appointments are not available on Sundays as it is for emergency only. Please choose another day.', 'danger')
            return render_template('appointment_form.html', form=form, title='Book Appointment',
                                   form_action=url_for('appointment_new'))
        elif weekday == 5:  # Saturday
            if not (time >= datetime.strptime('09:00', '%H:%M').time() and time <= datetime.strptime('16:00', '%H:%M').time()):
                flash('On Saturdays, appointments are only available from 9:00 AM to 4:00 PM. Please choose a valid time.', 'danger')
                return render_template('appointment_form.html', form=form, title='Book Appointment',
                                       form_action=url_for('appointment_new'))
        else:  # Monday to Friday
            if time >= datetime.strptime('18:00', '%H:%M').time() or time <= datetime.strptime('07:59', '%H:%M').time():
                flash('On weekdays (Monday to Friday), appointments are not available from 6:00 PM to 7:59 AM. Please choose a valid time.', 'danger')
                return render_template('appointment_form.html', form=form, title='Book Appointment',
                                       form_action=url_for('appointment_new'))

        appt = Appointment(
            pet_id=form.pet_id.data,
            owner_id=current_user.id,
            service=form.service.data,
            scheduled_at=scheduled_date,
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
        now = datetime.now()
        scheduled_date = form.scheduled_at.data

        # Prevent editing to today or past
        if scheduled_date.date() <= now.date():
            flash('You cannot set the appointment to today or a past date. Please choose a future date.', 'danger')
            return render_template('appointment_form.html', form=form, title='Edit Appointment',
                                   form_action=url_for('appointment_edit', id=id))

        # Validate clinic hours
        weekday = scheduled_date.weekday()  # 0=Mon, 1=Tue, ..., 6=Sun
        time = scheduled_date.time()

        if weekday == 6:  # Sunday
            flash('Appointments are not available on Sundays as it is for emergency only. Please choose another day.', 'danger')
            return render_template('appointment_form.html', form=form, title='Edit Appointment',
                                   form_action=url_for('appointment_edit', id=id))
        elif weekday == 5:  # Saturday
            if not (time >= datetime.strptime('09:00', '%H:%M').time() and time <= datetime.strptime('16:00', '%H:%M').time()):
                flash('On Saturdays, appointments are only available from 9:00 AM to 4:00 PM. Please choose a valid time.', 'danger')
                return render_template('appointment_form.html', form=form, title='Edit Appointment',
                                       form_action=url_for('appointment_edit', id=id))
        else:  # Monday to Friday
            if time >= datetime.strptime('18:00', '%H:%M').time() or time <= datetime.strptime('07:59', '%H:%M').time():
                flash('On weekdays (Monday to Friday), appointments are not available from 6:00 PM to 7:59 AM. Please choose a valid time.', 'danger')
                return render_template('appointment_form.html', form=form, title='Edit Appointment',
                                       form_action=url_for('appointment_edit', id=id))

        appt.pet_id = form.pet_id.data
        appt.service = form.service.data
        appt.scheduled_at = scheduled_date
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

# ------------------- ADMIN ROUTES -------------------
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_pets = Pet.query.count()
    total_appointments = Appointment.query.count()

    # Calculate total payable for all scheduled appointments
    service_prices = {
        'Wellness Checkup': 500.0,
        'Vaccination': 800.0,
        'Surgery': 3000.0,
        'Deworming': 350.0,
        'Dental Cleaning': 1200.0,
        'Grooming': 600.0
    }

    appointments = Appointment.query.all()
    subtotal = sum(float(service_prices.get(a.service, 0.0)) for a in appointments)
    vat = round(subtotal * 0.12, 2)
    total_payable = round(subtotal + vat, 2)

    return render_template('admin_dashboard.html', total_users=total_users, total_pets=total_pets, total_appointments=total_appointments, total_payable=total_payable)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_user_edit(id):
    user = User.query.get_or_404(id)
    form = RegistrationForm(obj=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.password = form.password.data  # plain text
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin_user_form.html', form=form, title='Edit User', form_action=url_for('admin_user_edit', id=id))

@app.route('/admin/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def admin_user_delete(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Cannot delete yourself.', 'danger')
        return redirect(url_for('admin_users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'info')
    return redirect(url_for('admin_users'))

@app.route('/admin/pets')
@login_required
@admin_required
def admin_pets():
    pets = Pet.query.all()
    return render_template('admin_pets.html', pets=pets)

@app.route('/admin/appointments')
@login_required
@admin_required
def admin_appointments():
    appointments = Appointment.query.order_by(Appointment.scheduled_at).all()

    # Define the service prices (base prices)
    service_prices = {
        'Wellness Checkup': 500.0,
        'Vaccination': 800.0,
        'Surgery': 3000.0,
        'Deworming': 350.0,
        'Dental Cleaning': 1200.0,
        'Grooming': 600.0
    }

    # Attach prices and total payable to each appointment
    for a in appointments:
        price = float(service_prices.get(a.service, 0.0))
        a.price = price
        a.total_payable = round(price * 1.12, 2)  # 12% VAT

    return render_template('admin_appointments.html', appointments=appointments)

@app.route('/admin/appointments/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def admin_appointment_delete(id):
    appointment = Appointment.query.get_or_404(id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment deleted successfully.', 'info')
    return redirect(url_for('admin_appointments'))

@app.route('/admin/pets/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
@csrf.exempt
def admin_pet_delete(id):
    pet = Pet.query.get_or_404(id)
    db.session.delete(pet)
    db.session.commit()
    flash('Pet deleted successfully.', 'info')
    return redirect(url_for('admin_pets'))

if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT", 5000)))