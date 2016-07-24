from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.contrib import messages
from django.http import HttpResponse

import atws
from autotask_api_app import atvar

at = None
accounts = None
step = 1

TICKET_SOURCES = {
    "LinkedIn": atvar.Ticket_Source_LinkedIn,
    "In Person at Support Centre": atvar.Ticket_Source_InPersonatSupportCentre,
    "Unspecified": atvar.Ticket_Source_Unspecified,
    "Facebook": atvar.Ticket_Source_Facebook,
    "Contractual": atvar.Ticket_Source_Contractual,
    "Telephone": atvar.Ticket_Source_Telephone,
    "On Site Request": atvar.Ticket_Source_OnSiteRequest,
    "Complaint": atvar.Ticket_Source_Complaint,
    "Twitter": atvar.Ticket_Source_Twitter,
    "Insourced": atvar.Ticket_Source_Insourced,
    "Remote Monitor": atvar.Ticket_Source_RemoteMonitor,
    "Client Portal": atvar.Ticket_Source_ClientPortal,
    "Sales Office": atvar.Ticket_Source_SalesOffice,
    "Backup": atvar.Ticket_Source_Backup,
    "Email": atvar.Ticket_Source_Email,
}

QUEUE_IDS = {
    "Monthlies": atvar.Ticket_QueueID_Monthlies,
    "Customer Services": atvar.Ticket_QueueID_CustomerServices,
    "Client Project Tickets": atvar.Ticket_QueueID_ClientProjectTickets,
    "Backup Tickets": atvar.Ticket_QueueID_BackupTickets,
    "Sales Office": atvar.Ticket_QueueID_SalesOffice,
    "Bridges Electrical": atvar.Ticket_QueueID_BridgesElectrical,
    "Home User Tickets": atvar.Ticket_QueueID_HomeUserTickets,
    "Post Sale": atvar.Ticket_QueueID_PostSale,
    "Gadget Repairs": atvar.Ticket_QueueID_GadgetRepairs,
    "Recurring Tickets": atvar.Ticket_QueueID_RecurringTickets,
    "Monitoring Alert": atvar.Ticket_QueueID_MonitoringAlert,
    "Management": atvar.Ticket_QueueID_Management,
    "Support Desk": atvar.Ticket_QueueID_SupportDesk,
    "ETIT Internal": atvar.Ticket_QueueID_ETITInternal,
    "Client Portal": atvar.Ticket_QueueID_ClientPortal,
    "Selwood Taskfire": atvar.Ticket_QueueID_SelwoodTaskfire,
    "Ready for Invoicing": atvar.Ticket_QueueID_ReadyforInvoicing,
}

PRIORITY = {
    "Low": atvar.Ticket_Priority_Low,
    "Critical": atvar.Ticket_Priority_Critical,
    "High": atvar.Ticket_Priority_High,
    "Awaiting Assessment": atvar.Ticket_Priority_AwaitingAssessment,
    "Medium": atvar.Ticket_Priority_Medium,
}

STATUS = {
    "In Progress": atvar.Ticket_Status_InProgress,
    "On Hold": atvar.Ticket_Status_OnHold,
    "Note Added By Email": atvar.Ticket_Status_NoteAddedbyEmail,
    "Complete: to be Collected": atvar.Ticket_Status_CompletetobeCollected,
    "Monitoring": atvar.Ticket_Status_Monitoring,
    "With Sales Office": atvar.Ticket_Status_WithSalesOffice,
    "Escalated": atvar.Ticket_Status_Escalated,
    "Complete": atvar.Ticket_Status_Complete,
    "New": atvar.Ticket_Status_New,
    "Goods Received": atvar.Ticket_Status_GoodsReceived,
    "Waiting Customer": atvar.Ticket_Status_WaitingCustomer,
    "Engineer Dispatched": atvar.Ticket_Status_EngineerDispatched,
    "With Customer Services": atvar.Ticket_Status_WithCustomerServices ,
    "Waiting Approval": atvar.Ticket_Status_WaitingApproval,
    "Waiting 3rd Party": atvar.Ticket_Status_Waiting3rdParty,
    "Assessed": atvar.Ticket_Status_Assessed,
    "Booked With Customer": atvar.Ticket_Status_BookedwithCustomer,
    "Ready for Invoicing": atvar.Ticket_Status_ReadyforInvoicing,
}

ACCOUNT_TYPES = {
    "Lead": atvar.Account_AccountType_Lead,
    "Dead": atvar.Account_AccountType_Dead,
    "Vendor": atvar.Account_AccountType_Vendor,
    "Partner": atvar.Account_AccountType_Partner,
    "Prospect": atvar.Account_AccountType_Prospect,
    "Customer": atvar.Account_AccountType_Customer,
    "Cancellation": atvar.Account_AccountType_Cancellation,
}

RESOURCE_ROLES = {
    "Engineer": 29682834,
    "Admin": 29683587,
    "Home User Engineer": 29683586,
    "Sales": 29683582,

}

def autotask_login(request):
    page = 'settings'
    # First we must connect to autotask using valid credentials
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        autotask_login_function(username, password)
        messages.add_message(request, messages.SUCCESS, 'Successfully logged in. You may now search for an Autotask account.')
        return render(request, 'index.html', {"page": page, "at": at})
    else:
        return render(request, 'autotask_login.html', {"page": page, "at": at})

def autotask_login_function(username, password):
    global at
    at = atws.connect(username=username,password=password)
    return at

# Create your views here.
def index(request):
    try:
        page = 'index'
        accounts = None
        # Once an account name/id is entered
        if request.method == "POST":
            # map account_id to the inputted value
            account_name = request.POST['account-name']
            accounts = resolve_account_name(account_name)
            #account_id = resolve_account_id(account_name)
            # then get autotask account using that ID
        else:
            accounts = None

        return render(request, 'index.html', {"accounts": accounts, "page": page, "at": at, "ACCOUNT_TYPES": ACCOUNT_TYPES})
    except AttributeError:
        messages.add_message(request, messages.ERROR, 'Lost connection with Autotask.')
        return render(request, 'index.html', {"at": at, "ACCOUNT_TYPES": ACCOUNT_TYPES})


def ticket_detail(request, account_id, ticket_id):
    try:
        page = 'ticket_detail'
        account = get_account(account_id)
        ticket = get_ticket_from_id(ticket_id)
        assigned_resource_id = ''
        for key, value in ticket:
            if key == 'ContactID':
                contact_id = value
            if key == 'CreatorResourceID':
                resource_id = value
            if key == 'AssignedResourceID':
                assigned_resource_id = value
        contact = get_contact_for_ticket(contact_id)
        resource = get_resource_from_id(resource_id)
        if assigned_resource_id:
            assigned_resource = get_resource_from_id(assigned_resource_id)
        else:
            assigned_resource = "No Resource Set"
        return render(request, 'ticket.html', {"account": account, "ticket": ticket, "contact": contact, "resource": resource, "assigned_resource": assigned_resource, "TICKET_SOURCES": TICKET_SOURCES, "STATUS": STATUS, "PRIORITY": PRIORITY, "QUEUE_IDS": QUEUE_IDS, "RESOURCE_ROLES": RESOURCE_ROLES})
    except AttributeError:
        messages.add_message(request, messages.ERROR, 'Lost connection with Autotask.')
        return render(request, 'index.html', {"at": at, "ACCOUNT_TYPES": ACCOUNT_TYPES})


def account(request, id):
    account_id = id
    account = get_account(account_id)
    tickets = get_tickets_for_account(account_id)
    ticket_account_name = resolve_account_name_from_id(account_id)
    ticket_info = get_ticket_info(tickets)
    return render(request, 'account.html', {"account": account, "tickets": tickets, "ticket_account_name": ticket_account_name, "ACCOUNT_TYPES": ACCOUNT_TYPES, "QUEUE_IDS": QUEUE_IDS, "TICKET_SOURCES": TICKET_SOURCES})


def edit_account(request, id):
    account_id = id
    account = get_account(account_id)
    if request.method == "POST":
        new_account_name = request.POST['account-name']
        new_address_1 = request.POST['address1']
        new_address_2 = request.POST['address2']
        new_state = request.POST['state']
        new_city = request.POST['city']
        new_postalcode = request.POST['postcode']
        new_phone = request.POST['phone']
        account.AccountName = new_account_name
        account.Address1 = new_address_1
        account.Address2 = new_address_2
        account.State = new_state
        account.City = new_city
        account.PostalCode = new_postalcode
        account.Phone = new_phone
        account.update()
        messages.add_message(request, messages.SUCCESS, 'Successfully edited.')

        return redirect("/account/" + account_id, successMessage="Success!")
    return render(request, 'edit_account.html', {"account": account, "ACCOUNT_TYPES": ACCOUNT_TYPES})




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
    tquery.WHERE('AccountID',tquery.Equals,account_id)
    tickets = at.query(tquery).fetch_all()
    return tickets

def get_ticket_from_id(ticket_id):
    tquery = atws.Query('Ticket')
    tquery.WHERE('id',tquery.Equals,ticket_id)
    ticket = at.query(tquery).fetch_one()
    return ticket


def get_ticket_info(tickets):
    # tickets variable is entered as a LIST of tickets
    # each LIST of tickets have the tuples so I need to loop through each LIST and then unpack into a dict
    ticket_info = {}
    for ticket in tickets:
        i = 0
        for field, value in ticket:
            try:
                ticket_info.update({field:value})
            except ValueError:
                print("Some error with unpacking tuple")
    return ticket_info

def get_individual_ticket_info(ticket):
    ticket_info = {}
    for field, value in ticket:
        try:
            ticket_info.update({field:value})
        except ValueError:
            print("Some error with unpacking tuple")
    return ticket_info

def resolve_account_name(string):
    aquery = atws.Query('Account')
    aquery.WHERE('AccountName',aquery.Contains,string)
    accounts = at.query(aquery).fetch_all()
    return accounts

def resolve_account_id(string):
    aquery = atws.Query('Account')
    aquery.WHERE('AccountName',aquery.Equals,string)
    accounts = at.query(aquery).fetch_one()
    for field, value in accounts:
        if field == "id":
            acc_id = value
        else:
            acc_id = None
        return acc_id

def resolve_account_name_from_id(account_id):
    aquery = atws.Query('Account')
    aquery.WHERE('id',aquery.Equals,account_id)
    accounts = at.query(aquery).fetch_one()
    for field, value in accounts:
        if field == "AccountName":
            account_name = value
            return account_name


def get_resource_from_id(resource_id):
    aquery = atws.Query('Resource')
    aquery.WHERE('id',aquery.Equals,resource_id)
    resource = at.query(aquery).fetch_one()
    return resource

def get_contact_for_ticket(contact_id):
    aquery = atws.Query('Contact')
    aquery.WHERE('id',aquery.Equals,contact_id)
    contact = at.query(aquery).fetch_one()
    return contact


def create_ticket(request, id):
    account_id = id
    account = get_account(account_id)
    if request.method == "POST":
        new_ticket = at.new('Ticket')
        new_ticket.AccountID = account_id
        new_ticket.Title = request.POST['title']
        new_ticket.Description = request.POST['description']
        new_ticket.DueDateTime = request.POST['duedatetime']
        new_ticket.EstimatedHours = request.POST['estimatedhours']
        new_ticket.Priority = request.POST['priority']
        new_ticket.Status = request.POST['status']
        new_ticket.QueueID = request.POST['queueid']

        # custom validation rules
        if new_ticket.EstimatedHours == '3' and new_ticket.Priority == '3':
            messages.add_message(request, messages.ERROR, 'Cannot have Estimated Hours and Priority set to 3 at the same time.')
            return redirect("/account/" + account_id, {"account": account, "PRIORITY": PRIORITY, "QUEUE_IDS": QUEUE_IDS, "STATUS": STATUS})
        else:
            ticket = at.create(new_ticket).fetch_one()
    return render(request, 'create_ticket.html', {"account": account, "PRIORITY": PRIORITY, "QUEUE_IDS": QUEUE_IDS, "STATUS": STATUS})


def create_home_user_ticket(request, id):
    account_id = id
    account = get_account(account_id)

    # Preset fields for home user ticket creation
    title = "Test Home User Ticket"
    description = "Test Home User Description"
    status = atvar.Ticket_Status_New

    # Grab field values from user input, include predefined fields above
    if request.method == "POST":
        new_ticket = at.new('Ticket')
        new_ticket.AccountID = account_id
        new_ticket.Title = request.POST['title']
        new_ticket.Description = request.POST['description']
        new_ticket.DueDateTime = request.POST['duedatetime']
        new_ticket.EstimatedHours = request.POST['estimatedhours']
        new_ticket.Priority = request.POST['priority']
        new_ticket.Status = request.POST['status']
        new_ticket.QueueID = request.POST['queueid']
        # custom validation rules
        if new_ticket.Title != title:
            messages.add_message(request, messages.ERROR, ('Cannot specify title other than ' + title))
            return redirect("create_home_user_ticket.html", {"account": account, "PRIORITY": PRIORITY, "QUEUE_IDS": QUEUE_IDS, "STATUS": STATUS, "title": title, "description": description})
        else:
            ticket = at.create(new_ticket).fetch_one()

    return render(request, 'create_home_user_ticket.html', {"account": account, "PRIORITY": PRIORITY, "QUEUE_IDS": QUEUE_IDS, "STATUS": STATUS, "title": title, "description": description})
