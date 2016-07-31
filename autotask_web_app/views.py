from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.contrib import messages
from django.http import HttpResponse
import time
import datetime


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

def create_upsell(request, id):
    account_id = id
    account = get_account(account_id)

    try:
        if request.method == 'POST':
            AVG = request.POST.get('AVG', False)
            SSD128 = request.POST.get('SSD128', False)
            SSD256 = request.POST.get('SSD256', False)
            SSD512 = request.POST.get('SSD512', False)
            HDD50025 = request.POST.get('HDD50025', False)
            HDD100025 = request.POST.get('HDD100025', False)
            HDD50035 = request.POST.get('HDD50035', False)
            HDD100035 = request.POST.get('HDD100035', False)
            # First we need to create a new opportunity
            new_opportunity = at.new('Opportunity')
            new_opportunity.AccountID = account_id
            new_opportunity.Amount = 5
            new_opportunity.Cost = 1
            new_opportunity.CreateDate = time.strftime("%d.%m.%Y")
            new_opportunity.OwnerResourceID = 29715730 # AH
            new_opportunity.Probability = 100
            new_opportunity.ProjectedCloseDate = time.strftime("%d.%m.%Y")
            new_opportunity.Stage = atvar.Opportunity_Stage_QWOrderReceived
            new_opportunity.Status = atvar.Opportunity_Status_Active
            new_opportunity.Title = "Upsell"
            new_opportunity.UseQuoteTotals = False
            new_opportunity.LeadReferral = atvar.Opportunity_LeadReferral_SalesOfficeSuggestion
            opportunity = at.create(new_opportunity).fetch_one()
            # Before creating a quote we must have a quote location
            new_quote_location = at.new('QuoteLocation')
            new_quote_location.Address1 = account.Address1
            new_quote_location.Address2 = account.Address2
            new_quote_location.City = account.City
            new_quote_location.PostalCode = account.PostalCode
            quote_location = at.create(new_quote_location).fetch_one()
            # Then we need to create a quote with the items in
            new_quote = at.new('Quote')
            new_quote.AccountID = account_id
            new_quote.BillToLocationID = quote_location.id
            # Need to grab a contact to extract the id
            contact = get_contact_for_account(account_id)
            new_quote.ContactID = contact.id
            new_quote.EffectiveDate = time.strftime("%d.%m.%Y")
            new_quote.ExpirationDate = '14.08.2016'
            new_quote.Name = "New Upsell Quote"
            new_quote.OpportunityID = opportunity.id
            new_quote.ShipToLocationID = quote_location.id
            new_quote.SoldToLocationID = quote_location.id
            quote = at.create(new_quote).fetch_one()
            # Now we need to add in the items that are not defined as False at post method
            new_quote_item = at.new('QuoteItem')
            new_quote_item.IsOptional = False
            new_quote_item.LineDiscount = 0
            new_quote_item.PercentageDiscount = 0
            new_quote_item.Quantity = 1
            new_quote_item.QuoteID = quote.id
            new_quote_item.ProductID = 29729474
            new_quote_item.PeriodType = atvar.QuoteItem_PeriodType_OneTime
            new_quote_item.Type = atvar.QuoteItem_Type_Product
            new_quote_item.UnitDiscount = 0
            new_quote_item.Name = 'Test Item Name'
            quote_item = at.create(new_quote_item).fetch_one()



    except NameError:
        opportunity = None
        return render(request, 'create_upsell.html', {"account": account, "opportunity": opportunity})
    opportunity = None

    return render(request, 'create_upsell.html', {"account": account, "opportunity": opportunity})

# For booking in form only
ticket_account = {}
ticket_contact = {}
ticket_sheet_obj = {}
ticket_misc = {}
# For booking in form only
def booking_in_form(request):
    page = "booking_in_form"
    step = 1
    if request.method == 'POST':
        if request.POST.get('step1', False):
            # first we need to check this account doesn't already exist
            # then we need to create an account
            # set the step to 2 and return to the page
            account_name = request.POST['account-name']
            account_exist = check_account_exists(account_name)
            if account_exist:
                # if an account exists then show error message
                messages.add_message(request, messages.ERROR, 'Account already exists and has been selected. Please continue with the booking in process.')
                # Then grab that account to continue with the form
                account_id = resolve_account_id(account_name)
                account = get_account(account_id)
                ticket_account['AccountID'] = account_id
                ticket_account['AccountObj'] = account
                # Now we need to find a contact for the account
                # First we need to find all contacts with an AccountID equal to our account.id object
                contacts = get_contacts_for_account(account_id)
                # Then we need to loop through each of these and display them to the user to select the appropriate contact. This is done on frontend
                # Then update our contact arrays
                step = 2
                return render(request, 'booking_in_form.html', {"contacts": contacts, "page": page, "at": at, "step": step, "ACCOUNT_TYPES": ACCOUNT_TYPES, "PRIORITY": PRIORITY, "STATUS": STATUS, "QUEUE_IDS": QUEUE_IDS, "ticket_account": ticket_account, "ticket_contact": ticket_contact, "ticket_sheet_obj": ticket_sheet_obj, "ticket_misc": ticket_misc})
            else:
                # else process the form and create a new account
                # then need to create a new contact for that account
                new_account = at.new('Account')
                new_account.AccountName = request.POST['account-name']
                new_account.Address1 = request.POST['address1']
                new_account.Address2 = request.POST['address2']
                new_account.City = request.POST['city']
                new_account.PostalCode = request.POST['postcode']
                new_account.Phone = request.POST['phone']
                new_account.AccountType = request.POST['type']
                new_account.OwnerResourceID = 29683570
                account = at.create(new_account).fetch_one()
                # now create a contact
                new_contact = at.new('Contact')
                new_contact.FirstName = request.POST['firstname']
                new_contact.LastName = request.POST['surname']
                new_contact.EMailAddress = request.POST['email']
                new_contact.AddressLine = request.POST['address1']
                new_contact.AddressLine1 = request.POST['address2']
                new_contact.City = request.POST['city']
                new_contact.ZipCode = request.POST['postcode']
                new_contact.Phone = request.POST['phone']
                new_contact.Active = 1
                account_id = resolve_account_id(account_name)
                new_contact.AccountID = account_id
                # append account_id to a dict to use for making sure ticket is added to right account
                ticket_account['AccountID'] = account_id
                ticket_account['AccountObj'] = account
                contact = at.create(new_contact).fetch_one()
                step = 2
                messages.add_message(request, messages.SUCCESS, 'Successfully created account')

                # update contact info to add contacts to ticket creation
                ticket_contact['ContactID'] = contact.id
                ticket_contact['ContactObj'] = contact
        if request.POST.get('step2', False):
            # first grab account from step 1
            # then create a new autotask ticket from form fields
            new_ticket = at.new('Ticket')
            new_ticket.AccountID = ticket_account['AccountID']
            # this is for list of contacts displayed
            if not ticket_contact['ContactID']:
                ticket_contact['ContactID'] = request.POST['contact']
            new_ticket.ContactID = ticket_contact['ContactID']
            new_ticket.Title = request.POST['title']
            new_ticket.Description = request.POST['description']
            new_ticket.DueDateTime = request.POST['duedatetime']
            new_ticket.EstimatedHours = request.POST['estimatedhours']
            new_ticket.Priority = request.POST['priority']
            new_ticket.Status = request.POST['status']
            new_ticket.QueueID = request.POST['queueid']
            new_ticket.Source = atvar.Ticket_Source_InPersonatSupportCentre
            ticket = at.create(new_ticket).fetch_one()
            step = 3
            ticket_sheet_obj['Ticket'] = ticket
        if request.POST.get('step3', False):
            ticket_misc['software_collected'] = request.POST['software-collected']
            ticket_misc['chargers_collected'] = request.POST['chargers-collected']
            ticket_misc['cables_collected'] = request.POST['cables-collected']
            ticket_misc['item'] = request.POST['item']
            ticket_misc['passwords'] = request.POST['passwords']
            ticket_misc['action_required'] = request.POST['action-required']
            ticket_misc['software_legitimacy'] = request.POST['software-legitimacy']
            ticket_misc['condition'] = request.POST['condition']
            ticket_misc['ifotheraction'] = request.POST['ifotheraction']
            ticket_misc['damaged'] = request.POST['damaged']
            ticket_misc['front'] = request.POST['front']
            ticket_misc['lside'] = request.POST['lside']
            ticket_misc['rside'] = request.POST['rside']
            ticket_misc['top'] = request.POST['top']
            ticket_misc['bottom'] = request.POST['bottom']
            ticket_misc['screen'] = request.POST['screen']
            ticket_misc['cables'] = request.POST['cables']
            ticket_misc['keyboard'] = request.POST['keyboard']
            ticket_misc['other'] = request.POST['other']
            step = 4
            messages.add_message(request, messages.SUCCESS, 'Successfully gathered customer information')


    return render(request, 'booking_in_form.html', {"page": page, "at": at, "step": step, "ACCOUNT_TYPES": ACCOUNT_TYPES, "PRIORITY": PRIORITY, "STATUS": STATUS, "QUEUE_IDS": QUEUE_IDS, "ticket_account": ticket_account, "ticket_contact": ticket_contact, "ticket_sheet_obj": ticket_sheet_obj, "ticket_misc": ticket_misc})


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


def check_account_exists(account_name):
    aquery = atws.Query('Account')
    aquery.WHERE('AccountName',aquery.Equals,account_name)
    accounts = at.query(aquery).fetch_all()
    if accounts:
        return True
    else:
        return False

def get_contact_for_account(account_id):
    tquery = atws.Query('Contact')
    tquery.WHERE('AccountID',tquery.Equals,account_id)
    contact = at.query(tquery).fetch_one()
    return contact

def get_contacts_for_account(account_id):
    tquery = atws.Query('Contact')
    tquery.WHERE('AccountID',tquery.Equals,account_id)
    contact = at.query(tquery).fetch_all()
    return contact


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
