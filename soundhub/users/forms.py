from django import forms
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class SignInForm(forms.Form):
    email = forms.EmailField(max_length=255, widget=forms.EmailInput(
        attrs={
            'class': 'signin-field',
            'placeholder': 'Email Address'
        }
    ))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'signin-field',
            'placeholder': 'Password'
        }
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        self.user = authenticate(
            email=email,
            password=password,
        )

        if not self.user:
            raise forms.ValidationError('Incorrect email address or password')
        else:
            setattr(self, 'login', self._login)

    def _login(self, request):
        login(request, self.user)


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'signup-field transition',
        'placeholder': 'Password',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'signup-field transition',
            'placeholder': 'Password Confirmation'
        }))

    class Meta:
        model = User
        fields = (
            'email',
            'nickname',
            'password1',
            'password2',
        )
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': 'signup-field transition',
                    'placeholder': 'E-mail Address',
                }
            ),
            'nickname': forms.TextInput(
                attrs={
                    'class': 'signup-field transition',
                    'placeholder': 'Nickname',
                }
            ),
        }
