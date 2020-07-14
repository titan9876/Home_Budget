from flask import session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DecimalField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,NumberRange,InputRequired
from titan2.models import User, Account, Deposit, Expense
from titan2 import bcrypt

class FlexibleDecimalField(DecimalField):
    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", "")
        return super(FlexibleDecimalField, self).process_formdata(valuelist)

class SubmitExpenseForm(FlaskForm):
    date = DateField('Date:',validators=[DataRequired()])
    amount = FlexibleDecimalField('Amount:',places=2,rounding=None,validators=[DataRequired()])
    payee = StringField('Payee:',validators=[DataRequired(),Length(max=35,)])
    category = StringField('Category:',validators=[DataRequired()])
    comment = StringField('Comment:',validators=None)
    submit_expense = SubmitField('Submit')


class SubmitDepositForm(FlaskForm):
    dep_date = DateField('Date:',validators=[DataRequired()])
    dep_amount = FlexibleDecimalField('Amount:',places=2,rounding=None,validators=[DataRequired()])
    dep_source = StringField('Source:',validators=[DataRequired()])
    submit_deposit = SubmitField('Submit')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired()])
    submit = SubmitField('Reset Password')

class RegistrationForm(FlaskForm):
    username = StringField("User Name",validators=[DataRequired(),Length(min=5,max=12,message="Username Must Be 5-12 Characters.")])
    email = StringField('Email',validators=[DataRequired(), Email(message="This is not a Valid E-Mail Address")])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=4,message="Password Must Be 4 or More Characters.")])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password',message='Passwords Do Not Match.')])
    submit = SubmitField('Register Account')

    #Validation for Duplication of User Id's. Gets used by authentication in route form to direct user.
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('User id is already in use.')
    #Validation for Duplication of email. Gets used by authentication in route form to direct user.
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('E-Mail address already has associated account.')

class LoginForm(FlaskForm):
    username = StringField('User Name',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    #Validate Username
    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError('Username is Not Valid')
    #Validate Password fields
    def validate_password(self,password):
        user = User.query.filter_by(username=self.username.data).first()
        if user and not bcrypt.check_password_hash(user.password,password.data):
            raise ValidationError('Incorrect Password Entered. Please Try Again.')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[Length(min=6, max=15)])
    email = StringField('Email',validators=[Email()])
    picture = FileField('Update Image', validators=[FileAllowed(['jpg', 'png', 'jpeg','tiff'],message="Acceptable: jpg,jpeg,png,tiff")])
    password = PasswordField('Must Be Atleast 8 Characters:')
    confirm_password = PasswordField('Must Match Entered Password:')
    submit = SubmitField('Submit Changes')

    #Validation for Duplication of User Id's. Gets used by authentication in route form to direct user
    def validate_username(self, username):
        if username.data and (username.data != current_user.username):
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('User id is already in use.')

    #Validation for Duplication of email. Gets used by authentication in route form to direct user.
    def validate_email(self, email):
        if email.data and (email.data != current_user.email):
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('E-Mail address already has associated account.')

    def validate_password(self,password):
        if password.data:
            if len(password.data) < 8:
                raise ValidationError('Password is Too Short')

    def validate_confirm_password(self,*args):
        if self.confirm_password.data or self.password.data:
            if (self.confirm_password.data != self.password.data):
                raise ValidationError('Passwords Do Not Match')




class AddAccountForm(FlaskForm):
    account_name = StringField('Account Name:', validators=[DataRequired(),Length(min=1,max=20)])
    safe_bal = IntegerField('Safe Balance:',default=0)
    crit_bal = IntegerField('Critical Balance:',default=0)
    submit_add_account = SubmitField('Add Account')
    current_account = IntegerField()

    #Set Default Account for the first Account Added by a Username
    # ******** Moved to Routes page ***********
    # def validate_username(self,*args):
    #     if not current_user.accounts:
    #         accounts = Account.query.filter(Account.id).all()
    #         last_id = accounts[-1]
    #         last_id = last.id
    #         raise ValidationError(last)
    #         self.current_account.data = last + 1
    #         return self.current_account.data



   # Useful Code Snippet for Custom Validations:
   # class TestForm(FlaskForm):
   #      startdate = DateField('Start Date',default=date.today)
   #      enddate = DateField('End Date',default=date.today)
   #
   #      def validate_on_submit(self):
   #          result = super(TestForm, self).validate()
   #          if (self.startdate.data>self.enddate.data):
   #              return False
   #          else:
   #              return result

# class TransferForm(FlaskForm):
#     if Account.query.filter(Account.owner_id == User.id).first():
#         choices=[(str(acct.id),acct.name) for acct in Account.query.filter(Account.owner_id == User.id).all()]
#     else:
#         choices=[("0",'No Choices'),("1","Choice 1"),("2","Choice 2")]
#     print(choices)
#     trans_date = DateField('Date:',validators=[DataRequired()])
#     trans_amount = FlexibleDecimalField('Amount:',places=2,rounding=None,validators=[DataRequired()])
#     transfer_from_acct = SelectField('From Account:',validators=[DataRequired(message="Must select a Source Account")],choices=choices)
#     transfer_to_acct = SelectField('To Account:',validators=[DataRequired(message="Must select a valid choice")],choices=choices)
#     submit_transfer = SubmitField('Submit')
#
#     def validate_transfer_from_acct(self,*args):
#         if not self.transfer_from_acct or not self.transfer_to_acct:
#             raise ValidationError('You Must Select Accounts to Transfer To and From')
#         elif self.transfer_from_acct == self.transfer_to_acct:
#             raise ValidationError('You Cannot Transfer to the Same Account')
