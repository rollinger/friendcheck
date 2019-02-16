from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from decimal import Decimal

from . paypal_conf import PAYPAL_RECEIVER_EMAIL, SUBSCRIPTION_PLANS_DETAILS
from friendcheck.users.models import User, Booking

def paypal_ipn_transaction_callback(sender, **kwargs):
    # https://django-paypal.readthedocs.io/en/stable/standard/ipn.html
    ipn_obj = sender

    #payment_is_valid = False
    print('DEBUG')
    print(ipn_obj.invoice)
    print(ipn_obj.payment_status)
    print(ipn_obj.receiver_email)
    print(ipn_obj.custom)
    print(ipn_obj.mc_gross)
    print(ipn_obj.mc_currency)
    print(ipn_obj)

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != PAYPAL_RECEIVER_EMAIL:
            # Not a valid payment
            return

        # Undertake some action depending upon `ipn_obj`.
        # CHECK IF NO FORM TAMPERING OCCURRED
        if ipn_obj.custom == "monthly_plan":
            # Set target values for the ipn_obj
            price = SUBSCRIPTION_PLANS_DETAILS['MONTHLY']['price_usd']
            subscription_extention_days = SUBSCRIPTION_PLANS_DETAILS['MONTHLY']['subscription_extention_days']
        else:
            # Not a valid payment
            return

        if ipn_obj.mc_gross == Decimal( price ) and ipn_obj.mc_currency == 'USD':
            # if ipn_obj matches target value (mc_gross comes in Decimal type):
            # Extend subscription of user
            # => Get user object and call extend_subscription with the days to extend
            try:
                # Get user from invoice (TODO: Better way?)
                user_pk_from_invoice = int( ipn_obj.invoice.split('-')[1] )
                user = User.objects.get(pk=user_pk_from_invoice)
                # Extend Subscription
                user.extend_subscription(subscription_extention_days)
            except:
                # Subscription Extention was not possible
                return

        else:
            # Not a valid payment
            return

    else:
        # Not a valid payment
        return

valid_ipn_received.connect(paypal_ipn_transaction_callback)
