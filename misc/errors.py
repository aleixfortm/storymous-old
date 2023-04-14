from flask import render_template
from main import app


# handles typeError
@app.errorhandler(TypeError)
def handle_type_error(e):
    if e is None:
        error_message = 'An unknown error occurred'
    else:
        error_message = str(e)
    return render_template('404.html', error=error_message), 400


# handles valueError
@app.errorhandler(ValueError)
def handle_value_error(e):
    if e is None:
        error_message = 'An unknown error occurred'
    else:
        error_message = str(e)
    return render_template('400.html', error=error_message), 400


# handles notFoundError
@app.errorhandler(404)
def not_found_error(e):
    return render_template("404.html", error=e), 404

