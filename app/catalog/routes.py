from flask import render_template
from . import catalog #this imports that main blueprint from __init__.py

@catalog.route('/search')
def search():
    # temporary placeholder
    return "<h1>Search Page</h1><p>Coming soon...</p>"

@catalog.route('/c/<country>/')
def country(country):
    return f"<h1>Products from {country.title()}</h1><p>Coming soon...</p>"

@catalog.route('/c/<country>/<category>/')
def country_category(country, category):
    return f"<h1>{category.title()} from {country.title()}</h1><p>Coming soon...</p>"