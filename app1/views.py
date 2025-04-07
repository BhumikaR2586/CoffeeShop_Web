from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Coffee, Cart

def home(request):
    app1 = Coffee.objects.all()
    return render(request, 'home.html', {'coffee': app1})

def add_to_cart(request, coffee_id):
    coffee = get_object_or_404(Coffee, id=coffee_id)

    # Check if the coffee is in stock
    if coffee.quantity <= 0:
        return HttpResponse("Sorry, this coffee is out of stock.")

    # Get or create the cart item
    cart_item, created = Cart.objects.get_or_create(coffee=coffee)

    # Check if adding the item exceeds the available stock
    if cart_item.quantity + 1 > coffee.quantity:
        return HttpResponse("Sorry, not enough stock available.")

    # Increment the cart item quantity by 1
    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1
    cart_item.save()

    # Reduce the stock of the coffee by 1
    coffee.quantity -= 1
    coffee.save()

    return redirect('home')

def view_cart(request):
    cart_items = Cart.objects.all()
    total = sum(item.coffee.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

def increment_quantity(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id)
    coffee = cart_item.coffee

    # Check if adding exceeds available stock
    if cart_item.quantity + 1 > coffee.quantity:
        return HttpResponse("Sorry, not enough stock available.")

    # Increment the cart item quantity
    cart_item.quantity += 1
    cart_item.save()

    # Reduce the stock of the coffee
    coffee.quantity -= 1
    coffee.save()

    return redirect('view_cart')

def decrement_quantity(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id)
    coffee = cart_item.coffee

    # Decrease quantity or remove item if quantity is 1
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        coffee.quantity += 1  # Restore stock
        cart_item.save()
        coffee.save()
    else:
        # Remove the cart item and restore stock
        coffee.quantity += cart_item.quantity
        coffee.save()
        cart_item.delete()

    return redirect('view_cart')

def view_cart(request):
    cart_items = Cart.objects.all()
    total = 0
    for item in cart_items:
        item.subtotal = item.coffee.price * item.quantity  # Calculate subtotal for each item
        total += item.subtotal  # Add to total

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})