from django import forms
from .models import AmazonSettings

class AmazonSettingsForm(forms.ModelForm):
    """
    نموذج لتعديل إعدادات الاتصال بـ Amazon SP-API
    """
    aws_secret_key = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        label="AWS Secret Key"
    )
    lwa_client_secret = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        label="LWA Client Secret"
    )
    refresh_token = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        label="Refresh Token"
    )
    
    class Meta:
        model = AmazonSettings
        fields = [
            'aws_access_key', 
            'aws_secret_key', 
            'role_arn', 
            'lwa_client_id', 
            'lwa_client_secret', 
            'refresh_token'
        ]
        widgets = {
            'aws_access_key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'AKIAXXXXXXXXXXXXXXXX',
                'autocomplete': 'off'
            }),
            'aws_secret_key': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                'autocomplete': 'off'
            }, render_value=True),
            'role_arn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'arn:aws:iam::XXXXXXXXXXXX:role/SellerRole',
                'autocomplete': 'off'
            }),
            'lwa_client_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'amzn1.application-oa2-client.XXXXXXXXXXXXXXXXXXXXXXXX',
                'autocomplete': 'off'
            }),
            'lwa_client_secret': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
                'autocomplete': 'off'
            }, render_value=True),
            'refresh_token': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Atzr|IwEBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                'autocomplete': 'off'
            }, render_value=True),
        } 