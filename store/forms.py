from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django import forms

from store.models import Profile


class LoginForm(forms.Form):
    '''
    A form for user login.
    It includes fields for usernama and password.
    clean method checks if the username and password are valid.
    '''
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Username',
            'autocomplete': 'username',  # Add autocomplete for better UX
            'autofocus': True  # Automatically focus on username field
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
            'autocomplete': 'current-password'  # Add autocomplete for better UX
        })
    )

    remember_me = forms.BooleanField(  # Add remember me functionality
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError(
                    "Please enter a correct username and password. "
                    "Note that both fields may be case-sensitive."
                )
            self.user = user
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)


class UserInfoForm(forms.ModelForm):
    '''
    A form for updating user information.
    It includes fields for phone number, address, city, state, zipcode, and country.
    '''
    phone = forms.CharField(label="Phone Number", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'}), required=False)
    address1 = forms.CharField( label="Address", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Address Line 1'}), required=False)
    address2 = forms.CharField( label="Address", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Address Line 2'}), required=False)
    city = forms.CharField( label="City", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'City'}), required=False)
    state = forms.CharField( label="State", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'State'}), required=False)
    zipcode = forms.CharField( label="Zipcode", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Zip Code'}), required=False)
    country = forms.CharField( label="Country", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Country'}),required=False)

    class Meta:
        model = Profile
        fields = ['phone', 'address1', 'address2', 'city', 'state', 'zipcode', 'country']



class ChangePasswordForm(forms.Form):
    '''
    A form for changing the user's password.
    It includes fields for the current password, new password, and confirmation of the new password.
    clean methods check if the current password is correct and if the new passwords match.
    The save method updates the user's password in the database.
    '''
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg mb-3',
            'placeholder': 'Current Password',
            'autocomplete': 'current-password'
        }),
        label=''
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg mb-3',
            'placeholder': 'New Password',
            'autocomplete': 'new-password'
        }),
        label='',
        help_text='<ul class="form-text text-muted small mb-3">'
                  '<li>At least 8 characters long</li>'
                  '<li>Must contain at least one letter and one number</li>'
                  '<li>Cannot be too similar to your personal information</li>'
                  '<li>Cannot be a commonly used password</li>'
                  '</ul>'
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg mb-3',
            'placeholder': 'Confirm New Password',
            'autocomplete': 'new-password'
        }),
        label='',
        help_text='<span class="form-text text-muted small">Enter the same password as above, for verification.</span>'
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Your current password was entered incorrectly.')
        return current_password

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
            
        if password.isdigit():
            raise forms.ValidationError('Password cannot be entirely numeric.')
            
        if not any(char.isalpha() for char in password) or not any(char.isdigit() for char in password):
            raise forms.ValidationError('Password must contain both letters and numbers.')
            
        # Check for common passwords
        common_passwords = ['password123', '12345678', 'qwerty123']
        if password.lower() in common_passwords:
            raise forms.ValidationError('This password is too common.')
            
        # Check similarity to user information
        if self.user.username.lower() in password.lower():
            raise forms.ValidationError('Password is too similar to your username.')
            
        return password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('The two password fields didn\'t match.')
        return password2

    def save(self):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        self.user.save()
        return self.user


class UpdateUserForm(UserChangeForm):
    '''
    A form for updating user information.
    It includes fields for username, email, first name, and last name.
    The clean methods check if the username and email are unique.
    The save method updates the user's information in the database.
    '''
    password = None
    username = forms.CharField(
        max_length=150,
        label='User Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg mb-3',
            'placeholder': 'Username',
            'autocomplete': 'username'
        }),
        # help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg mb-3',
            'placeholder': 'Email Address'
        }),
        required=False
    )

    first_name = forms.CharField(
        label='First Name',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg mb-3',
            'placeholder': 'First Name'
        }),
        required=False
    )

    last_name = forms.CharField(
        label='Last Name',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg mb-3',
            'placeholder': 'Last Name'
        }),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for field in self.fields.values():
        #     field.label = ""  # Remove labels

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Check if username exists but exclude current user
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        # Check username format
        if not username.isalnum() and not set(username).issubset(set("@.+-_")):
            raise forms.ValidationError('Username may only contain letters, numbers, and @/./+/-/_')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('This email is already registered to another account.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class RegisterForm(forms.Form):
    '''
    A form for user registration.
    It includes fields for first name, last name, username, email, and password.
    The clean methods check if the username and email are unique, and if the password meets certain criteria.
    The save method creates a new user and a corresponding profile.
    '''
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'First Name',
            'autocomplete': 'given-name'
        }),
        required=False
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Last Name',
            'autocomplete': 'family-name'
        }),
        required=False
    )

    username = forms.CharField(
        min_length=3,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Username',
            'autocomplete': 'username'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Email Address',
            'autocomplete': 'email'
        })
    )

    password1 = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        })
    )


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered')
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        # Check if password is entirely numeric
        if password1.isdigit():
            raise forms.ValidationError('Password cannot be entirely numeric')

        # Check for common passwords (you can expand this list)
        common_passwords = ['password', '12345678', 'qwerty']
        if password1.lower() in common_passwords:
            raise forms.ValidationError('This password is too common')
        """
        --Restrict password--
        
        # Check for minimum length
        if len(password1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long')
        # Check for Uppercase and lowercase letters
        if not any(char.isupper() for char in password1) or not any(char.islower() for char in password1):
            raise forms.ValidationError('Password must contain both uppercase and lowercase letters')
        # Check for digits
        if not any(char.isdigit() for char in password1):
            raise forms.ValidationError('Password must contain at least one digit')
        # Check for special characters
        if not any(char in "!@#$%^&*()-_=+[]{}|;:',.<>?/" for char in password1):
            raise forms.ValidationError('Password must contain at least one special character')
            
        # Check for similarity to username
        if self.cleaned_data.get('username').lower() in password1.lower():
            raise forms.ValidationError('Password is too similar to your username')
        """

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Passwords do not match')
        return password2

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username', '')
        password1 = cleaned_data.get('password1', '')

        # Check if password is too similar to username
        if username and password1:
            if username.lower() in password1.lower():
                raise forms.ValidationError(
                    'Password is too similar to your username'
                )

        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )

        # Create user profile
        Profile.objects.create(user=user)

        return user