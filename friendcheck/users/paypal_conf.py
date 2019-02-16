

# Configuration Data for PayPal Payments
#PAYPAL_RECEIVER_EMAIL = 'philipp.rollinger@gmail.com'
PAYPAL_RECEIVER_EMAIL = 'philipp.rollinger-business02@gmail.com'


SUBSCRIPTION_PLANS_DETAILS = {
    'MONTHLY': {'price_usd':'5.99',
        'subscription_extention_days': 30,
        'item_name': "Friendcheck Monthly Plan",},
    'MONTHLY DISCOUNT': {'price_usd':'3.99',
        'subscription_extention_days': 30,
        'item_name': "Friendcheck Monthly Discount Plan",},
    'YEARLY': {'price_usd':'45.0',
        'subscription_extention_days': 365,
        'item_name': "Friendcheck Yearly Plan",},
}
