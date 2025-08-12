from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user
from . import auth #this imports that main blueprint from __init__.py
from .forms import LoginForm, RegistrationForm
from app.models import User, Customer, Supplier
from app.extensions import db

@auth.route('/login', methods = ['GET', 'POST'])
def login():

    login_form = LoginForm()

    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        remember = login_form.remember.data

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash("Logged in successfully!", "success")
            return redirect(url_for('dashboard.user_dashboard'))
        else:
            flash("Invalid email or password", "danger")

    return render_template('auth/login.html', form = login_form)


@auth.route('/register', methods=['GET', 'POST'])
def register():

    registration_form = RegistrationForm()

    # Check which button was clicked by looking at request.form
    if request.method == 'POST':

        registration_type = request.form.get('registration_type')

        if registration_form.validate_on_submit():
            email = registration_form.email.data
            password = registration_form.password.data
            first_name = registration_form.first_name.data
            last_name = registration_form.last_name.data

            # Create User
            user = User(
                email = email, 
                role = registration_type,
                first_name = first_name,
                last_name = last_name)
            user.set_password(password)

            db.session.add(user)
            db.session.flush() # Get user.id

            if registration_type == 'customer':

                customer = Customer(user_id=user.id)
                db.session.add(customer)
                db.session.commit()
                login_user(user)

                flash("Successfully registered as a customer!", "success")
                return redirect(url_for('dashboard.customer_dashboard'))

            elif registration_type == 'supplier':

                supplier = Supplier(user_id=user.id)
                db.session.add(supplier)
                db.session.commit()
                login_user(user)

                flash("Successfully registered as a supplier!", "success")
                return redirect(url_for('dashboard.supplier_dashboard'))

        else:
            flash("Please correct the errors in the form.", "danger")

    return render_template('auth/register.html', form=registration_form)


@auth.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.index'))