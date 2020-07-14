import secrets
import os
from PIL import Image
from flask import url_for, redirect, flash, render_template, request, abort, Markup
from titan2.forms import RegistrationForm, LoginForm, UpdateAccountForm, AddAccountForm, ForgotPasswordForm, SubmitExpenseForm, SubmitDepositForm, TransferForm
from titan2.models import User, Account, Deposit, Expense
from titan2 import app, db, bcrypt
from flask_login import login_user, current_user, login_required, logout_user
from datetime import datetime

authenticated=False

def set_standard_values():
    if current_user.accounts:
        accounts = Account.query.filter(Account.owner_id==current_user.id).all()
        current_account = current_user.current_account
        current_account_name = Account.query.filter(Account.id==current_user.current_account).first().name
        deposits = Deposit.query.filter(Deposit.acct_id==current_account).order_by(Deposit.date).order_by(Deposit.id).all()[::-1]
        expenses = Expense.query.filter(Expense.acct_id==current_account).order_by(Expense.date).order_by(Expense.id).all()[::-1]
        total_of_deposits = 0
        total_of_expenses = 0
        for x in range(0,len(deposits)):
            total_of_deposits = total_of_deposits + deposits[x].amount
        for x in range(0,len(expenses)):
            total_of_expenses = total_of_expenses + expenses[x].amount
        ####Convert Integer to Float####
        balance = (total_of_deposits - total_of_expenses) / 100
        #If Balance is Negative, remove the "-" sign with "()" wrappers
        if balance < 0:
            balance = float(str(balance).replace('-',''))
            balance = str('{:,.2f}'.format(balance))
            balance = "(" + balance + ")"
        else:
            balance = str('{:,.2f}'.format(balance))
        #################################
    else: #Else User is Not Logged in#
        accounts=[]
        current_account=""
        current_account_name = ""
        balance = ""
        expenses = ""
        deposits = ""
    #Return Values for all Users
    len_act = len(accounts)
    return current_account,current_account_name,accounts,len_act,balance,deposits,expenses


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/home',methods=['GET','POST'])
def home():
    #Set Form Values
    expense_form = SubmitExpenseForm()
    deposit_form = SubmitDepositForm()
    add_account_form= AddAccountForm()
    #Get Default Values for All Forms
    if True:
        current_account,current_account_name,accounts,len_act,balance,deposits,expenses = set_standard_values()
    ### Form Submit for Adding New Account Modal ###
    if add_account_form.validate_on_submit():
        account = Account(name = add_account_form.account_name.data, safe_bal = add_account_form.safe_bal.data,
                          crit_bal = add_account_form.crit_bal.data,owner_id=current_user.id)
        db.session.add(account)
        db.session.commit()
        # If This is the First Account, Set it as Default in View
        if len(current_user.accounts) == 1:
            all_accounts = Account.query.filter(Account.id).all()
            last_account = all_accounts[-1]
            last_account = last_account.id
            current_user.current_account = last_account
            db.session.commit()
        #flash('Account Has Been Added', 'success')
        return redirect(url_for('home'))
    ##################################################
    ### Form Submit for Adding an Expense ###
    if expense_form.validate_on_submit():
        #Convert Decimals to Full Integers to be divided later
        temp_amount=str(round(float(expense_form.amount.data),2))
        if len(temp_amount.split('.')[1]) == 1:
            temp_amount = temp_amount + "0"
        expense_form.amount.data = int(temp_amount.replace('.',''))
        #End of Convert
        expense = Expense(date = expense_form.date.data,amount = expense_form.amount.data, payee = expense_form.payee.data,
                           category = expense_form.category.data, comment = expense_form.comment.data, acct_id=current_user.current_account)
        db.session.add(expense)
        db.session.commit()
        #flash('Payment Entered Successfully', 'success')
        return redirect(url_for('home'))
    ###########################################
    ### Form Submit for Adding a Deposit ###
    if deposit_form.validate_on_submit():
        temp_amount=str(round(float(deposit_form.dep_amount.data),2))
        if len(temp_amount.split('.')[1]) == 1:
            temp_amount = temp_amount + "0"
        deposit_form.dep_amount.data = int(temp_amount.replace('.',''))
        deposit= Deposit(date=deposit_form.dep_date.data,amount=deposit_form.dep_amount.data,source=deposit_form.dep_source.data,acct_id=current_user.current_account)
        db.session.add(deposit)
        db.session.commit()
        #flash('Deposit Has Been Added.', 'success')
        return redirect(url_for('home'))
    ############################################
    # Re-Format dates so they are 'Murican' ###
    for x in range(0,len(deposits)):
        temp_date=str(deposits[x].date)
        Y,m,d = (x for x in temp_date.split('-'))
        new_date = (m + '/' + d +'/' + Y)
        deposits[x].date = new_date
    for x in range(0,len(expenses)):
        temp_date=str(expenses[x].date)
        Y,m,d = (x for x in temp_date.split('-'))
        new_date = (m + '/' + d +'/' + Y)
        expenses[x].date = new_date
    #############################################
    ### Create The Required Chart Values ###
    colors=["#cf1919","#16b53b","#1a3cc7","#fa9f20","#891af0","#ffef3b",
                    "#285926","#7d3232","#434175","#d66dca","#f7f283","#64367a",
                    "#000000","#818485","#ffffff","#3ab6c2"]
    # Create a Unique List of Expense Categories to Be used in Charts (by using set() function)
    expense_categories=[]
    for x in range (0,len(expenses)):
            expense_categories.append(expenses[x].category)
    expense_categories= list(set(expense_categories))
    #Create a List Using the Expense Categories for the Amounts in the Chart
    expense_amounts=[]
    expense_colors=[]
    for z in range(0,len(expense_categories)):
        expense_colors.append(colors[z])
    for category_name in expense_categories:
        category_amount = 0
        for y in range(0, len(expenses)):
            if expenses[y].category == category_name:
                category_amount = category_amount + (expenses[y].amount / 100)
        expense_amounts.append(category_amount)
    ##############################################
    return render_template('home.html',accounts=accounts,balance=balance,
                            len_act=len_act,current_account=current_account,current_account_name=current_account_name,add_account_form=add_account_form,
                            expense_form=expense_form, deposit_form=deposit_form,expenses=expenses,deposits=deposits,
                            set=zip(expense_amounts,expense_categories,expense_colors))


@app.route('/login',methods=['GET','POST'])
def login():
    #If user is already Logged In they don't need to see this
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    #Otherwise, Take them to the login page
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            #Redirect to Requested page if not logged in first
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Failed. Please check Username and Password','danger')
    return render_template('login.html',title='Login',form=form)


@app.route('/register',methods=['GET','POST'])
def register():

    #If user is Logged in, they don't need to register either
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    users = User.query.all()
    #If they aren't Lgged in, they can Register a new account
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        #flash('Your Account has been created. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.route('/forgot-password',methods=['GET','POST'])
def forgot():
    add_account_form = AddAccountForm()
    #If user is logged in, they certainly didn't forget their goddam password
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ForgotPasswordForm()
    return render_template('forgot-password.html',form=form)

@app.route('/charts')

def charts():
    current_account=""
    add_account_form = AddAccountForm()
    if True:
        current_account,current_account_name,accounts,len_act,balance,deposits,expenses = set_standard_values()
    return render_template('charts.html',accounts=accounts,balance=balance,len_act=len_act,
                            current_account=current_account,current_account_name=current_account_name,
                            deposits=deposits,expenses=expenses)

@app.route('/reports')
def reports():
    length=10
    add_account_form = AddAccountForm()
    expense_form = SubmitExpenseForm()
    deposit_form = SubmitDepositForm()
    current_account=""
    if True:
        current_account,current_account_name,accounts,len_act,balance,deposits,expenses = set_standard_values()
    return render_template('reports.html',length=length,accounts=accounts,balance=balance,
                            len_act=len_act,current_account=current_account,current_account_name=current_account_name,
                            deposits=deposits,expenses=expenses,expense_form=expense_form,deposit_form=deposit_form)
@app.route('/alerts')
def alerts():
    current_account=""
    expense_form = SubmitExpenseForm()
    deposit_form = SubmitDepositForm()
    if True:
        current_account,current_account_name,accounts,len_act,balance,deposits,expenses = set_standard_values()
    return render_template('alerts.html',accounts=accounts,balance=balance,
                            len_act=len_act,current_account=current_account,current_account_name=current_account_name,
                            deposits=deposits,expenses=expenses,expense_form=expense_form,deposit_form=deposit_form)



@app.route('/my_account',methods=['GET','POST'])
@login_required
def my_account():
    users = User.query.all()
    my_form = UpdateAccountForm()
    if my_form.validate_on_submit():
        if my_form.picture.data:
            picture_file = save_picture(my_form.picture.data)
            current_user.image_file = picture_file
        current_user.username = my_form.username.data
        current_user.email = my_form.email.data
        if my_form.password.data:
            current_user.password = bcrypt.generate_password_hash(my_form.password.data).decode('utf-8')
        db.session.commit()
        flash('Account Update Successful!', 'success')
        return redirect(url_for('my_account'))
    elif request.method == 'GET':
        my_form.username.data = current_user.username
        my_form.email.data = current_user.email
    if True:
        current_account,current_account_name,accounts,len_act,balance,deposits,expenses = set_standard_values()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    email_len = len(current_user.email)
    return render_template('my_account.html',title="My Account",my_form=my_form,email_len=email_len,image_file=image_file,users=users,accounts=accounts,balance=balance,
                            len_act=len_act,current_account=current_account,current_account_name=current_account_name,deposits=deposits,expenses=expenses)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/set_active_account/<int:set_account>/set',methods=['GET','POST'])
@login_required
def set_active_account(set_account):
    if set_account != current_user.current_account:
        current_user.current_account = set_account
        db.session.commit()
    #Return to the same page upon submission
    return redirect(request.referrer)

@app.route('/set_view/<int:view>/set',methods=['GET','POST'])
@login_required
def set_view(view):
    if view != current_user.view:
        current_user.view = view
        db.session.commit()
    #Return to the same pages
    return redirect(request.referrer)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    #Get file extension from supplied file
    _, f_ext = os.path.splitext(form_picture.filename)
    #Generates a unique filename in case two users try to use the same name
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    #Use Pillow Functions to resize Images
    output_size=(150, 150)
    new_img = Image.open(form_picture)
    new_img.thumbnail(output_size)
    new_img.save(picture_path)

    return picture_fn
