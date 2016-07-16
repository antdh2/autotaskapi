from django.shortcuts import render
from django.shortcuts import render_to_response

import atws


# Create your views here.
def index(request):
    # First we must connect to autotask using valid credentials
    at = atws.connect(username='ant.horner@eye-techit.com',password='Mnschnaap1!')
    # Then we need to grab a query object using autotask wrapper
    query = atws.Query('Account')
    # Then filter what we want the query object to grab using SQL
    query.WHERE('id',query.Equals,29774062)
    # Assign the generator from query object to a list which we can interact with
    accounts = at.query(query).fetch_one()
    # Loop through tuples in accounts to find the field AccountName and check it's equal to user input
    # Then print that
    for field, value in accounts:
        if field == "AccountName" and value == "test":
            account_name_field = field
            account_name_value = value
        if field == "id":
            account_id_field = field
            account_id_value = str(value)
    return render_to_response('index.html', {"account_name_field": account_name_value, "account_id_field": account_id_value, "accounts": accounts})
