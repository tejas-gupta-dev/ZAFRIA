# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Users, Offer, Product, CartItem
from django.contrib.auth.models import User
import json
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse



@csrf_exempt
def send_whatsapp_order(request):
    if request.method == "POST":
        data = json.loads(request.body)

        name = data.get("name")
        phone = data.get("phone")
        address = data.get("address")
        payment_mode = data.get("payment_mode")
        user_id = request.session.get("custom_user_id")

        if not user_id:
            return JsonResponse({"error": "User not logged in"}, status=400)

        user = Users.objects.get(pk=user_id)
        cart_items = CartItem.objects.filter(Users=user)

        total = 0
        cart_msg = ""
        for i, item in enumerate(cart_items, start=1):
            price = item.quantity * item.product.price
            total += price
            cart_msg += f"\nItem {i}: {item.product.description}\nSize: {item.selected_size}, Color: {item.selected_color}, Qty: {item.quantity}, Price: ₹{price}"

        final_message = f"""🛍️ *New Order Received*
👤 Name: {name}
📞 Phone: {phone}
🏠 Address: {address}
💳 Payment Mode: {payment_mode}

🛒 Order Details:{cart_msg}
📦 Total: ₹{total}
"""
        user_message = f"✅ Thank you {name}! Your order has been received. We’ll contact you soon!"
        upi_link = ""
        if payment_mode.lower() == "online payment":
            upi_id = settings.UPI_ID  # Replace with your actual UPI ID
            upi_link = (
                f"https://upi.me/pay?"
                f"pa={upi_id}&pn=zafria+Store&am={total}&cu=INR&tn=Order+Payment"
            )
            user_message += f"\n💳 Please pay using this UPI link:\n{upi_link}"
        
        # Send WhatsApp via Twilio
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Send to Admin (you)
        client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to="whatsapp:+918447698907",  # replace
            body=final_message
        )

        # Send Confirmation to User
        '''client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:+91{phone}",
            body=f"✅ Thank you {name}! Your order has been received. We’ll contact you soon!"
        )'''

        if upi_link:
            user_message += f"\n💳 Please pay using this UPI link:\n{upi_link}"
            if product.quantity >= item.quantity:
                product.quantity -= item.quantity
                product.save()

                # ✅ Delete product if quantity reaches 0
                if product.quantity == 0:
                    product.delete()
            else:
                return JsonResponse({"error": f"Not enough stock for {product.description}"}, status=400)


        client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:+91{phone}",
            body=user_message
        )
        return JsonResponse({"success": True})



def logout_user(request):
    logout(request)
    request.session.flush()
    return redirect('login')


def home(request):
    offers = Offer.objects.all().order_by('-created_at')
    offers_serialized = []
    for offer in offers:
        offers_serialized.append({
            'title': offer.title,
            'description': offer.description,
            'image_url': offer.image.url
        })

    return render(request, 'home.html', {
        'offers': offers,
        'user': request.user,
        'offers_json': json.dumps(offers_serialized),
        'admin_email': settings.ADMIN_E
    })

def remove_from_cart(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(CartItem, id=item_id)
        item.delete()
    return redirect('cart')  

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        selected_size = request.POST.get('size', '')
        selected_color = request.POST.get('color', '')

        # Get your custom user from session
        custom_user_id = request.session.get('custom_user_id')
        if not custom_user_id:
            return redirect('login')

        user = get_object_or_404(Users, pk=custom_user_id)

        CartItem.objects.create(
            Users=user,
            product=product,
            selected_size=selected_size,
            selected_color=selected_color
        )
        return redirect('cart')

    

def upload_product(request):
    if request.method == 'POST':
        description = request.POST.get('description')
        pro_image = request.FILES.get('pro_image')
        price = request.POST.get('price')
        size = request.POST.get('size')
        color = request.POST.get('color')
        quantity = request.POST.get('quantity')
        if description and pro_image and price and size and color and quantity:
            Product.objects.create(
                description=description,
                pro_image=pro_image,
                price=price,
                size=size,
                quantity=quantity,
                color=color
            )
            return redirect('product')
            #Product.save()
        return redirect('home')
    return render(request, 'upload_pro.html')
    

def upload_offer(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if title and description and image:
            Offer.objects.create(
                title=title,
                description=description,
                image=image
            )
        return redirect('home')

    return render(request, 'upload_offer.html')


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        age = request.POST.get('age')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        password = request.POST.get('password')
        user = User.objects.create_user(username=email, email=email)
        user.set_password(password)
        user.save()
        custom_user = Users.objects.create(user=user, name=name, email=email, age=age, password=password, address=address, phone_number=phone_number)
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            request.session['custom_user_id'] = custom_user.id
        return redirect('home')
    return render(request, 'register.html')

'''
def logins(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not Users.objects.filter(email = email).exists():
            print("invalid")
            return redirect("login")
        
        user = authenticate(request, username=email, password=password)
        if user is None:
            print("invalid2")
            return redirect('login')
        else:
            login(request, user)
            print("success")
            return redirect('home')
    return render(request, 'login.html')
'''
def logins(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate using built-in User model
        user = authenticate(request, username=email, password=password)

        if user is None:
            print("Invalid login")  # wrong username or password
            return redirect('login')
        else:
            login(request, user)

            # Link to custom Users model if exists
            try:
                custom_user = Users.objects.get(user=user)
                request.session['custom_user_id'] = custom_user.id
            except Users.DoesNotExist:
                print("Custom user missing")
                return redirect('login')

            print("Login success")
            return redirect('home')
    
    return render(request, 'login.html')


'''def product(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'product.html', context)'''
def product(request):
    products = Product.objects.all()

    # Add size_list and color_list attributes to each product
    for product in products:
        product.size_list = product.size.split(',') if product.size else []
        product.color_list = product.color.split(',') if product.color else []

    context = {
        'products': products
    }
    return render(request, 'product.html', context)

def update_cart(request, item_id):
    return redirect('cart')
def cart(request):
    custom_user_id = request.session.get('custom_user_id')
    if not custom_user_id:
        return redirect('login')

    user = get_object_or_404(Users, pk=custom_user_id)
    cart_items = CartItem.objects.filter(Users=user)

    subtotal = 0
    for item in cart_items:
        item.total_price = item.quantity * item.product.price  # dynamically add total_price attribute
        subtotal += item.total_price

    delivery_charge = 50  # Flat charge (you can make dynamic later)
    total = subtotal + delivery_charge
    total_items = cart_items.count()

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_items': total_items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'total': total
    })
