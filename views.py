from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import authenticate, login , logout
from .models import Product
from .models import Order, OrderItem
from collections import Counter
from decimal import Decimal
from django.http import Http404
from django.http import HttpResponseForbidden



def start(request):
    """Entry point for the site.
    If user is authenticated -> go to home, otherwise go to login page.
    """
    if request.user.is_authenticated:
        return redirect("app1:home")
    return redirect("app1:login")


@login_required(login_url='app1:login')
def home(request):
    featured_products = Product.objects.all()[:6]
    return render(request, "app1/home.html", {"featured_products": featured_products})


@login_required(login_url='app1:login')
def customer_list(request):
    users = User.objects.all()
    return render(request, "app1/customer_list.html", {"users": users})


# @login_required(login_url='app1:login')
# def products(request):
#     all_products = Product.objects.all()  # सर्व products fetch
#     context = {
#         'products': all_products
#     }
#     return render(request, 'app1/products.html', context)




@login_required(login_url='app1:login')
def shop(request):
    cart = request.session.get("cart", [])
    
    if request.method == "POST":
        action = request.POST.get("action")
        pid = request.POST.get("product_id")
        
        if action == "add" and pid:
            cart.append(int(pid))
            request.session["cart"] = cart
        elif action == "remove" and pid:
            if int(pid) in cart:
                cart.remove(int(pid))
                request.session["cart"] = cart
    
    products_qs = Product.objects.all()
    cart_products = Product.objects.filter(id__in=cart)
    total_price = sum((p.price for p in cart_products))
    
    return render(request, "app1/shop.html", {
        "products": products_qs,
        "cart_products": cart_products,
        "total_price": total_price,
        "cart_count": len(cart)
    })




# @login_required(login_url='app1:login')
# def cart_page(request):
#     cart = request.session.get("cart", [])
#     cart_products = Product.objects.filter(id__in=cart)
#     total_price = sum(p.price for p in cart_products)

#     return render(request, "app1/cart.html", {
#         "cart_products": cart_products,
#         "total_price": total_price,
#         "cart_count": len(cart)
#     })

@login_required(login_url='app1:login')
def cart_page(request):
    cart = request.session.get("cart", [])

    # Important: session cart ko int list me ensure karo
    cart = [int(i) for i in cart]

    cart_products = Product.objects.filter(id__in=cart)
    total_price = sum(p.price for p in cart_products)

    return render(request, "app1/cart.html", {
        "cart_products": cart_products,
        "total_price": total_price,
        "cart_count": len(cart)
    })



@login_required(login_url='app1:login')
def checkout(request):
    cart = request.session.get("cart", [])
    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect('app1:shop')

    # Count quantities
    counts = Counter(cart)
    products = Product.objects.filter(id__in=counts.keys())

    total = Decimal('0')
    for p in products:
        qty = counts.get(p.id, 0)
        total += p.price * qty

    # create order
    order = Order.objects.create(user=request.user, total=total)

    for p in products:
        qty = counts.get(p.id, 0)
        if qty <= 0:
            continue
        OrderItem.objects.create(order=order, product=p, price=p.price, quantity=qty)
        # reduce stock
        try:
            p.stock = max(0, p.stock - qty)
            p.save()
        except Exception:
            pass

    # clear cart
    request.session['cart'] = []

    return render(request, 'app1/order_confirmation.html', {'order': order})


@login_required(login_url='app1:login')
def orders(request):
    """List orders for the logged-in user."""
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'app1/orders.html', {'orders': user_orders})


@login_required(login_url='app1:login')
def order_detail(request, order_id):
    """Show single order details (only for owner)."""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        raise Http404("Order not found")
    return render(request, 'app1/order_detail.html', {'order': order})


@login_required(login_url='app1:login')
def edit_product(request, pk):
    """Allow staff users to edit a product from the site."""
    if not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to edit products.")

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')

        if name:
            product.name = name
        product.description = description
        try:
            product.price = price
        except Exception:
            pass
        try:
            product.stock = int(stock) if stock else product.stock
        except Exception:
            pass

        if image:
            product.image = image

        product.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('app1:products')

    return render(request, 'app1/edit_product.html', {'product': product})


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("app1:signup")
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("app1:signup.html")
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("app1:login")
    
    return render(request, "app1/signup.html")


@login_required(login_url='app1:login')
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("app1:login")


def delete_order(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order.delete()
        messages.success(request, f"Order #{order_id} deleted successfully!")
        return redirect('app1:orders')