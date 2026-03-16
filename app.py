
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "secretkey"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# -----------------------
# DATABASE MODELS
# -----------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))  # student or teacher


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.Text)
    subject_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    post_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    votes = db.Column(db.Integer, default=0)


# -----------------------
# CREATE DATABASE + SUBJECTS
# -----------------------

with app.app_context():

    db.create_all()

    if Subject.query.count() == 0:

        subjects = [
            "Data Structures",
            "DBMS",
            "Operating Systems",
            "Computer Networks"
        ]

        for s in subjects:
            db.session.add(Subject(name=s))

        db.session.commit()


# -----------------------
# ROUTES
# -----------------------

@app.route("/")
def landing():
    return render_template("landing.html")
@app.route("/home")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    subjects = Subject.query.all()

    return render_template(
        "dashboard.html",
        subjects=subjects
    )

# -----------------------
# REGISTER
# -----------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        hashed = generate_password_hash(password)

        user = User(
            username=username,
            password=hashed,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# -----------------------
# LOGIN
# -----------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            return redirect("/home")

    return render_template("login.html")


# -----------------------
# LOGOUT
# -----------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# -----------------------
# SUBJECT PAGE
# -----------------------

@app.route("/subject/<int:id>")
def subject(id):

    posts = Post.query.filter_by(subject_id=id).all()

    return render_template(
        "subject.html",
        posts=posts,
        subject=id
    )


# -----------------------
# CREATE POST
# -----------------------

@app.route("/create/<int:subject>", methods=["GET", "POST"])
def create_post(subject):

    if request.method == "POST":

        title = request.form["title"]
        body = request.form["body"]

        post = Post(
            title=title,
            body=body,
            subject_id=subject,
            user_id=session.get("user_id")
        )

        db.session.add(post)
        db.session.commit()

        return redirect(f"/subject/{subject}")

    return render_template(
        "create_post.html",
        subject=subject
    )


# -----------------------
# VIEW POST
# -----------------------

@app.route("/post/<int:id>", methods=["GET", "POST"])
def post(id):

    post = Post.query.get(id)

    if request.method == "POST":

        answer = request.form["answer"]

        new_answer = Answer(
            text=answer,
            post_id=id,
            user_id=session.get("user_id")
        )

        db.session.add(new_answer)
        db.session.commit()

    answers = Answer.query.filter_by(post_id=id).all()

    return render_template(
        "post.html",
        post=post,
        answers=answers
    )


# -----------------------
# VOTING
# -----------------------

@app.route("/vote/<int:id>/<action>")
def vote(id, action):

    ans = Answer.query.get(id)

    if action == "up":
        ans.votes += 1
    else:
        ans.votes -= 1

    db.session.commit()

    return redirect(request.referrer)


# -----------------------
# RUN SERVER
# -----------------------

if __name__ == "__main__":
    app.run(debug=True)

