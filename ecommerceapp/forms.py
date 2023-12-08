# ecommerceapp/forms.py

from django import forms


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(label='Shipping Address', max_length=255, widget=forms.Textarea)
    payment_method = forms.ChoiceField(
        label='Payment Method',
        choices=[
            ('credit_card', 'Credit Card'),
            ('paypal', 'PayPal'),
            # Add other payment methods as needed
        ]
    )
    # Add other fields as needed for your checkout process
