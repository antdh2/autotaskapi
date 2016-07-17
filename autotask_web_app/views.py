from django.shortcuts import render
from django.shortcuts import render_to_response

import atws



# First we must connect to autotask using valid credentials
at = atws.connect(username='ant.horner@eye-techit.com',password='Mnschnaap1!')

# Create your views here.
def index(request):
    # Once an account name/id is entered
    if request.method == "POST":
        # map account_id to the inputted value
        account_id = request.POST['input-account-id']
        # then get autotask account using that ID
        # accounts = get_account(account_id)

        accounts = resolve_account_name(account_id)

    else:
        account_id = None
        accounts = None



    return render(request, 'index.html', {"account_id": account_id, "accounts": accounts})


def get_account(account_id):
    # Then we need to grab a query object using autotask wrapper
    query = atws.Query('Account')
    # Then filter what we want the query object to grab using SQL
    query.WHERE('id',query.Equals,account_id)
    # Assign the generator from query object to a list which we can interact with
    accounts = at.query(query).fetch_one()
    return accounts

def get_tickets_for_account(account_id):
    tquery = atws.Query('Ticket')
    tquery.WHERE('AccountID',query.Equals,account_id)
    tickets = at.query(tquery).fetch_one()


def resolve_account_name(string):
    aquery = atws.Query('Account')
    aquery.WHERE('AccountName',aquery.Equals,string)
    accounts = at.query(aquery).fetch_one()
    for field, value in accounts:
        if field == "AccountName" and value == string:
            return accounts
