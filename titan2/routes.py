import secrets
import os
from PIL import Image
from flask import url_for, redirect, flash, render_template, request, abort, Markup, session
from titan2.forms import RegistrationForm, LoginForm, UpdateAccountForm, AddAccountForm, ForgotPasswordForm, SubmitExpenseForm, SubmitDepositForm
from titan2.models import User, Account, Deposit, Expense
from titan2 import app, db, bcrypt
from flask_login import login_user, current_user, login_required, logout_user
from datetime import datetime, date
from random import randint
import random

def set_standard_values():
    if current_user.accounts:
        accounts = Account.query.filter(Account.owner_id==current_user.id).all()
        current_account = current_user.current_account
        current_account_name = Account.query.filter(Account.id==current_user.current_account).first().name
        all_accounts = []
        all_balances = []
        for z in range(0,len(accounts)):
            balance=0
            deposits = Deposit.query.filter(Deposit.acct_id==accounts[z].id).order_by(Deposit.date).order_by(Deposit.id).all()[::-1]
            expenses = Expense.query.filter(Expense.acct_id==accounts[z].id).order_by(Expense.date).order_by(Expense.id).all()[::-1]
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
            all_accounts.append(accounts[z].name)
            all_balances.append(balance)
            if accounts[z].id == current_user.current_account:
                current_balance=balance
                current_deposits=deposits
                current_expenses=expenses
        #################################
    else: #Else User is Not Logged in or Has No Accounts Yet#
        accounts=[]
        current_account=""
        current_account_name=""
        balance=""
        expenses=""
        deposits=""
        current_expenses=""
        current_deposits=""
        current_balance=""
        all_accounts=""
        all_balances=""
    #Return Values for all Users
    len_act = len(accounts)
    return current_account,current_account_name,accounts,len_act,current_balance,current_deposits,current_expenses,deposits,expenses,all_accounts,all_balances


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/home',methods=['GET','POST'])
@login_required
def home():
    #Get Default Values for All Forms
    if True:
        current_account,current_account_name,accounts,len_act,current_balance,current_deposits,current_expenses,deposits,expenses,all_accounts,all_balances = set_standard_values()
    #Set Form Values
    expense_form = SubmitExpenseForm()
    deposit_form = SubmitDepositForm()
    add_account_form = AddAccountForm()
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
    for x in range(0,len(current_deposits)):
        temp_date=str(current_deposits[x].date)
        Y,m,d = (x for x in temp_date.split('-'))
        new_date = (m + '/' + d +'/' + Y)
        current_deposits[x].date = new_date
    for x in range(0,len(current_expenses)):
        temp_date=str(current_expenses[x].date)
        Y,m,d = (x for x in temp_date.split('-'))
        new_date = (m + '/' + d +'/' + Y)
        current_expenses[x].date = new_date
    ############################################

    ########################################
    ### Create The Required Chart Values ###
    # Create a Unique List of Expense Categories to Be used in Charts (by using set() function)
    expense_categories=[]
    for x in range (0,len(current_expenses)):
            expense_categories.append(current_expenses[x].category)
    expense_categories= list(set(expense_categories))
    #Create a List Using the Expense Categories for the Amounts in the Chart
    # Set Some Default Colors to Be used in Charts #
    colors=["#cf1919","#16b53b","#1a3cc7","#fa9f20","#891af0","#ffef3b",
                    "#285926","#7d3232","#434175","#d66dca","#f7f283","#64367a",
                    "#000000","#818485","#ffffff","#3ab6c2"]
    #   If More Colors Are Required, we will create them   #
    if len(colors) < len(expense_categories):
        diff_len = len(expense_categories) - len(colors)
        for missing_color in range(0,diff_len):
            new_color=""
            for pos in range(0,6):
                # Flip a Coin To See if you get Numbers or Letters #
                coin_toss=randint(0,1)
                #If 0, You have an Integer
                if coin_toss == 0:
                    new_char=randint(0,9)
                else:
                    #Otherwise You get a letter
                    alphas="ABCDEF"
                    new_char=random.choice(alphas)
                new_color=(new_color + str(new_char))
            new_color=("#" + new_color)
            colors.append(new_color)
    ######  OK - We Are Done Playing with Colors Now  ######
    expense_amounts=[]
    expense_colors=[]
    for z in range(0,len(expense_categories)):
        expense_colors.append(colors[z])
    for category_name in expense_categories:
        category_amount = 0
        for y in range(0, len(current_expenses)):
            if current_expenses[y].category == category_name:
                category_amount = category_amount + (current_expenses[y].amount)
        expense_amounts.append(category_amount)
    ##############################################
    tot_bal=0
    for i in range(0,len_act):
        if "(" in all_balances[i]: #In Case A Balance is Negative
            #Remove Parathesis so total Balance can Be calculated
            all_balances[i] = all_balances[i].replace("(","").replace(")","")
            tot_bal = tot_bal - float(all_balances[i].replace(",",""))
            #Put Parenthesis back for Viewing
            all_balances[i] = "(" + all_balances[i] + ")"
        else:
            tot_bal = float(all_balances[i].replace(",","")) + tot_bal
    tot_bal=str('{:,.2f}'.format(tot_bal))
    return render_template('home.html',tot_bal=tot_bal,accounts=accounts,current_balance=current_balance,all_accounts=all_accounts,all_balances=all_balances,
                            len_act=len_act,current_account=current_account,current_account_name=current_account_name,add_account_form=add_account_form,
                            expense_form=expense_form, deposit_form=deposit_form,expenses=expenses,current_expenses=current_expenses,current_deposits=current_deposits,deposits=deposits,
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
        current_account,current_account_name,accounts,len_act,current_balance,current_deposits,current_expenses,deposits,expenses,all_accounts,all_balances = set_standard_values()
    ########################################
    ### Create The Required Chart Values ###
    # Create a Unique List of Expense Categories to Be used in Charts (by using set() function)
    expense_categories=[]
    for x in range (0,len(current_expenses)):
            expense_categories.append(current_expenses[x].category)
    expense_categories= list(set(expense_categories))
    #Create a List Using the Expense Categories for the Amounts in the Chart
    # Set Some Default Colors to Be used in Charts #
    colors=["#cf1919","#16b53b","#1a3cc7","#fa9f20","#891af0","#ffef3b",
                    "#285926","#7d3232","#434175","#d66dca","#f7f283","#64367a",
                    "#000000","#818485","#ffffff","#3ab6c2"]
    #   If More Colors Are Required, we will create them   #
    if len(colors) < len(expense_categories):
        diff_len = len(expense_categories) - len(colors)
        for missing_color in range(0,diff_len):
            new_color=""
            for pos in range(0,6):
                # Flip a Coin To See if you get Numbers or Letters #
                coin_toss=randint(0,1)
                #If 0, You have an Integer
                if coin_toss == 0:
                    new_char=randint(0,9)
                else:
                    #Otherwise You get a letter
                    alphas="ABCDEF"
                    new_char=random.choice(alphas)
                new_color=(new_color + str(new_char))
            new_color=("#" + new_color)
            colors.append(new_color)
    ######  OK - We Are (Almost) Done Playing with Colors Now  ######
    # Set Empty Lists for Categories #
    expense_amounts=[]
    expense_colors=[]
    mtd_expense_amounts=[]
    mtd_expense_categories=[]
    mtd_colors=[]
    ytd_expense_amounts=[]
    ytd_expense_categories=[]
    ytd_colors=[]

    this_year=date.today().strftime("%Y")
    this_month=date.today().strftime("%m")

    for category_name in expense_categories:
        category_amount = 0
        mtd_category_amount = 0
        ytd_category_amount = 0
        for y in range(0, len(current_expenses)):
            if current_expenses[y].category == category_name:
                category_amount = category_amount + (current_expenses[y].amount)
                exp_year = str(current_expenses[y].date)[0:4]
                exp_month = str(current_expenses[y].date)[5:7]
                if exp_year == this_year:
                    ytd_category_amount = ytd_category_amount + (current_expenses[y].amount)
                    if exp_month == this_month:
                        mtd_category_amount = mtd_category_amount + (current_expenses[y].amount)
        expense_amounts.append(category_amount)
        if mtd_category_amount > 0:
            mtd_expense_categories.append(category_name)
            mtd_expense_amounts.append(mtd_category_amount)
        if ytd_category_amount > 0:
            ytd_expense_categories.append(category_name)
            ytd_expense_amounts.append(ytd_category_amount)
    for z in range(0,len(expense_categories)):
        expense_colors.append(colors[z])
    for z in range(0,len(mtd_expense_categories)):
        mtd_colors.append(colors[z])
    for z in range(0,len(ytd_expense_categories)):
        ytd_colors.append(colors[z])
    ##############################################
    return render_template('charts.html',accounts=accounts,current_balance=current_balance,len_act=len_act,
                            current_account=current_account,all_accounts=all_accounts,all_balances=all_balances,current_deposits=current_deposits,current_expenses=current_expenses,
                            current_account_name=current_account_name,set=zip(expense_amounts,expense_categories,expense_colors),
                            mtd=zip(mtd_expense_amounts,mtd_expense_categories,mtd_colors),ytd=zip(ytd_expense_amounts,ytd_expense_categories,ytd_colors))


@app.route('/reports')
def reports():
    length=10
    expense_form = SubmitExpenseForm()
    deposit_form = SubmitDepositForm()
    add_account_form = AddAccountForm()
    current_account=""
    if True:
        current_account,current_account_name,accounts,len_act,current_balance,current_deposits,current_expenses,deposits,expenses,all_accounts,all_balances = set_standard_values()
    return render_template('reports.html',length=length,accounts=accounts,current_balance=current_balance,
                            len_act=len_act,current_account=current_account,current_expenses=current_expenses,current_deposits=current_deposits,current_account_name=current_account_name,
                            deposits=deposits,expenses=expenses,all_accounts=all_accounts,all_balances=all_balances)
@app.route('/alerts')
def alerts():
    current_account=""
    expense_form = SubmitExpenseForm()
    deposit_form = SubmitDepositForm()
    add_account_form = AddAccountForm()
    if True:
        current_account,current_account_name,accounts,len_act,current_balance,current_deposits,current_expenses,deposits,expenses,all_accounts,all_balances = set_standard_values()
    return render_template('alerts.html',accounts=accounts,current_balance=current_balance,all_accounts=all_accounts,all_balances=all_balances,
                            len_act=len_act,current_account=current_account,current_account_name=current_account_name,
                            deposits=deposits,expenses=expenses,expense_form=expense_form,deposit_form=deposit_form)

@app.route('/edit_deposit/<int:dep_id>',methods=['GET','POST'])
def edit_deposit(dep_id):
    current_account=""
    deposit_form = SubmitDepositForm()
    this_dep=Deposit.query.get_or_404(dep_id)
    if True:
        current_account,current_account_name,accounts,len_act,current_balance,current_deposits,current_expenses,deposits,expenses,all_accounts,all_balances = set_standard_values()
    ###########################################
    ### Form Submit for Adding a Deposit ###
    if deposit_form.validate_on_submit():
        temp_amount=str(round(float(deposit_form.dep_amount.data),2))
        if len(temp_amount.split('.')[1]) == 1:
            temp_amount = temp_amount + "0"
        deposit_form.dep_amount.data = int(temp_amount.replace('.',''))
        this_dep.date=deposit_form.dep_date.data
        this_dep.amount=deposit_form.dep_amount.data
        this_dep.source=deposit_form.dep_source.data
        db.session.commit()
        #flash('Deposit Has Been Added.', 'success')
        return redirect(url_for('reports'))
    return render_template('edit_deposit.html',this_dep=this_dep,accounts=accounts,current_balance=current_balance,all_accounts=all_accounts,all_balances=all_balances,
                            len_act=len_act,current_account=current_account,current_account_name=current_account_name,
                            deposit_form=deposit_form)

@app.route('/edit_expense/<int:exp_id>',methods=['GET','POST'])
def edit_expense(exp_id):
    current_account=""
    expense_form = SubmitExpenseForm()
    this_exp=Expense.query.get_or_404(exp_id)
    if True:
        current_account,current_account_name,accounts,len_act,current_balance,current_deposits,current_expenses,deposits,expenses,all_accounts,all_balances = set_standard_values()
    ##################################################
    ### Form Submit for Adding an Expense ###
    if expense_form.validate_on_submit():
        #Convert Decimals to Full Integers to be divided later
        temp_amount=str(round(float(expense_form.amount.data),2))
        if len(temp_amount.split('.')[1]) == 1:
            temp_amount = temp_amount + "0"
        expense_form.amount.data = int(temp_amount.replace('.',''))
        #End of Convert
        this_exp.date = expense_form.date.data
        this_exp.amount = expense_form.amount.data
        this_exp.payee = expense_form.payee.data
        this_exp.category = expense_form.category.data
        this_exp.comment = expense_form.comment.data
        db.session.commit()
        #flash('Payment Entered Successfully', 'success')
        return redirect(url_for('reports'))

    return render_template('edit_expense.html',this_exp=this_exp,accounts=accounts,current_balance=current_balance,all_accounts=all_accounts,all_balances=all_balances,
                            len_act=len_act,current_account=current_account,current_account_name=current_account_name,
                            expense_form=expense_form)

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
        current_account,current_account_name,accounts,len_act,current_balance,current_deposits,current_expenses,deposits,expenses,all_accounts,all_balances = set_standard_values()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    email_len = len(current_user.email)
    return render_template('my_account.html',title="My Account",my_form=my_form,email_len=email_len,image_file=image_file,users=users,accounts=accounts,current_balance=current_balance,
                            len_act=len_act,current_account=current_account,current_account_name=current_account_name,deposits=deposits,expenses=expenses,
                            all_accounts=all_accounts,all_balances=all_balances)

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

@app.route("/transaction/<trans_type>/<int:trans_id>/delete", methods=['GET','POST'])
@login_required
def delete_transaction(trans_type,trans_id):
    trans=""
    if trans_type=="dep":
        transaction = Deposit.query.get_or_404(trans_id)
        db.session.delete(transaction)
        db.session.commit()
        flash('Transaction has been deleted!', 'success')
    else:
        #trans_type=="exp":
        transaction = Expense.query.get_or_404(trans_id)
        db.session.delete(transaction)
        db.session.commit()
    return redirect(request.referrer)
