from flask import url_for
from flask_mail import Message
from app import mail

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Şifre Sıfırlama İsteği',
                  recipients=[user.email])
    msg.body = f'''Şifrenizi sıfırlamak için aşağıdaki linke tıklayın:
{url_for('auth.reset_token', token=token, _external=True)}

Bu isteği siz yapmadıysanız, bu e-postayı görmezden gelin.
'''
    mail.send(msg) 