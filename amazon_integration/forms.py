from django import forms
from .models import AmazonSettings, AppSettings

class AmazonSettingsForm(forms.ModelForm):
    """
    نموذج لإدارة إعدادات الاتصال بـ Amazon SP-API
    """
    refresh_token = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        label="Refresh Token"
    )
    
    class Meta:
        model = AmazonSettings
        fields = [
            'refresh_token',
            'marketplace_id',
            'location_id',
            'is_active'
        ]
        widgets = {
            'refresh_token': forms.PasswordInput(attrs={
                'class': 'form-control ltr-input',
                'placeholder': 'Atzr|IwEBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
                'autocomplete': 'off'
            }, render_value=True),
            'marketplace_id': forms.Select(attrs={
                'class': 'form-select ltr-input',
                'autocomplete': 'off'
            }),
            'location_id': forms.TextInput(attrs={
                'class': 'form-control ltr-input',
                'placeholder': 'أدخل رقم موقع FBM المقدم من أمازون'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

class AppSettingsForm(forms.ModelForm):
    """
    نموذج لإدارة إعدادات التطبيق الثابتة
    """
    class Meta:
        model = AppSettings
        fields = ['aws_access_key', 'aws_secret_key', 'role_arn', 'lwa_client_id', 'lwa_client_secret', 'is_active']
        widgets = {
            'aws_access_key': forms.TextInput(attrs={'class': 'form-control ltr-input', 'placeholder': 'AKIAXXXXXXXXXXXXXXXX'}),
            'aws_secret_key': forms.PasswordInput(attrs={'class': 'form-control ltr-input', 'placeholder': 'Secret Key'}, render_value=True),
            'role_arn': forms.TextInput(attrs={'class': 'form-control ltr-input', 'placeholder': 'arn:aws:iam::XXXXXXXXXXXX:role/SellerRole'}),
            'lwa_client_id': forms.TextInput(attrs={'class': 'form-control ltr-input', 'placeholder': 'amzn1.application-oa2-client.XXXXXXXXXXXXXXXX'}),
            'lwa_client_secret': forms.PasswordInput(attrs={'class': 'form-control ltr-input', 'placeholder': 'Client Secret'}, render_value=True),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 