#Contains Models for DB to prevent clutter of Main program.
from datetime import datetime
from titan2 import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	__tablename__='users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False,unique=True)
	email = db.Column(db.String(80), nullable=False, unique=True)
	image_file = db.Column(db.String(40), nullable=True, default='boring.jpg')
	password = db.Column(db.String(60), nullable=False)
	view = db.Column(db.Integer,default=1)
	current_account = db.Column(db.Integer,default=1)
	accounts = db.relationship('Account',backref='owner',lazy=True)

	# def __init__(self,username,email,password):
	# 	self.username = username
	# 	self.email = email
	# 	self.password = password


	def __repr__(self):
		return f"User: {self.username},{self.email},{self.image_file},{self.view},{self.accounts}"

class Account(db.Model):
	__tablename__='accounts'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(30), nullable=False)
	current_account = db.Column(db.Integer,nullable=False,default=0)
	safe_bal = db.Column(db.Integer,nullable=True)
	crit_bal = db.Column(db.Integer,nullable=True)
	owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	deposits = db.relationship('Deposit',backref="account",lazy=True)
	expenses = db.relationship('Expense',backref="account",lazy=True)

	# def __init__(self,name,safe_bal,crit_bal,user_id):
	# 	self.name = name
	# 	self.safe_bal = safe_bal
	# 	self.crit_bal = crit_bal
	# 	self.user_id = user_id

	def __repr__(self):
		return f"Account: {self.name},{self.current_account},{self.safe_bal},{self.crit_bal},{self.owner_id}"

class Deposit(db.Model):
	__tablename__='deposits'
	id = db.Column(db.Integer,primary_key=True)
	date = db.Column(db.Date,nullable=False)
	amount = db.Column(db.Integer,nullable=False)
	source = db.Column(db.String(40),nullable=False)
	acct_id = db.Column(db.Integer,db.ForeignKey('accounts.id'),nullable=False)

	# def __init__(self,date,amount,source):
	# 	self.date = date
	# 	self.amount = amount
	# 	self.source = source

	def __repr__(self):
		return f"Deposit: {self.date},{self.amount},{self.source}"

class Expense(db.Model):
	__tablename__='expenses'
	id = db.Column(db.Integer,primary_key=True)
	date = db.Column(db.Date,nullable=False)
	amount = db.Column(db.Integer,nullable=False)
	payee = db.Column(db.String,nullable=False)
	category = db.Column(db.String,nullable=False)
	comment = db.Column(db.Text(40),nullable=True)
	acct_id = db.Column(db.Integer,db.ForeignKey('accounts.id'),nullable=False)

	# def __init__(self,date,amount,payee,category):
	# 	self.date = date
	# 	self.amount = amount
	# 	self.payee = payee
	# 	self.category = category

	def __repr__(self):
		return f"Expense: {self.date},{self.amount},{self.payee},{self.category},{self.comment}"
