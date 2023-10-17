from flask import Blueprint, render_template

# Create a blueprint
bp = Blueprint('home', __name__)


@bp.route('/')
def home():
    return render_template('homepage.html')
