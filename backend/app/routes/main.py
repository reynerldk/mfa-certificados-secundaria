from flask import Blueprint, render_template

bp = Blueprint('main', __name__) 

@bp.route('/')
def serve_frontend():
    """Sirve el archivo index.html para la ruta raíz."""
    return render_template('index.html')


