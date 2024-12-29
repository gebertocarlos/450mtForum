from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı',
                         validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Şifreyi Onayla',
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Kayıt Ol')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu kullanıcı adı zaten alınmış. Lütfen başka bir tane seçin.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu email adresi zaten kullanımda. Lütfen başka bir tane seçin.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class EntryForm(FlaskForm):
    title = StringField('Başlık', validators=[DataRequired(), Length(min=3, max=100)])
    content = TextAreaField('İçerik', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Gönder')

class ReplyForm(FlaskForm):
    content = TextAreaField('Cevabınız', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Cevapla')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    submit = SubmitField('Şifre Sıfırlama İsteği Gönder')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Bu email adresiyle kayıtlı bir hesap bulunamadı.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Yeni Şifre', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Yeni Şifreyi Onayla',
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Şifreyi Sıfırla') 