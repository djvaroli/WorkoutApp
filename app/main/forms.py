from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, Optional
from flask_login import current_user
from flask_babel import _, lazy_gettext as _l
from app.models import User, Exercise
import string


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    units = SelectField(_l('Select Units'), choices=[('metric', 'kg/m'), ('imperial', 'lbs/ft')], default='metric')
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))




def input_is_int(form,field):
    try:
        value = int(field.data)
    except:
        raise ValidationError(_('Entry must be a number, e.g. 10'))

def input_is_int_or_float(form,field):
    try:
        input_is_int(field,field)
    except:
        try:
            value = float(field.data)
        except:
            raise ValidationError(_('Entry must be a number, e.g. 10 or 10.5'))

def no_special_chars(form,field):
    accepted = list(string.ascii_lowercase) + ['{}'.format(i) for i in range(10)] + [' ','_','-']
    entry = list(field.data.lower())
    for l in entry:
        if l not in accepted:
            raise ValidationError(_('Name should not contain special characters!'))

def name_not_duplicate(form,field):
    name = field.data
    exercise = Exercise.query.filter_by(name = name, user_id = current_user.id).first()
    print(exercise)
    if exercise is not None:
        raise ValidationError(_('Name already exists!'))

class ExerciseForm(FlaskForm):
    name = StringField(_l('Enter Exercise Name'), validators=[DataRequired(),no_special_chars, name_not_duplicate])
    type = SelectField(_l('Select Exercise Type'), choices= [('repetition','Repetition Exercise'),
                                             ('duration','Duration Exercise'),
                                             ('mental','Mental Exercise'),
                                             ], default='Repetition Exercise')
    submit = SubmitField(_l('Add Exercise'))

class ProgressionForm(FlaskForm):
    reps = StringField(_l('Reps'), validators=[DataRequired(),input_is_int])
    sets = StringField(_l('Sets'), validators=[DataRequired(),input_is_int])
    weight = StringField(_l('Weight'), validators=[DataRequired(), input_is_int_or_float], default=0.0)
    duration = StringField(_l('Duration'),validators=[DataRequired(), input_is_int_or_float],default=0.0)
    submit = SubmitField(_l('Add Progression'))

class ProgressionFormMental(FlaskForm):
    description = TextAreaField(_l('Exercise Description'), validators=[DataRequired()])
    submit = SubmitField(_l('Add Progression'))

