"""
Stripe BlouseBrothers Tools
"""
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

plans = stripe.Plan.list()
plan_id = [x for x in plans if x['nickname'] == "abo mensuel"][0]['id']
