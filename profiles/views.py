from unittest import case
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse

from checkout.models import Order
from products.models import Product
from products.forms import ProductForm, BookForm, BoxedSetForm, CollectibleForm

from .models import UserProfile, Address
from .forms import UserForm, AddressForm


@login_required
def profile(request):
    """Return the user profile template"""

    template = 'profiles/profile.html'

    return render(request, template)


def order_history(request):
    """Return the user' order history"""

    user_profile = get_object_or_404(UserProfile, user=request.user)
    orders = user_profile.orders.all().order_by('-date')

    template = 'profiles/order_history.html'
    context = {
        'orders': orders,
    }

    return render(request, template, context)


@login_required
def order_summary(request, order_number):
    """Return order summary of given order number"""

    order = get_object_or_404(Order, order_number=order_number)

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)


@login_required
def details(request):
    """Return user profile details"""

    user = get_object_or_404(get_user_model(), username=request.user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect(reverse('details'))
        else:
            messages.error(request,
                           ('Update failed. Please ensure '
                            'the form is valid.'))
    else:
        form = UserForm(instance=user)

    template = 'profiles/details.html'
    context = {
        'user': user,
        'form': form,
    }

    return render(request, template, context)


def delete_addresses(user_profile: UserProfile, delete_ids: list):
    for address_id in delete_ids:
        try:
            user_profile.addresses.get(id=address_id).delete()
        except Address.DoesNotExist:
            print(f'address {address_id} does not exist, delete failed')


def set_default_address(user_profile: UserProfile, address_id: int):
    try:
        address = user_profile.addresses.get(id=address_id)
        address.default = True
        address.save()
    except Address.DoesNotExist:
        print(f'address {address_id} does not exist, set as default failed')


@login_required
def address_book(request):
    """Return user's saved addresses"""

    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        if 'default' in request.POST:
            address_id = request.POST['default']
            set_default_address(user_profile, address_id)
            redirect(reverse('address_book'))
        if 'delete' in request.POST:
            delete_ids = request.POST.getlist('delete')
            delete_addresses(user_profile, delete_ids)
            messages.success(request, f'{len(delete_ids)} item(s) deleted')
            redirect(reverse('address_book'))

    addresses = user_profile.addresses.all()

    if len(addresses) == 0:
        default_address = None
        total = 0
    else:
        try:
            default_address = user_profile.addresses.get(default=True)
            addresses = user_profile.addresses.filter(default=False)
            # addresses not default + default address
            total = len(addresses) + 1
        except Address.DoesNotExist:
            default_address = None
            addresses = user_profile.addresses.filter(default=False)
            total = len(addresses)

    template = 'profiles/address_book.html'
    context = {
        'addresses': addresses,
        'default_address': default_address,
        'total': total,
    }

    return render(request, template, context)


@login_required
def add_address(request):
    """Return add address form and template"""

    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.profile = user_profile
            instance.save()
            messages.success(request, 'Address added successfully')
            return redirect(reverse('address_book'))
        else:
            messages.error(request,
                           ('Update failed. Please ensure '
                            'the form is valid.'))
    else:
        form = AddressForm()

    template = 'profiles/add_address.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_address(request, address_id):

    user_profile = get_object_or_404(UserProfile, user=request.user)
    address = user_profile.addresses.get(id=address_id)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully')
            return redirect(reverse('address_book'))
    else:
        form = AddressForm(instance=address)

    template = 'profiles/edit_address.html'
    context = {
        'form': form,
        'address_id': address_id,
    }

    return render(request, template, context)


@login_required
def saved(request):

    user_profile = get_object_or_404(UserProfile, user=request.user)
    saved_products = user_profile.saved.all()

    template = 'profiles/saved_products.html'
    context = {
        'saved_products': saved_products,
    }

    return render(request, template, context)


@login_required
def remove(request, product_id):
    """Remove product from saved list"""

    user_profile = get_object_or_404(UserProfile, user=request.user)
    product = get_object_or_404(Product, pk=product_id)
    redirect_url = request.POST.get('redirect_url')

    try:
        user_profile.saved.get(product=product).delete()
        messages.success(
            request, f'{product.name} removed from saved items')
    except Address.DoesNotExist:
        messages.error(request, 'Product is not saved')

    return redirect(redirect_url)


@login_required
def admin(request):
    """Return admin template for super users"""
    if not request.user.is_superuser:
        messages.error(request, 'Unauthorized access')
        return redirect(reverse('home'))

    products = Product.objects.all()

    template = 'profiles/admin.html'
    context = {
        'products': products
    }

    return render(request, template, context)


@login_required
def add_product(request, category_id):
    """Add a product to the store"""
    if not request.user.is_superuser:
        messages.error(request, 'Unauthorized access')
        return redirect(reverse('home'))

    if request.method == "POST":
        if category_id == 1:
            form = BookForm(request.POST, request.FILES)
        elif category_id == 2:
            form = BoxedSetForm(request.POST, request.FILES)
        elif category_id == 3:
            form = CollectibleForm(request.POST, request.FILES)
        else:
            form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)
            if instance.image:
                instance.image_url = instance.image.url
            instance.save()
            messages.success(request, 'Product added successfully')
            return redirect(reverse('admin'))
        else:
            messages.error(request,
                           ('Update failed. Please ensure '
                            'the form is valid.'))
    else:
        if category_id == 1:
            form = BookForm(request.POST, request.FILES)
        elif category_id == 2:
            form = BoxedSetForm(request.POST, request.FILES)
        elif category_id == 3:
            form = CollectibleForm(request.POST, request.FILES)
        else:
            form = ProductForm(request.POST, request.FILES)

    template = 'profiles/add_product.html'
    context = {
        'form': form,
        'category_id': category_id
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """Edit a product"""
    if not request.user.is_superuser:
        messages.error(request, 'Unauthorized access')
        return redirect(reverse('home'))

    product = Product.objects.get(id=product_id)

    if request.method == "POST":
        if product.category.id == 1:
            form = BookForm(request.POST, request.FILES, instance=product)
        elif product.category.id == 2:
            form = BoxedSetForm(request.POST, request.FILES, instance=product)
        elif product.category.id == 3:
            form = CollectibleForm(
                request.POST, request.FILES, instance=product)
        else:
            form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            instance = form.save(commit=False)
            if instance.image:
                instance.image_url = instance.image.url
            instance.save()
            messages.success(request, 'Product updated successfully')
            return redirect(reverse('admin'))
    else:
        if product.category.id == 1:
            form = BookForm(instance=product)
        elif product.category.id == 2:
            form = BoxedSetForm(instance=product)
        elif product.category.id == 3:
            form = CollectibleForm(instance=product)
        else:
            form = ProductForm(instance=product)

    template = 'profiles/edit_product.html'
    context = {
        'form': form,
        'product_id': product_id,
    }

    return render(request, template, context)


@login_required
@require_POST
def delete_product(request):
    """Delete a product from the store"""
    if not request.user.is_superuser:
        messages.error(request, 'Unauthorized access')
        return redirect(reverse('home'))

    product_ids = request.POST.getlist('delete')
    for pid in product_ids:
        Product.objects.get(id=pid).delete()
    messages.success(request, f'Deleted {len(product_ids)} item(s)')
    return redirect(reverse(admin))
