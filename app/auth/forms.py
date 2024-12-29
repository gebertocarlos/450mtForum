from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Kullanıcı Adı',
                         validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('E-posta',
                       validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
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
            raise ValidationError('Bu e-posta adresi zaten kayıtlı. Lütfen başka bir tane kullanın.')

class LoginForm(FlaskForm):
    email = StringField('E-posta',
                       validators=[DataRequired(), Email()])
    password = PasswordField('Şifre', validators=[DataRequired()])
    remember = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')

class RequestResetForm(FlaskForm):
    email = StringField('E-posta',
                       validators=[DataRequired(), Email()])
    submit = SubmitField('Şifre Sıfırlama İste')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Bu e-posta adresiyle kayıtlı bir hesap bulunamadı.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Şifre', validators=[DataRequired()])
    confirm_password = PasswordField('Şifreyi Onayla',
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Şifreyi Sıfırla') 