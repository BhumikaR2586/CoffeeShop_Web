from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Coffee, Cart, Order
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth.decorators import login_required


def home(request):
    app1 = Coffee.objects.all()
    return render(request, 'home.html', {'coffee': app1})

def add_to_cart(request, coffee_id):
    if not request.user.is_authenticated:
        return redirect('login')  

    coffee = get_object_or_404(Coffee, id=coffee_id)

    # Check if the coffee is in stock
    if coffee.quantity <= 0:
        return HttpResponse("Sorry, this coffee is out of stock.")

    # Get or create the cart item for the logged-in user
    cart_item, created = Cart.objects.get_or_create(user=request.user, coffee=coffee)

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
    if not request.user.is_authenticated:
        return redirect('login')

    cart_items = Cart.objects.filter(user=request.user)
    total = 0

    for item in cart_items:
        item.subtotal = item.coffee.price * item.quantity
        total += item.subtotal

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})


def increment_quantity(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)  # Ensure the cart item belongs to the user
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
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)  # Ensure the cart item belongs to the user
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

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

def user_register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        address = request.POST['address']
        
        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                # Save the address to the UserProfile
                user_profile = UserProfile.objects.get(user=user)
                user_profile.address = address
                user_profile.save()
                messages.success(request, "Registration successful. Please log in.")
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'register.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def user_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'profile.html', {'user_profile': user_profile})

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items:
        messages.error(request, "Your cart is empty!")
        return redirect('home')

    total = sum(item.coffee.price * item.quantity for item in cart_items)

    # Create the order
    order = Order.objects.create(
        user=request.user,
        total=total,
        status='pending',
        address=request.user.userprofile.address  # Assuming address is in UserProfile
    )

    # Add cart items to the order (Many-to-Many relationship)
    order.cart_items.set(cart_items)

    # Create order_items data for the template (detailed bill)
    order_items = []
    for item in cart_items:
        order_items.append({
            'coffee': item.coffee,
            'quantity': item.quantity,
            'total_price': item.coffee.price * item.quantity
        })

    # Reduce coffee stock and delete cart items after the order is created
    for item in cart_items:
        item.coffee.quantity -= item.quantity
        item.coffee.save()

    cart_items.delete()

    return render(request, 'checkout_confirmation.html', {'order': order, 'order_items': order_items})

@login_required
def edit_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
        email = request.POST['email']
        address = request.POST['address']

        # Update fields
        request.user.email = email
        request.user.save()
        user_profile.address = address
        user_profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('profile')  # Go back to the profile page

    return render(request, 'edit_profile.html', {
        'user': request.user,
        'user_profile': user_profile
    })
