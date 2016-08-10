from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.files import File

import time
import datetime
from datetime import datetime
from datetime import timedelta
import os
import re
import atws
import atws.monkeypatch.attributes
import account.views
import account.forms
import autotask_web_app.forms
# import the wonderful decorator for stripe
from djstripe.decorators import subscription_payment_required
from autotask_api_app import atvar
from .models import Profile, BookingInDetails, Upsell, Picklist
from account.signals import user_logged_in


# Constants
at = None
accounts = None
step = 1


@receiver(post_save, sender=User)
def handle_user_save(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)

############################################################
#
# All views must go inside of here
#
############################################################

def profile(request, id):
    page = 'profile'
    # First we must connect to autotask using valid credentials
    if request.method == "POST":
        if request.POST.get('editprofile', False):
            profile = Profile.objects.filter(user_id=id)
            profile.first_name = request.POST['profile-firstname']
            profile.last_name = request.POST['profile-lastname']
            profile.about = request.POST['profile-about']
            profile.update()
            return render(request, 'account/profile.html', {"page": page, "profile": profile})
        if request.POST.get('autotasklogin', False):
            at = None
            username = request.POST['username']
            password = request.POST['password']
            at = autotask_login_function(request, username, password)
            if at:
                messages.add_message(request, messages.SUCCESS, 'Successfully logged in. You may now search for an Autotask account.')
                return render(request, 'index.html', {"page": page, "at": at})
            else:
                return render(request, 'account/profile.html', {"page": page, "at": at, "profile": profile})

    # Now figure out sales figures
    upsells = Upsell.objects.filter(profile=request.user.profile)
    total_revenue = 0
    total_profit = 0
    for upsell in upsells:
        total_revenue += upsell.product_price
        x = upsell.product_price - upsell.product_cost
        total_profit += x
    return render(request, 'account/profile.html', {"total_revenue": round(total_revenue,2), "upsells": upsells.count, "total_profit": round(total_profit,2)})

def profile_overview(request, id):
    page = 'profile_overview'
    # Work out revenue for user
    upsells = Upsell.objects.filter(profile=request.user.profile)
    total_revenue = 0
    total_profit = 0
    for upsell in upsells:
        total_revenue += upsell.product_price
        x = upsell.product_price - upsell.product_cost
        total_profit += x


    return render(request, 'account/profile_overview.html', {"total_revenue": round(total_revenue,2), "upsells": upsells.count, "total_profit": round(total_profit,2)})

def create_upsell(request, id):
    account_id = id
    ataccount = get_account(account_id)
    sold_products = {}
    test = None
    module = "sales"
    page = "create-upsell"
    try:
        if request.method == 'POST':
            # First we need to create a new opportunity for our quote items (we can validate front end for name to stop a NULL post request)
            opportunity = opportunity_create_new(
                AccountID = account_id,
                Amount = 5,
                Cost = 1,
                CreateDate = time.strftime("%d.%m.%Y"),
                OwnerResourceID = 29715730, # AH
                Probability = 100,
                ProjectedCloseDate = time.strftime("%d.%m.%Y"),
                Stage = atvar.Opportunity_Stage_QWOrderReceived,
                Status = atvar.Opportunity_Status_Active,
                Title = request.POST['opportunity-name'],
                UseQuoteTotals = True,
                LeadReferral = atvar.Opportunity_LeadReferral_SalesOfficeSuggestion,
            )
            # Before creating a quote we must have a quote location (handled in function)
            # Then we need to create a quote with the items in, all done with below function
            quote = quote_create_new(ataccount, opportunity, datetime.now() + timedelta(days=14), opportunity.Title)
            if request.POST.get('AVG', False) != False:
                sold_products['AVG'] = request.POST['AVG-PRICE']
                # Save information to our own DB
                Upsell.objects.create(profile=request.user.profile,
                                      product_name="AVG",
                                      account_id=account_id,
                                      product_id='29729474',
                                      product_cost=5.50,
                                      product_price=float(sold_products['AVG'])/1.2,
                                      opportunity_id=opportunity.id)
                # Now to add item onto quote
                new_quote_item = quote_item_create_new(quote,
                  IsOptional = False,
                  LineDiscount = 0,
                  PercentageDiscount = 0,
                  Quantity = 1,
                  ProductID = 29729474,
                  PeriodType = atvar.QuoteItem_PeriodType_OneTime,
                  Type = atvar.QuoteItem_Type_Product,
                  UnitDiscount = 0,
                  Name = "AVG Internet Security 2016",
                  UnitCost = 5.50,
                  UnitPrice = float(sold_products['AVG'])/1.2,
                )
            if request.POST.get('SSD128', False) != False:
                sold_products['SSD128'] = request.POST['SSD128-PRICE']
                # Save information to our own DB
                Upsell.objects.create(profile=request.user.profile,
                                      product_name="SSD128",
                                      account_id=account_id,
                                      product_id='29730653',
                                      product_cost=41.25,
                                      product_price=float(sold_products['SSD128'])/1.2,
                                      opportunity_id=opportunity.id)
                # Now to add item onto quote
                new_quote_item = quote_item_create_new(quote,
                  IsOptional = False,
                  LineDiscount = 0,
                  PercentageDiscount = 0,
                  Quantity = 1,
                  ProductID = 29730653,
                  PeriodType = atvar.QuoteItem_PeriodType_OneTime,
                  Type = atvar.QuoteItem_Type_Product,
                  UnitDiscount = 0,
                  Name = "128GB SSD",
                  UnitCost = 41.25,
                  UnitPrice = float(sold_products['SSD128'])/1.2,
                )
            if request.POST.get('SSD256', False) != False:
                sold_products['SSD256'] = request.POST['SSD256-PRICE']
                # Save information to our own DB
                Upsell.objects.create(profile=request.user.profile,
                                      product_name="SSD256",
                                      account_id=account_id,
                                      product_id='29730661',
                                      product_cost=56.65,
                                      product_price=float(sold_products['SSD256'])/1.2,
                                      opportunity_id=opportunity.id)
                # Now to add item onto quote
                new_quote_item = quote_item_create_new(quote,
                  IsOptional = False,
                  LineDiscount = 0,
                  PercentageDiscount = 0,
                  Quantity = 1,
                  ProductID = 29730661,
                  PeriodType = atvar.QuoteItem_PeriodType_OneTime,
                  Type = atvar.QuoteItem_Type_Product,
                  UnitDiscount = 0,
                  Name = "256GB SSD",
                  UnitCost = 56.65,
                  UnitPrice = float(sold_products['SSD256'])/1.2,
                )
            if request.POST.get('SSD512', False) != False:
                sold_products['SSD512'] = request.POST['SSD512-PRICE']
                # Save information to our own DB
                Upsell.objects.create(profile=request.user.profile,
                                      product_name="SSD512",
                                      account_id=account_id,
                                      product_id='29730506',
                                      product_cost=125.36,
                                      product_price=float(sold_products['SSD512'])/1.2,
                                      opportunity_id=opportunity.id)
                # Now to add item onto quote
                new_quote_item = quote_item_create_new(quote,
                  IsOptional = False,
                  LineDiscount = 0,
                  PercentageDiscount = 0,
                  Quantity = 1,
                  ProductID = 29730506,
                  PeriodType = atvar.QuoteItem_PeriodType_OneTime,
                  Type = atvar.QuoteItem_Type_Product,
                  UnitDiscount = 0,
                  Name = "512GB SSD",
                  UnitCost = 125.36,
                  UnitPrice = float(sold_products['SSD512'])/1.2,
                )
            if request.POST.get('HDD50025', False) != False:
                sold_products['HDD50025'] = request.POST['HDD50025-PRICE']
                # Save information to our own DB
                Upsell.objects.create(profile=request.user.profile,
                                      product_name="HDD50025",
                                      account_id=account_id,
                                      product_id='29730662',
                                      product_cost=35.40,
                                      product_price=float(sold_products['HDD50025'])/1.2,
                                      opportunity_id=opportunity.id)
                # Now to add item onto quote
                new_quote_item = quote_item_create_new(quote,
                  IsOptional = False,
                  LineDiscount = 0,
                  PercentageDiscount = 0,
                  Quantity = 1,
                  ProductID = 29730662,
                  PeriodType = atvar.QuoteItem_PeriodType_OneTime,
                  Type = atvar.QuoteItem_Type_Product,
                  UnitDiscount = 0,
                  Name = '2.5" 500GB HDD',
                  UnitCost = 35.40,
                  UnitPrice = float(sold_products['HDD50025'])/1.2,
                )
            if request.POST.get('HDD100025', False) != False:
                sold_products['HDD100025'] = request.POST['HDD100025-PRICE']
                # Save information to our own DB
                Upsell.objects.create(profile=request.user.profile,
                                      product_name="HDD100025",
                                      account_id=account_id,
                                      product_id='29730663',
                                      product_cost=36.24,
                                      product_price=float(sold_products['HDD100025'])/1.2,
                                      opportunity_id=opportunity.id)
                # Now to add item onto quote
                new_quote_item = quote_item_create_new(quote,
                  IsOptional = False,
                  LineDiscount = 0,
                  PercentageDiscount = 0,
                  Quantity = 1,
                  ProductID = 29730663,
                  PeriodType = atvar.QuoteItem_PeriodType_OneTime,
                  Type = atvar.QuoteItem_Type_Product,
                  UnitDiscount = 0,
                  Name = '2.5" 1TB HDD',
                  UnitCost = 36.24,
                  UnitPrice = float(sold_products['HDD100025'])/1.2,
                )
            if request.POST.get('HDD50035', False) != False:
                sold_products['HDD50035'] = request.POST['HDD50035-PRICE']
                # Save information to our own DB
                Upsell.objects.create(profile=request.user.profile,
                                      product_name="HDD50035",
                                      account_id=account_id,
                                      product_id='29730037',
                                      product_cost=35.82,
                                      product_price=float(sold_products['HDD50035'])/1.2,
                                      opportunity_id=opportunity.id)
                # Now to add item onto quote
                new_quote_item = quote_item_create_new(quote,
                  IsOptional = False,
                  LineDiscount = 0,
                  PercentageDiscount = 0,
                  Quantity = 1,
                  ProductID = 29730037,
                  PeriodType = atvar.QuoteItem_PeriodType_OneTime,
                  Type = atvar.QuoteItem_Type_Product,
                  UnitDiscount = 0,
                  Name = '3.5" 500GB HDD',
                  UnitCost = 35.82,
                  UnitPrice = float(sold_products['HDD50035'])/1.2,
                )
            if request.POST.get('HDD100035', False) != False:
                sold_products['HDD100035'] = request.POST['HDD100035-PRICE']
                # Save information to our own DB
                Upsell.objects.create(profile=request.user.profile,
                                      product_name="HDD100035",
                                      account_id=account_id,
                                      product_id='29730664',
                                      product_cost=36.24,
                                      product_price=float(sold_products['HDD100035'])/1.2,
                                      opportunity_id=opportunity.id)
                # Now to add item onto quote
                new_quote_item = quote_item_create_new(quote,
                  IsOptional = False,
                  LineDiscount = 0,
                  PercentageDiscount = 0,
                  Quantity = 1,
                  ProductID = 29730664,
                  PeriodType = atvar.QuoteItem_PeriodType_OneTime,
                  Type = atvar.QuoteItem_Type_Product,
                  UnitDiscount = 0,
                  Name = '3.5" 1TB HDD',
                  UnitCost = 36.24,
                  UnitPrice = float(sold_products['HDD100035'])/1.2,
                )

    except NameError:
        opportunity = None
        return render(request, 'create_upsell.html', {"ataccount": ataccount, "opportunity": opportunity})
    opportunity = None

    return render(request, 'create_upsell.html', {"ataccount": ataccount, "opportunity": opportunity, "sold_products": sold_products, "test": test})

# For booking in form only
ticket_account = {}
ticket_contact = {}
ticket_sheet_obj = {}
ticket_misc = {}
opportunity_obj = {}
bookingin_obj = {}
@login_required(login_url='/account/login/')
@subscription_payment_required
def booking_in_form(request):
    module = "customerservices"
    page = "booking-in-form"
    step = 1
    bookingindetails = None
    contacts = None
    if request.user:
        at = autotask_login_function(request, request.user.profile.autotask_username, request.user.profile.autotask_password)
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
                ataccount = get_account(account_id)
                ticket_account['AccountID'] = account_id
                ticket_account['AccountObj'] = ataccount
                # Now we need to find a contact for the account
                # First we need to find all contacts with an AccountID equal to our account.id object
                contacts = get_contacts_for_account(account_id)
                # Then we need to loop through each of these and display them to the user to select the appropriate contact. This is done on frontend
                # Then update our contact arrays
                step = 2
                return render(request, 'booking_in_form.html', {"contacts": contacts, "page": page, "module": module, "at": at, "step": step, "ACCOUNT_TYPES": ACCOUNT_TYPES, "PRIORITY": PRIORITY, "STATUS": STATUS, "QUEUE_IDS": QUEUE_IDS, "ticket_account": ticket_account, "ticket_contact": ticket_contact, "ticket_sheet_obj": ticket_sheet_obj, "ticket_misc": ticket_misc})
            else:
                # else process the form and create a new account
                # then need to create a new contact for that account
                new_account = account_create_new(True,
                    AccountName = request.POST['account-name'],
                    Address1 = request.POST['address1'],
                    Address2 = request.POST['address2'],
                    City = request.POST['city'],
                    PostalCode = request.POST['postcode'],
                    Phone = request.POST['phone'],
                    AccountType = request.POST['type'],
                    OwnerResourceID = 29683570
                )

                # now create a contact, first we must get and pass in the account ID
                account_id = resolve_account_id(account_name)
                new_contact = contact_create_new(True,
                    FirstName = request.POST['firstname'],
                    LastName = request.POST['surname'],
                    EMailAddress = request.POST['email'],
                    AddressLine = request.POST['address1'],
                    AddressLine1 = request.POST['address2'],
                    City = request.POST['city'],
                    ZipCode = request.POST['postcode'],
                    Phone = request.POST['phone'],
                    Active = 1,
                    AccountID = account_id
                )

                # append account_id to a dict to use for making sure ticket is added to right account
                ticket_account['AccountID'] = account_id
                ticket_account['AccountObj'] = new_account
                step = 2
                messages.add_message(request, messages.SUCCESS, 'Successfully created account')

                # update contact info to add contacts to ticket creation
                ticket_contact['ContactID'] = new_contact.id
                ticket_contact['ContactObj'] = new_contact
        if request.POST.get('step2', False):
            # Now to grab all input from user for additional fields
            # But first we must create a BookingInDetails object to store data in the DB
            bookingindetails = BookingInDetails.objects.create(profile=request.user.profile)
            bookingindetails.account_id = ticket_account['AccountID']
            bookingindetails.software_collected = request.POST['software-collected']
            bookingindetails.chargers_collected = request.POST['chargers-collected']
            bookingindetails.cables_collected = request.POST['cables-collected']
            bookingindetails.item = request.POST['item']
            bookingindetails.passwords = request.POST['passwords']
            bookingindetails.action_required = request.POST['action-required']
            bookingindetails.software_legitimacy = request.POST['software-legitimacy']
            bookingindetails.condition = request.POST['condition']
            bookingindetails.ifotheraction = request.POST['ifotheraction']
            bookingindetails.damaged = request.POST['damaged']
            bookingindetails.front = request.POST['front']
            bookingindetails.lside = request.POST['lside']
            bookingindetails.rside = request.POST['rside']
            bookingindetails.top = request.POST['top']
            bookingindetails.bottom = request.POST['bottom']
            bookingindetails.screen = request.POST['screen']
            bookingindetails.cables = request.POST['cables']
            bookingindetails.keyboard = request.POST['keyboard']
            bookingindetails.other = request.POST['other']
            bookingindetails.save()
            bookingin_obj['id'] = bookingindetails.id
            # If booking in an MOT then create the opportunity and quote
            if request.POST['action-required'] == "MOT":
                opportunity = opportunity_create_new(
                    AccountID = ticket_account['AccountID'],
                    Amount = 5,
                    Cost = 1,
                    CreateDate = time.strftime("%d.%m.%Y"),
                    OwnerResourceID = 29715730, # AH
                    Probability = 100,
                    ProjectedCloseDate = time.strftime("%d.%m.%Y"),
                    Stage = atvar.Opportunity_Stage_QWOrderReceived,
                    Status = atvar.Opportunity_Status_Active,
                    Title = request.POST['action-required'],
                    UseQuoteTotals = True,
                    LeadReferral = atvar.Opportunity_LeadReferral_SalesOfficeSuggestion,
                )
                # Save information for upsell to our own DB
                upsell = Upsell.objects.create(profile=request.user.profile,
                                      product_name="MOT",
                                      account_id=ticket_account['AccountID'],
                                      product_id='29690896',
                                      product_cost=0,
                                      product_price=float(49)/1.2,
                                      opportunity_id=opportunity.id)
                ticket_misc['allocationcodeid'] = upsell.product_id
                opportunity_obj['OpportunityId'] = opportunity.id
                opportunity_obj['Opportunity'] = opportunity
                # Before creating a quote we must have a quote location (handled in function)
                # Then we need to create a quote with the items in, all done with below function
                quote = quote_create_new(ticket_account['AccountObj'], opportunity, datetime.now() + timedelta(days=14), opportunity.Title)
            # If booking in an Diagnostic then create the opportunity and quote
            if request.POST['action-required'] == "Diagnostic":
                opportunity = opportunity_create_new(
                    AccountID = ticket_account['AccountID'],
                    Amount = 5,
                    Cost = 1,
                    CreateDate = time.strftime("%d.%m.%Y"),
                    OwnerResourceID = 29715730, # AH
                    Probability = 100,
                    ProjectedCloseDate = time.strftime("%d.%m.%Y"),
                    Stage = atvar.Opportunity_Stage_QWOrderReceived,
                    Status = atvar.Opportunity_Status_Active,
                    Title = request.POST['action-required'],
                    UseQuoteTotals = True,
                    LeadReferral = atvar.Opportunity_LeadReferral_SalesOfficeSuggestion,
                )
                # Save information for upsell to our own DB
                upsell = Upsell.objects.create(profile=request.user.profile,
                                      product_name="Diagnostic",
                                      account_id=ticket_account['AccountID'],
                                      product_id='29690897',
                                      product_cost=0,
                                      product_price=float(25)/1.2,
                                      opportunity_id=opportunity.id)
                ticket_misc['allocationcodeid'] = upsell.product_id
                opportunity_obj['OpportunityId'] = opportunity.id
                opportunity_obj['Opportunity'] = opportunity
                # Before creating a quote we must have a quote location (handled in function)
                # Then we need to create a quote with the items in, all done with below function
                quote = quote_create_new(ticket_account['AccountObj'], opportunity, datetime.now() + timedelta(days=14), opportunity.Title)
            # If booking in a Reload then create the opportunity and quote
            if request.POST['action-required'] == "Reload":
                opportunity = opportunity_create_new(
                    AccountID = ticket_account['AccountID'],
                    Amount = 5,
                    Cost = 1,
                    CreateDate = time.strftime("%d.%m.%Y"),
                    OwnerResourceID = 29715730, # AH
                    Probability = 100,
                    ProjectedCloseDate = time.strftime("%d.%m.%Y"),
                    Stage = atvar.Opportunity_Stage_QWOrderReceived,
                    Status = atvar.Opportunity_Status_Active,
                    Title = request.POST['action-required'],
                    UseQuoteTotals = True,
                    LeadReferral = atvar.Opportunity_LeadReferral_SalesOfficeSuggestion,
                )
                # Save information for upsell to our own DB
                upsell = Upsell.objects.create(profile=request.user.profile,
                                              product_name="Reload",
                                              account_id=ticket_account['AccountID'],
                                              product_id='29690898',
                                              product_cost=0,
                                              product_price=float(90)/1.2,
                                              opportunity_id=opportunity.id)
                ticket_misc['allocationcodeid'] = upsell.product_id
                opportunity_obj['OpportunityId'] = opportunity.id
                opportunity_obj['Opportunity'] = opportunity
                # Before creating a quote we must have a quote location (handled in function)
                # Then we need to create a quote with the items in, all done with below function
                quote = quote_create_new(ticket_account['AccountObj'], opportunity, datetime.now() + timedelta(days=14), opportunity.Title)
            # Set which option was selected to a dict so we can access it in step 3 for ticket cost item
            ticket_misc['action-required'] = request.POST['action-required']
            # Now we need to find a contact for the account
            # First we need to find all contacts with an AccountID equal to our account.id object
            contacts = get_contacts_for_account(ticket_account['AccountID'])
            step = 3
            messages.add_message(request, messages.SUCCESS, 'Successfully gathered customer information')
        if request.POST.get('step3', False):
            # this is for list of contacts displayed
            ticket_contact['ContactID'] = request.POST['contact']
            # first grab account from step 1
            # then create a new autotask ticket from form fields
            new_ticket = ticket_create_new(True,
                AccountID = ticket_account['AccountID'],
                ContactID = ticket_contact['ContactID'],
                Title = request.POST['title'],
                Description = request.POST['description'],
                DueDateTime = request.POST['duedatetime'],
                EstimatedHours = request.POST['estimatedhours'],
                Priority = request.POST['priority'],
                Status = request.POST['status'],
                QueueID = request.POST['queueid'],
                Source = atvar.Ticket_Source_InPersonatSupportCentre,
                OpportunityId = opportunity_obj['OpportunityId']
            )
            step = 4
            # Update DB entry with ticket information
            ticket_sheet_obj['Ticket'] = new_ticket
            bookingindetail_to_update = BookingInDetails.objects.get(id=bookingin_obj['id'])
            bookingindetail_to_update.ticket_id = new_ticket.TicketNumber
            bookingindetail_to_update.save()
            # Now we add the relevent charge onto the ticket.
            if ticket_misc['action-required'] == "MOT":
                ticket_cost_item = ticket_cost_item_create_new(new_ticket,
                    Name = "PC MOT Service Charge",
                    AllocationCodeID = int(ticket_misc['allocationcodeid']),
                    CostType = 1,
                    DatePurchased = time.strftime("%d.%m.%Y"),
                    UnitQuantity = 1)
            if ticket_misc['action-required'] == "Diagnostic":
                ticket_cost_item = ticket_cost_item_create_new(new_ticket,
                    Name = "PC Diagnostic Service Charge",
                    AllocationCodeID = int(ticket_misc['allocationcodeid']),
                    CostType = 1,
                    DatePurchased = time.strftime("%d.%m.%Y"),
                    UnitQuantity = 1)
            if ticket_misc['action-required'] == "Reload":
                ticket_cost_item = ticket_cost_item_create_new(new_ticket,
                    Name = "PC Reload Service Charge",
                    AllocationCodeID = int(ticket_misc['allocationcodeid']),
                    CostType = 1,
                    DatePurchased = time.strftime("%d.%m.%Y"),
                    UnitQuantity = 1)

    return render(request, 'booking_in_form.html', {"page": page, "module": module, "at": at, "step": step, "ACCOUNT_TYPES": ACCOUNT_TYPES, "PRIORITY": PRIORITY, "STATUS": STATUS, "QUEUE_IDS": QUEUE_IDS, "ticket_account": ticket_account, "ticket_contact": ticket_contact, "ticket_sheet_obj": ticket_sheet_obj, "ticket_misc": ticket_misc, "bookingindetails": bookingindetails, "contacts": contacts, "opportunity_obj": opportunity_obj, "bookingin_obj": bookingin_obj})


@login_required(login_url='/account/login/')
def index(request):
    try:
        module = 'crm'
        page = 'search-for-account'
        accounts = None
        at = None
        if request.user:
            at = autotask_login_function(request, request.user.profile.autotask_username, request.user.profile.autotask_password)
        # Once an account name/id is entered
        if request.method == "POST":
            # map account_id to the inputted value
            account_name = request.POST['account-name']
            accounts = resolve_account_name(account_name)
            #account_id = resolve_account_id(account_name)
            # then get autotask account using that ID
        else:
            accounts = None

        return render(request, 'index.html', {"accounts": accounts, "page": page, "module": module, "at": at, "ACCOUNT_TYPES": ACCOUNT_TYPES})
    except AttributeError:
        messages.add_message(request, messages.ERROR, 'Lost connection with Autotask.')
        return render(request, 'index.html', {"at": at, "ACCOUNT_TYPES": ACCOUNT_TYPES})


@login_required(login_url='/account/login/')
def ticket_detail(request, account_id, ticket_id):
    try:
        page = 'ticket_detail'
        ataccount = get_account(account_id)
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
        return render(request, 'ticket.html', {"ataccount": ataccount, "ticket": ticket, "contact": contact, "resource": resource, "assigned_resource": assigned_resource, "TICKET_SOURCES": TICKET_SOURCES, "STATUS": STATUS, "PRIORITY": PRIORITY, "QUEUE_IDS": QUEUE_IDS, "RESOURCE_ROLES": RESOURCE_ROLES})
    except AttributeError:
        messages.add_message(request, messages.ERROR, 'Lost connection with Autotask.')
        return render(request, 'index.html', {"at": at, "ACCOUNT_TYPES": ACCOUNT_TYPES})


@login_required(login_url='/account/login/')
def edit_ataccount(request, id):
    account_id = id
    ataccount = get_account(account_id)
    if request.method == "POST":
        updated_account = account_update(ataccount,
            AccountName = request.POST['account-name'],
            Address1 = request.POST['address1'],
            Address2 = request.POST['address2'],
            State = request.POST['state'],
            City = request.POST['city'],
            PostalCode = request.POST['postcode'],
            Phone = request.POST['phone'],
        )
        messages.add_message(request, messages.SUCCESS, 'Successfully edited account.')
        return redirect("/ataccount/" + account_id)
    return render(request, 'edit_ataccount.html', {"ataccount": ataccount, "ACCOUNT_TYPES": ACCOUNT_TYPES})


@login_required(login_url='/account/login/')
def create_ticket(request, id):
    account_id = id
    ataccount = get_account(account_id)
    if request.method == "POST":
        # custom validation rules
        if request.POST['estimatedhours'] == '3' and request.POST['priority'] == '3':
            messages.add_message(request, messages.ERROR, 'Cannot have Estimated Hours and Priority set to 3 at the same time.')
            return redirect("/ataccount/" + account_id, {"ataccount": ataccount, "PRIORITY": PRIORITY, "QUEUE_IDS": QUEUE_IDS, "STATUS": STATUS})
        else:
            new_ticket = ticket_create_new(True,
                AccountID = account_id,
                Title = request.POST['title'],
                Description = request.POST['description'],
                DueDateTime = request.POST['duedatetime'],
                EstimatedHours = request.POST['estimatedhours'],
                Priority = request.POST['priority'],
                Status = request.POST['status'],
                QueueID = request.POST['queueid'],
            )
            messages.add_message(request, messages.SUCCESS, ('Ticket - ' + new_ticket.TicketNumber + ' - ' + new_ticket.Title + ' created.'))
    return render(request, 'create_ticket.html', {"ataccount": ataccount, "PRIORITY": PRIORITY, "QUEUE_IDS": QUEUE_IDS, "STATUS": STATUS})


@login_required(login_url='/account/login/')
def create_home_user_ticket(request, id):
    account_id = id
    ataccount = get_account(account_id)
    # Preset fields for home user ticket creation
    title = "Test Home User Ticket"
    description = "Test Home User Description"
    status = atvar.Ticket_Status_New
    # Grab field values from user input, include predefined fields above
    if request.method == "POST":
        # custom validation rules
        if request.POST['title'] != title:
            messages.add_message(request, messages.ERROR, ('Cannot specify title other than ' + title))
            return redirect("create_home_user_ticket.html", {"ataccount": ataccount, "PRIORITY": PRIORITY, "QUEUE_IDS": QUEUE_IDS, "STATUS": STATUS, "title": title, "description": description})
        else:
            new_ticket = ticket_create_new(True,
                AccountID = account_id,
                Title = request.POST['title'],
                Description = request.POST['description'],
                DueDateTime = request.POST['duedatetime'],
                EstimatedHours = request.POST['estimatedhours'],
                Priority = request.POST['priority'],
                Status = request.POST['status'],
                QueueID = request.POST['queueid'],
            )
            messages.add_message(request, messages.SUCCESS, ('Ticket - ' + new_ticket.TicketNumber + ' - ' + new_ticket.Title + ' created.'))
    return render(request, 'create_home_user_ticket.html', {"ataccount": ataccount, "PRIORITY": PRIORITY, "QUEUE_IDS": QUEUE_IDS, "STATUS": STATUS, "title": title, "description": description})


############################################################
#
# All custom methods in here (NO VIEWS)
#
############################################################

def ataccount(request, id):
    account_id = id
    ataccount = get_account(account_id)
    tickets = get_tickets_for_account(account_id)
    ticket_account_name = resolve_account_name_from_id(account_id)
    ticket_info = get_ticket_info(tickets)
    return render(request, 'account.html', {"ataccount": ataccount, "tickets": tickets, "ticket_account_name": ticket_account_name, "ACCOUNT_TYPES": ACCOUNT_TYPES, "QUEUE_IDS": QUEUE_IDS, "TICKET_SOURCES": TICKET_SOURCES})


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

def get_opportunity_from_id(opportunity_id):
    tquery = atws.Query('Opportunity')
    tquery.WHERE('id',tquery.Equals,opportunity_id)
    opportunity = at.query(tquery).fetch_one()
    return opportunity


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

def autotask_login_function(request, username, password):
    try:
        global at
        at_username = username
        at_password = password
        profile = Profile.objects.get(user=request.user)
        profile.autotask_username = username
        profile.autotask_password = password
        profile.save()
        at = atws.connect(username=profile.autotask_username,password=profile.autotask_password)
        return at
    except NameError:
        messages.add_message(request, messages.ERROR, 'Something went wrong')
    except ValueError:
        messages.add_message(request, messages.ERROR, 'Autotask username/password incorrect')



def opportunity_create_new(**kwargs):
    # First we need to create a new opportunity
    new_opportunity = at.new('Opportunity')
    new_opportunity.AccountID = kwargs.get('AccountID', None)
    new_opportunity.Amount = kwargs.get('Amount', None)
    new_opportunity.Cost = kwargs.get('Cost', None)
    new_opportunity.CreateDate = kwargs.get('CreateDate', None)
    new_opportunity.OwnerResourceID = kwargs.get('OwnerResourceID', None)
    new_opportunity.Probability = kwargs.get('Probability', None)
    new_opportunity.ProjectedCloseDate = kwargs.get('ProjectedCloseDate', None)
    new_opportunity.Stage = kwargs.get('Stage', None)
    new_opportunity.Status = kwargs.get('Status', None)
    new_opportunity.Title = kwargs.get('Title', None)
    new_opportunity.UseQuoteTotals = kwargs.get('UseQuoteTotals', None)
    new_opportunity.LeadReferral = kwargs.get('LeadReferral', None)
    opportunity = at.create(new_opportunity).fetch_one()
    return opportunity

def ticket_create_new(validated, **kwargs):
    new_ticket = at.new('Ticket')
    new_ticket.AccountID = kwargs.get('AccountID', None)
    new_ticket.ContactID = kwargs.get('ContactID', None)
    new_ticket.Title = kwargs.get('Title', None)
    new_ticket.Description = kwargs.get('Description', None)
    new_ticket.DueDateTime = kwargs.get('DueDateTime', None)
    new_ticket.EstimatedHours = kwargs.get('EstimatedHours', None)
    new_ticket.Priority = kwargs.get('Priority', None)
    new_ticket.Status = kwargs.get('Status', None)
    new_ticket.QueueID = kwargs.get('QueueID', None)
    new_ticket.OpportunityId = kwargs.get('OpportunityId', None)
    ticket = at.create(new_ticket).fetch_one()
    return ticket

def account_create_new(validated, **kwargs):
    new_account = at.new('Account')
    new_account.AccountName = kwargs.get('AccountName', None)
    new_account.Address1 = kwargs.get('Address1', None)
    new_account.Address2 = kwargs.get('Address2', None)
    new_account.City = kwargs.get('City', None)
    new_account.PostalCode = kwargs.get('PostalCode', None)
    new_account.Phone = kwargs.get('Phone', None)
    new_account.AccountType = kwargs.get('AccountType', None)
    new_account.OwnerResourceID = 29683570
    ataccount = at.create(new_account).fetch_one()
    return ataccount

def account_update(ataccount, **kwargs):
    ataccount.AccountName = kwargs.get('AccountName', None)
    ataccount.Address1 = kwargs.get('Address1', None)
    ataccount.Address2 = kwargs.get('Address2', None)
    ataccount.State = kwargs.get('State', None)
    ataccount.City = kwargs.get('City', None)
    ataccount.PostalCode = kwargs.get('PostalCode', None)
    ataccount.Phone = kwargs.get('Phone', None)
    ataccount.update()

def contact_create_new(validated, **kwargs):
    new_contact = at.new('Contact')
    new_contact.FirstName = kwargs.get('FirstName', None)
    new_contact.LastName = kwargs.get('LastName', None)
    new_contact.EMailAddress = kwargs.get('EMailAddress', None)
    new_contact.AddressLine = kwargs.get('AddressLine', None)
    new_contact.AddressLine1 = kwargs.get('AddressLine1', None)
    new_contact.City = kwargs.get('City', None)
    new_contact.ZipCode = kwargs.get('ZipCode', None)
    new_contact.Phone = kwargs.get('Phone', None)
    new_contact.AccountID = kwargs.get('AccountID', None)
    new_contact.Active = 1
    contact = at.create(new_contact).fetch_one()
    return contact

def quote_create_new(account, opportunity, expirydate, name, **kwargs):
    # First we must create a quote location
    new_quote_location = at.new('QuoteLocation')
    new_quote_location.Address1 = account.Address1
    try:
        new_quote_location.Address2 = account.Address2
    except AttributeError:
        new_quote_location.Address2 = ''
    new_quote_location.City = account.City
    new_quote_location.PostalCode = account.PostalCode
    quote_location = at.create(new_quote_location).fetch_one()
    # Then we need to create a quote
    new_quote = at.new('Quote')
    new_quote.AccountID = account.id
    new_quote.BillToLocationID = quote_location.id
    # Need to grab a contact to extract the id
    contact = get_contact_for_account(account.id)
    new_quote.ContactID = contact.id
    new_quote.EffectiveDate = time.strftime("%d.%m.%Y")
    new_quote.ExpirationDate = expirydate
    new_quote.Name = name
    new_quote.OpportunityID = opportunity.id
    new_quote.ShipToLocationID = quote_location.id
    new_quote.SoldToLocationID = quote_location.id
    quote = at.create(new_quote).fetch_one()
    return quote

def quote_item_create_new(quote, **kwargs):
    new_quote_item = at.new('QuoteItem')
    new_quote_item.IsOptional = kwargs.get('IsOptional', None)
    new_quote_item.LineDiscount = kwargs.get('LineDiscount', None)
    new_quote_item.PercentageDiscount = kwargs.get('PercentageDiscount', None)
    new_quote_item.Quantity = kwargs.get('Quantity', None)
    new_quote_item.QuoteID = quote.id
    new_quote_item.ProductID = kwargs.get('ProductID', None)
    new_quote_item.PeriodType = kwargs.get('PeriodType', None)
    new_quote_item.Type = kwargs.get('Type', None)
    new_quote_item.UnitDiscount = kwargs.get('UnitDiscount', None)
    new_quote_item.Name = kwargs.get('Name', None)
    new_quote_item.Description = kwargs.get('Description', None)
    new_quote_item.UnitCost = kwargs.get('UnitCost', None)
    new_quote_item.UnitPrice = kwargs.get('UnitPrice', None)
    quote_item = at.create(new_quote_item).fetch_one()
    return quote_item


def ticket_cost_item_create_new(ticket, **kwargs):
    new_ticket_cost = at.new('TicketCost')
    new_ticket_cost.AllocationCodeID = kwargs.get('AllocationCodeID', None)
    new_ticket_cost.Name = kwargs.get('Name', None)
    new_ticket_cost.CostType = kwargs.get('CostType', None)
    new_ticket_cost.DatePurchased = kwargs.get('DatePurchased', None)
    new_ticket_cost.TicketID = ticket.id
    new_ticket_cost.UnitQuantity = kwargs.get('UnitQuantity', None)
    ticket_cost = at.create(new_ticket_cost).fetch_one()
    return ticket_cost

def upsell_create_new(profile, sold, account_id, product_id, cost, **kwargs):
    # Now save info to DB
    for key, value in sold.items():
        Upsell.objects.create(profile=profile,
                              product_name=key,
                              account_id=account_id,
                              product_id=product_id,
                              product_cost=cost,
                              product_price=value,)


############################################################
#
# This is for the picklist module
#
############################################################

def create_picklist(request):
    string = "create_picklist_module --username {} --password {} atvar-test.py".format(at_username, at_password)
    os.system(string)
    messages.add_message(request, messages.SUCCESS, 'Creating picklist...this can take a while depending on the size of your database.')
    return render(request, 'account/profile.html', {})


def create_picklist_database(request):
    file = open('atvar.py', 'r')
    for line in file.readlines():
        # Split the line by whitespace giving ['Account_TerritoryID_Local', '=', '29682778']
        line_array = line.split()
        # Set the key to array index 0
        db_key = line_array[0]
        # Now to build the atvar string and we must convert to int for conditions to work
        db_value = line_array[2]
        print(db_key + ": " + str(db_value))
        Picklist.objects.create(profile=request.user.profile, key=db_key, value=db_value)
    messages.add_message(request, messages.SUCCESS, 'Added all picklist entities to database')
    return render(request, 'account/profile.html', {})

def create_picklist_dict(dict_name, index, regex):
    file = open('atvar.py', 'r')
    for line in file.readlines():
        my_line = line
        if re.search(regex, line):
            line_array = line.split()
            # This splits the left side of the equasion into an array seperated by underscore
            dict_key_parse = line_array[0].split("_", 3)
            # Then we grab the specific array we want for key name
            dict_key = dict_key_parse[index] # we want 2
            # Now to build the atvar string and we must convert to int for conditions to work
            dict_value = int(line_array[2])
            dict_name[dict_key] = dict_value
    return dict_name


TICKET_SOURCES = {}
create_picklist_dict(TICKET_SOURCES, 2, '^Ticket_Source_')

QUEUE_IDS = {}
create_picklist_dict(QUEUE_IDS, 2, '^Ticket_QueueID_')

PRIORITY = {}
create_picklist_dict(PRIORITY, 2, '^Ticket_Priority_')

STATUS = {}
create_picklist_dict(STATUS, 2, '^Ticket_Status_')

ACCOUNT_TYPES = {}
create_picklist_dict(ACCOUNT_TYPES, 2, '^Account_AccountType_')

RESOURCE_ROLES = {
    "Engineer": 29682834,
    "Admin": 29683587,
    "Home User Engineer": 29683586,
    "Sales": 29683582,
}




############################################################
#
# This is for overriding default user signup behaviour
#
############################################################

class LoginView(account.views.LoginView):

    form_class = account.forms.LoginEmailForm


class SignupView(account.views.SignupView):

   form_class = autotask_web_app.forms.SignupForm
   #
   def after_signup(self, form):
       self.create_profile(form)
       super(SignupView, self).after_signup(form)

   def create_profile(self, form):
       profile = self.created_user.profile  # replace with your reverse one-to-one profile attribute
       profile.first_name = form.cleaned_data["first_name"]
       profile.last_name = form.cleaned_data["last_name"]
       profile.email = form.cleaned_data["email"]
       profile.save()

   def generate_username(self, form):
        # do something to generate a unique username (required by the
        # Django User model, unfortunately)
        username = form.cleaned_data['email']
        return username
