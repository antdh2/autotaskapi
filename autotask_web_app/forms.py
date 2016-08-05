from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _

import account.forms


class SignupForm(account.forms.SignupForm):

    first_name = forms.CharField(
        label=_("First Name"),
        max_length=30,
        widget=forms.TextInput(attrs={'class' : 'form-control'}),
        required=False
    )
    last_name = forms.CharField(
        label=_("Last Name"),
        max_length=30,
        widget=forms.TextInput(attrs={'class' : 'form-control'}),
        required=False
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(render_value=False, attrs={'class' : 'form-control'})
    )
    password_confirm = forms.CharField(
        label=_("Password (again)"),
        widget=forms.PasswordInput(render_value=False, attrs={'class' : 'form-control'})
    )



    # remove usernames
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        del self.fields["username"]
