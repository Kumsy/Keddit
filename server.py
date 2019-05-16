"""keddit! The second to the frontpage of the internet."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, url_for
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, Users, Community, CommunityMembers, Threads, ThreadRatings, Comments, CommentRatings
from forms import RegistrationForm, LoginForm
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user

app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

#Handle User Logins
@login_manager.user_loader
def load_user(user_id):
    print("LOAD USER")
    print(user_id)
    return Users.query.get(user_id)


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/registration', methods=['GET', 'POST'])
def register_form():
    """Show form for user signup."""

    # Set form to our RegistrationForm() class from forms.py
    form = RegistrationForm()

    # When form submitted, add user to our database from our model.py classes
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(username=form.username.data, email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! Please log in.', 'sucess')
        return redirect('/login')
    
    return render_template("registration.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Show login form."""
    form = LoginForm()

    # When user submits login. Query for email data, validate, and check password.
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        print(user)
        print('DEBUGGGGGGGGGGGGG TESTSSSSSSSSSSSS')
        if user and bcrypt.check_password_hash(user.password, form.password.data):

            login_user(user, remember=form.remember.data)
            print(user)
            print("HEY LOOK AT MEEEEEEEEEE")
            flash("You are now logged in!")

            # Create session THIS DOES NOT WORK WHILE USING FLASK-LOGIN
            # username = user.username
            # session['user_id'] = user.user_id
            return redirect("/")
        else:
            flash('Login Unsucessful. Please check email and password.',
                                                                    'danger')
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    """Log out."""

    del session['user_id']
    flash("Logged Out. Hope to see you again!")
    return redirect("/")




# When you make account page add this orignally from login route.
# username = user.username

#     session['user_id'] = user.user_id
#     flash("Logged in")
#     return redirect(f"/u/{user.username}")










#____________________________________________________________

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)
    login_manager.init_app(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")