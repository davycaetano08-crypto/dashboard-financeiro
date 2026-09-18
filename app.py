import os
from datetime import datetime, date

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/ledgerly")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    transactions = db.relationship("Transaction", backref="user", lazy=True, cascade="all, delete-orphan")


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    kind = db.Column(db.String(12), nullable=False)  # income or expense
    occurred_on = db.Column(db.Date, nullable=False, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/")
def index():
    return redirect(url_for("dashboard" if current_user.is_authenticated else "login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").lower().strip()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name, an account identifier, and a password of at least 8 characters.", "error")
        elif User.query.filter_by(email=email).first():
            flash("An account already exists for that email. Please sign in.", "error")
        else:
            user = User(name=name, email=email, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("dashboard"))
    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, request.form.get("password", "")):
            login_user(user, remember=True)
            return redirect(url_for("dashboard"))
        flash("Incorrect email or password.", "error")
    return render_template("auth.html", mode="login")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.occurred_on.desc(), Transaction.id.desc()).all()
    income = sum(float(t.amount) for t in transactions if t.kind == "income")
    spending = sum(float(t.amount) for t in transactions if t.kind == "expense")
    categories = {}
    for item in transactions:
        if item.kind == "expense":
            categories[item.category] = categories.get(item.category, 0) + float(item.amount)
    return render_template("dashboard.html", transactions=transactions, income=income, spending=spending,
                           balance=income-spending, categories=categories)


def user_financials():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.occurred_on.desc(), Transaction.id.desc()).all()
    income = sum(float(item.amount) for item in transactions if item.kind == "income")
    spending = sum(float(item.amount) for item in transactions if item.kind == "expense")
    categories = {}
    for item in transactions:
        if item.kind == "expense":
            categories[item.category] = categories.get(item.category, 0) + float(item.amount)
    return transactions, income, spending, categories


@app.route("/activity")
@login_required
def activity():
    transactions, income, spending, _ = user_financials()
    return render_template("activity.html", transactions=transactions, income=income, spending=spending)


@app.route("/planning")
@login_required
def planning():
    _, income, spending, categories = user_financials()
    suggested_budget = income * 0.30 if income else 0
    return render_template("planning.html", income=income, spending=spending, categories=categories,
                           suggested_budget=suggested_budget)


@app.route("/transactions", methods=["POST"])
@login_required
def add_transaction():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "Other").strip() or "Other"
    kind = request.form.get("kind", "expense")
    try:
        amount = float(request.form.get("amount", "0"))
        occurred_on = datetime.strptime(request.form.get("occurred_on"), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        flash("Please enter a valid amount and date.", "error")
        return redirect(url_for("dashboard"))
    if not title or amount <= 0 or kind not in ("income", "expense"):
        flash("Complete the transaction details before saving.", "error")
        return redirect(url_for("dashboard"))
    if occurred_on > date.today():
        flash("Transactions cannot be dated in the future.", "error")
        return redirect(url_for("dashboard"))
    db.session.add(Transaction(title=title, category=category, amount=amount, kind=kind,
                               occurred_on=occurred_on, user_id=current_user.id))
    db.session.commit()
    flash("Transaction saved.", "success")
    return redirect(url_for("dashboard"))


@app.route("/transactions/<int:transaction_id>/edit", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):
    transaction = db.session.get(Transaction, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        abort(404)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "Other").strip() or "Other"
        kind = request.form.get("kind", "expense")
        try:
            amount = float(request.form.get("amount", "0"))
            occurred_on = datetime.strptime(request.form.get("occurred_on"), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            flash("Please enter a valid amount and date.", "error")
            return redirect(url_for("edit_transaction", transaction_id=transaction.id))
        if not title or amount <= 0 or kind not in ("income", "expense"):
            flash("Complete the transaction details before saving.", "error")
        elif occurred_on > date.today():
            flash("Transactions cannot be dated in the future.", "error")
        else:
            transaction.title = title
            transaction.category = category
            transaction.kind = kind
            transaction.amount = amount
            transaction.occurred_on = occurred_on
            db.session.commit()
            flash("Transaction updated.", "success")
            return redirect(url_for("activity"))
    return render_template("edit_transaction.html", transaction=transaction, today=date.today().isoformat())


@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Database tables created.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
