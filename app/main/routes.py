from flask import render_template
from app.models import Product
from . import main #this imports that main blueprint from __init__.py


@main.route('/')
@main.route('/home')
def index():
    # Do some stuff

    countries = [
    {'code':'thailand','name':'Thailand'},
    {'code':'vietnam','name':'Vietnam'},
    {'code':'indonesia','name':'Indonesia'},
    {'code':'malaysia','name':'Malaysia'},
    {'code':'philippines','name':'Philippines'},
    {'code':'singapore','name':'Singapore'},
    ]

    categories = [
    {'slug':'snacks','name':'Snacks','emoji':'🍘'},
    {'slug':'fashion','name':'Fashion','emoji':'👗'},
    {'slug':'beauty','name':'Beauty','emoji':'💄'},
    {'slug':'home','name':'Home','emoji':'🏠'},
    {'slug':'crafts','name':'Crafts','emoji':'🧵'},
    {'slug':'coffee-tea','name':'Coffee & Tea','emoji':'☕'},
    ]
    featured_products = Product.query.filter_by(is_active=True).order_by(Product.date_added.desc()).limit(8).all()
    return render_template('main/index.html', countries=countries, categories=categories, featured_products=featured_products)