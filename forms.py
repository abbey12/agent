from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[Optional(), Length(max=100)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=100)])
    facility_name = StringField('Facility Name', validators=[Optional(), Length(max=200)])
    clinical_position = StringField('Clinical Position', validators=[Optional(), Length(max=100)])
    years_of_experience = IntegerField('Years of Experience', validators=[Optional()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[Optional()])
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Save Changes')
