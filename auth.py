from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from extensions import db, bcrypt
from models import User
from forms import RegistrationForm, LoginForm
import traceback

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Kayıt olma hatası: {str(e)}')
            current_app.logger.error(traceback.format_exc())
            flash('Kayıt olma sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin.', 'danger')
    return render_template('auth/register.html', title='Kayıt Ol', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Giriş başarısız. Lütfen email ve şifrenizi kontrol edin.', 'danger')
    return render_template('auth/login.html', title='Giriş', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home')) 