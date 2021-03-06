import json

from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect, reverse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

import stripe

from bag.contexts import bag_contents
from products.models import Product
from profiles.models import UserProfile

from .forms import OrderForm
from .models import Order, OrderLineItem


@require_POST
def cache_checkout_data(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        pid = data.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': data.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as error:
        messages.error(request, error)
        print(error)
        return HttpResponse(content=error, status=400)


def checkout(request):
    """Return checkout template and handle checkout logic"""

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        bag = request.session.get('bag', {})

        if 'address' in request.POST:
            address = user_profile.addresses.get(
                id=request.POST.get('address'))
            form_data = {
                'full_name': request.POST['full_name'],
                'email': request.POST['email'],
                'phone_number': address.phone_number,
                'country': address.country,
                'postcode': address.postcode,
                'town_or_city': address.town_or_city,
                'street_address1': address.street_address1,
                'street_address2': address.street_address2,
                'county': address.county,
            }
        else:
            form_data = {
                'full_name': request.POST['full_name'],
                'email': request.POST['email'],
                'phone_number': request.POST['phone_number'],
                'country': request.POST['country'],
                'postcode': request.POST['postcode'],
                'town_or_city': request.POST['town_or_city'],
                'street_address1': request.POST['street_address1'],
                'street_address2': request.POST['street_address2'],
                'county': request.POST['county'],
            }

        order_form = OrderForm(form_data)

        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    order_line_item = OrderLineItem(
                        order=order,
                        product=product,
                        quantity=item_data,
                    )
                    order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(
                        request, ("One of the products in your bag could not be found. Please contact us for assistance!"))
                    order.delete()
                    return redirect(reverse('view_bag'))

            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request,
                           'There was an error with your form. Please double check your details')

    bag = request.session.get('bag', {})

    if not bag:
        if request.user.is_authenticated:
            messages.error(
                request, 'There are no items in your bag currently')
            return redirect(reverse('products'))
        else:
            messages.error(request, 'Please log in to proceed to checkout')
            return redirect(reverse('products'))

    current_bag = bag_contents(request)
    total = current_bag['total']
    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
        automatic_payment_methods={'enabled': True},
    )

    order_form = OrderForm()
    addresses = user_profile.addresses.all()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing.')

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
        'addresses': addresses,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """Handle successful checkout"""

    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

    messages.success(request, 'Your order was successfully placed!')

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)
