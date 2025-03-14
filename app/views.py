import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.models import UserProfile
from app.forms import LoginForm, UploadForm


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Shamari McPherson")

@app.route('/login', methods=['POST', 'GET'])
def login():
    # Create an instance of the LoginForm (assuming it's a Flask-WTF form)
    form = LoginForm()

    # Check if the form is submitted and valid
    if form.validate_on_submit():
        # Query the database to find a user with the provided username
        user = UserProfile.query.filter_by(username=form.username.data).first()

        # If the user exists and the password matches, log the user in
        if user and check_password_hash(user.password, form.password.data):
            # Log the user in and store their session
            login_user(user)
            # Show a success message to the user
            flash('Logged in successfully!', 'success')
            # Redirect to the 'upload' page after successful login
            return redirect(url_for('upload'))
        else:
            # If the credentials are incorrect, show an error message
            flash('Invalid username or password', 'danger')

    # Render the login page with the form if the form isn't valid or hasn't been submitted
    return render_template('login.html', form=form)

@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    # Instantiate your form class
    form = UploadForm()
    # Validate file upload on submit
    if request.method == 'POST' and form.validate_on_submit():
        # Get file data and save to your uploads folder
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File Saved', 'success')
            print(f"Saving file to: {save_path}")
            file.save(save_path)
        else:
            flash('No file selected', 'danger')
        return redirect(url_for('files'))
    return render_template('upload.html', form=form)

def get_uploaded_images():
    # Helper function to iterate over the contents of the uploads folder and return filenames
    upload_folder = app.config['UPLOAD_FOLDER']
    filenames = []
    for subdir, dirs, files in os.walk(upload_folder):
        for file in files:
            # Ignore .DS_Store files
            if file == '.DS_Store':
                continue
            file_path = os.path.join(subdir, file)
            relative_path = os.path.relpath(file_path, upload_folder)
            filenames.append(relative_path)
    return filenames

@app.route('/uploads/<filename>')
@login_required
def get_image(filename):
    # View function to return a specific image from the upload folder
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)


@app.route('/files')
@login_required
def files():
    # Use the helper function to get uploaded image files
    files = get_uploaded_images()
    return render_template('files.html', files=files)


@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    # Log the user out
    logout_user()

    # Flash a message
    flash('You have been logged out successfully!', 'success')

    # Redirect to the home route
    return redirect(url_for('home'))

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
