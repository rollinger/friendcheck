from django.conf import settings

# Configuration Data for PayPal Payments

if settings.DEBUG:
    PAYPAL_RECEIVER_EMAIL = 'philipp.rollinger-business02@gmail.com'
else:
    PAYPAL_RECEIVER_EMAIL = 'philipp.rollinger@gmail.com'



SUBSCRIPTION_PLANS_DETAILS = {
    'MONTHLY': {'price_usd':'11.11',
        'subscription_extention_days': 30,
        'item_name': "Friendcheck Monthly Plan",},
    'MONTHLY DISCOUNT': {'price_usd':'9.99',
        'subscription_extention_days': 30,
        'item_name': "Friendcheck Monthly Discount Plan",},
    'YEARLY': {'price_usd':'108.00',
        'subscription_extention_days': 365,
        'item_name': "Friendcheck Yearly Plan",},
}
