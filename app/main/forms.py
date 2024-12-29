from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class EntryForm(FlaskForm):
    title = StringField('Başlık', validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('İçerik', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Gönder')

class ReplyForm(FlaskForm):
    content = TextAreaField('Cevap', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Gönder') 