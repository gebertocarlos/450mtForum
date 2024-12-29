from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt, mail
from app.models import User
from app.auth.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from flask_mail import Message
import traceback

auth = Blueprint('auth', __name__)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Şifre Sıfırlama İsteği',
                  recipients=[user.email])
    msg.body = f'''Şifrenizi sıfırlamak için aşağıdaki linke tıklayın:
{url_for('auth.reset_token', token=token, _external=True)}

Bu isteği siz yapmadıysanız, bu e-postayı görmezden gelin.
'''
    mail.send(msg)

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

@auth.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            send_reset_email(user)
            flash('Şifre sıfırlama talimatları e-posta adresinize gönderildi.', 'info')
            return redirect(url_for('auth.login'))
        except Exception as e:
            current_app.logger.error(f'E-posta gönderme hatası: {str(e)}')
            current_app.logger.error(traceback.format_exc())
            flash('E-posta gönderilirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.', 'danger')
    return render_template('auth/reset_request.html', title='Şifre Sıfırlama', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Geçersiz veya süresi dolmuş token.', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Şifreniz başarıyla güncellendi! Şimdi giriş yapabilirsiniz.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html', title='Şifre Sıfırla', form=form) 