from flask import Flask, redirect,render_template, request, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Usage

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"), method='sha256')

        if User.query.filter_by(email=email).first():
            return "User already exists"
        
        user = User(email=email,password=password)
        db.session.add(user)
        db.session.commit()
        
        return redirect("/login")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        
        return "Invalid credentials"
    
    return render_template("login.html")

@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        remaining = float(request.form["data"])
        usage = Usage(
            remaining_data=remaining,
            user_id=current_user.id
        )

        db.session.add(usage)
        db.session.commit()

    latest_usage = (
        Usage.query
        .filter_by(user_id=current_user.id)
        .order_by(Usage.updated_at.desc())
        .first()
    )

    return render_template(
        'dashboard.html',
        latest_usage=latest_usage
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()