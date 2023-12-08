from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem, Checkout,UserProfile, Cart, Checkout, Order
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .models import UserProfile, Cart, Checkout, Order
from .forms import CheckoutForm
import stripe
from django.contrib import messages

# Create your views here.
stripe.api_key = 'sk_test_51OL1aHSDPAgcGpuwymCvJsVcnz25PydH7vTEqdS58hK4iOyfRDJIcKsuCl7RkzVK0JiNmZjfKqY9jTYzZ669HBom00Hn1SYQH9'


def product_list(request):
    products = Product.objects.all()
    return render(request, 'ecommerceapp/products_list.html', {'products' : products})

def view_cart(request):
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = user_cart.cartitem_set.all()

    for cart_item in cart_items:
        cart_item.subtotal = cart_item.product.price * cart_item.quantity
        cart_item.save()

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'ecommerceapp/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('product_list')


def remove_from_cart(request, product_id):
    cart_item = CartItem.objects.get(
        product__id=product_id,
        cart__user=request.user
    )

    cart_item.quantity -= 1

    if cart_item.quantity == 0:
        cart_item.delete()
    else:
        cart_item.save()

    return redirect('view_cart')

def add_item(request, product_id):
    cart_item = CartItem.objects.get(
      product_id=product_id,
      cart__user=request.user
    )

    cart_item.quantity += 1
    cart_item.save()

    return redirect('view_cart')

@login_required
def checkout(request):
    # Retrieve or create UserProfile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Retrieve or create Cart
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    total_price = sum(cart_item.subtotal() for cart_item in user_cart.cartitem_set.all())

    # Check if the user has a UserProfile and create one if not
    if not user_profile:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            shipping_address = form.cleaned_data['shipping_address']
            payment_method = form.cleaned_data['payment_method']

            # Create Order
            order = Order.objects.create(user_profile=user_profile, total_price=total_price)

            # Create Checkout
            checkout = Checkout.objects.create(
                user_profile=user_profile,
                cart=user_cart,
                order=order,
                shipping_address=shipping_address,
                payment_method=payment_method,
                # Add other fields as needed
            )

            try:
                # Create a PaymentIntent with Stripe
                intent = stripe.PaymentIntent.create(
                    amount=int(total_price * 100),  # Convert to cents
                    currency='usd',
                )

                # Update the Order with the PaymentIntent ID
                order.payment_intent_id = intent.id
                order.save()

                # Clear Cart items
                user_cart.items.clear()

                # Update Order status
                order.status = 'Completed'
                order.save()

                return render(request, 'ecommerceapp/checkout_success.html', {'order': order})
            except stripe.error.CardError as e:
                messages.error(request, f"Error processing payment: {e.error.message}")
        else:
            messages.error(request, "Invalid form submission. Please check your input.")
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'total_price': total_price,
        'user_cart': user_cart,
        'cart_items': user_cart.cartitem_set.all(),
        'stripe_publishable_key': 'pk_test_51OL1aHSDPAgcGpuwQZALYVbjzRHtN6dmB6F0h3lmgpStE0XF1DlseBiTGoBBhLjq5bDMQ3QurChZLuxyzb4xi3QE00aKN8YUvu',  # Replace with your actual publishable key
    }

    return render(request, 'ecommerceapp/checkout.html', context)
