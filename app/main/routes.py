from flask import render_template
from app.models import Product, ProductStatus
from . import main #this imports that main blueprint from __init__.py


@main.route('/')
@main.route('/home')
def index():
    # Do some stuff

    countries = [
    {'code':'TH','name':'Thailand'},
    {'code':'VN','name':'Vietnam'},
    {'code':'ID','name':'Indonesia'},
    {'code':'MY','name':'Malaysia'},
    {'code':'PH','name':'Philippines'},
    {'code':'SG','name':'Singapore'},
    ]

    categories = [
    {'slug':'snacks','name':'Snacks','emoji':'🍘'},
    {'slug':'fashion','name':'Fashion','emoji':'👗'},
    {'slug':'beauty','name':'Beauty','emoji':'💄'},
    {'slug':'home','name':'Home','emoji':'🏠'},
    {'slug':'crafts','name':'Crafts','emoji':'🧵'},
    {'slug':'coffee-tea','name':'Coffee & Tea','emoji':'☕'},
    ]
    featured_products = Product.query.filter_by(status=ProductStatus.LIVE).order_by(Product.created_at.desc()).limit(8).all()
    return render_template('main/index.html', countries=countries, categories=categories, featured_products=featured_products)