from datetime import timedelta

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'nigger' #Put a more secure and politically correct key lol
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'  + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days = 1) #Arbitrary session hold selection

    CUSTOMER_COUNTRIES = ('BN', 'KH', 'ID', 'LA', 'MY', 'MM', 'PH', 'SG', 'TH', 'VN') # Adjust shipping destinations accordingly
    SUPPLIER_COUNTRIES = ('BN', 'KH', 'ID', 'LA', 'MY', 'MM', 'PH', 'SG', 'TH', 'VN') # Remove relevant countries accordingly

    # @app.route('/login', methods=['POST'])
    # def login():
    #     # after validating credentials
    #     session['user_id'] = user.id
    #     session.permanent = True  # activate the timeout
    #     return redirect(url_for('dashboard'))
