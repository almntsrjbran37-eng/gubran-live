from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"  # مفتاح سرّي للتطبيق
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# نموذج المستخدم في قاعدة البيانات
class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(150), unique=True, nullable=False)
  password = db.Column(db.String(150), nullable=False)
  balance = db.Column(db.Integer, default=100)  # رصيد افتراضي للمستخدم


@login_manager.user_loader
def load_user(user_id):
  return db.session.get(User, int(user_id))


# إنشاء جداول قاعدة البيانات تلقائياً
with app.app_context():
  db.create_all()


# الصفحة الرئيسية (البث)
@app.route("/")
@login_required
def index():
  return render_template("index.html")


# صفحة الملف الشخصي
@app.route("/profile")
@login_required
def profile():
  return render_template("profile.html", user=current_user)


# مسار تسجيل الحساب الجديد
@app.route("/register", methods=["GET", "POST"])
def register():
  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
      return "اسم المستخدم هذا موجود مسبقاً، اختر اسمًا آخر."

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
# مسار إنشاء حساب جديد
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # التأكد من عدم وجود المستخدم مسبقاً
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "اسم المستخدم موجود مسبقاً، اختر اسمًا آخر."
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
        
    return render_template("register.html")

# مسار تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("profile"))
        else:
            return "خطأ في البيانات أو اسم المستخدم غير موجود"
            
    return render_template("login.html")



# مسار تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "POST":
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
      login_user(user)
      return redirect(url_for("profile"))
    else:
      return "خطأ في البيانات أو اسم المستخدم غير موجود"

  return render_template("login.html")


# مسار تسجيل الخروج
@app.route("/logout")
@login_required
def logout():
  logout_user()
  return redirect(url_for("login"))


# مسار إرسال الهدية
@app.route("/send_gift")
@login_required
def send_gift():
  if current_user.balance >= 50:
    current_user.balance -= 50
    db.session.commit()
    flash("تم إرسال الهدية بنجاح 🎁", "success")
  else:
    flash("رصيدك غير كافٍ! قم بشحن الرصيد أولاً.", "danger")

  return redirect(url_for("profile"))


if __name__ == "__main__":
  app.run(debug=True)
