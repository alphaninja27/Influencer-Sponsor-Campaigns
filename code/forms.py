from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, BooleanField, TextAreaField, DecimalField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, NumberRange

class SponsorRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    company_name = StringField('Company Name', validators=[DataRequired()])
    industry = StringField('Industry', validators=[DataRequired()])
    budget = FloatField('Budget', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Sign Up')

class InfluencerRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    niche = StringField('Niche', validators=[DataRequired()])
    reach = FloatField('Reach', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CampaignForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=1000)])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    budget = DecimalField('Budget', validators=[DataRequired(), NumberRange(min=0)])
    visibility = SelectField('Visibility', choices=[('public', 'Public'), ('private', 'Private')], validators=[DataRequired()])

class AdRequestForm(FlaskForm):
    influencer_id = IntegerField('Influencer ID', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    payment_amount = DecimalField('Payment Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')

class EditAdRequestForm(FlaskForm):
    influencer_id = IntegerField('Influencer ID', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    payment_amount = DecimalField('Payment Amount', validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField('Status', choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('negotiating', 'Negotiating')], validators=[DataRequired()])
    submit = SubmitField('Update Ad Request')

class DeleteAdRequestForm(FlaskForm):
    submit = SubmitField('Delete')

class NegotiationForm(FlaskForm):
    payment_amount = FloatField('Proposed Payment Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Negotiate')

class AdRequestActionForm(FlaskForm):
    accept = SubmitField('Accept')
    reject = SubmitField('Reject')
