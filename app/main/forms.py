from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models import Title

class EntryForm(FlaskForm):
    title = StringField('başlık', validators=[DataRequired(), Length(min=2, max=200)])
    content = TextAreaField('içerik', validators=[DataRequired()])
    submit = SubmitField('gönder')

    def validate_title(self, title):
        # Başlık varsa hata verme, yeni entry olarak eklenecek
        pass

class ReplyForm(FlaskForm):
    content = TextAreaField('cevap', validators=[DataRequired()])
    submit = SubmitField('gönder') 