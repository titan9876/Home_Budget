from titan2.models import User, Expense, Deposit, Expense
from titan2 import app, db, bcrypt
import datetime

deposits = Deposit.query.filter(Deposit.acct_id != "").all()
expenses = Expense.query.filter(Expense.acct_id != "").all()

# Create a Unique List of Expense Categories to Be used in Charts (by using set() function)
expense_categories=[]
for x in range (0,len(expenses)):
        expense_categories.append(expenses[x].category)
expense_categories= list(set(expense_categories))

#Create a List Using the Expense Categories for the Amounts in the Chart
expense_amounts=[]
for category_name in expense_categories:
    print(category_name)
    category_amount = 0
    for y in range(0, len(expenses)):
        if expenses[y].category == category_name:
            category_amount = category_amount + expenses[y].amount
    print(category_amount)
    expense_amounts.append(category_amount)

for x in range(0,len(expense_categories)):
    print(f"{expense_categories[x]} has an amount of {expense_amounts[x]}")
print(expense_categories)
print(expense_amounts)



# deposits = Deposit.query.filter(Deposit.acct_id != "").all()[::-1]
# for x in range(0,len(deposits)):
#     print(deposits[x])
