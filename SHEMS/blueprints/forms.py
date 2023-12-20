import wtforms
from wtforms import StringField,validators
from wtforms.validators import length,DataRequired

class LoginForm(wtforms.Form):
    name=StringField(validators=[DataRequired()])
    password=StringField(validators=[DataRequired(),length(min=4,max=15)])

class RegisterForm(wtforms.Form):
    name=StringField(validators=[DataRequired()])
    password=StringField(validators=[DataRequired(),length(min=4,max=15)])
    billingaddress=StringField(validators=[DataRequired()])