from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Cart, CartItem, FAQ, Review, PasswordResetOTP, Order
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomLoginForm, ReviewForm, ChangeAddressForm, ChangeEmailForm, ChangeNameForm, ChangePhoneForm, ChangeUsernameForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, get_user_model
from .forms import EmailForm, OTPVerificationForm
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import random
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from razorpay import Client, Utility
import json

User = get_user_model()

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'products': products, 'categories': categories})

def about(request):
    categories = Category.objects.all()
    return render(request, 'store/about.html', {'categories': categories})

def terms(request):
    categories = Category.objects.all()
    return render(request, 'store/terms.html', {'categories': categories})

def cancel(request):
    categories = Category.objects.all()
    return render(request, 'store/cancelation_refund.html', {'categories': categories})

def shipping(request):
    categories = Category.objects.all()
    return render(request, 'store/shipping.html', {'categories': categories})


def support(request):
    categories = Category.objects.all()
    faqs = FAQ.objects.all().order_by('created_at')
    context = {
        'faqs': faqs,
        'support_phone': '9362843841',
        'support_email': 'storemoirang@gmail.com',
        'categories' : categories
    }
    return render(request, 'store/support.html', context)

def privacy(request):
    categories = Category.objects.all()
    return render(request, 'store/privacy.html', {'categories': categories})

def contact(request):
    categories = Category.objects.all()
    return render(request, 'store/contact.html', {'categories': categories})

@login_required
def account_settings(request):
    categories = Category.objects.all()
    return render(request, 'store/account_settings.html', {'categories': categories})

def category_items(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'products': products, 'categories': categories})

def search(request):
    query = request.GET.get('q')
    products = Product.objects.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'products': products, 'categories': categories})

def register_view(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'store/register.html', {'form': form, 'categories':categories})

def login_view(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = CustomLoginForm()
    return render(request, 'store/login.html', {'form': form, 'categories':categories})

def logout_view(request):
    logout(request)
    return redirect('home')


def product_detail(request, product_id):
    categories = Category.objects.all()
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product, 'categories':categories})

@login_required
def add_to_cart(request, product_id):
    categories = Category.objects.all()
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Get or create cart for user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get or create item
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()

    return redirect('product_detail', product_id=product.id)

def some_view(request):
    categories = Category.objects.all()
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.items.count()

    return render(request, 'store/your_template.html', {
        'cart_count': cart_count,
        'categories':categories
        # other context variables
    })

@login_required
def cart(request):
    categories = Category.objects.all()
    cart = Cart.objects.prefetch_related('items__product').filter(user=request.user).first()
    total = sum(item.product.price * item.quantity for item in cart.items.all()) if cart else 0
    return render(request, 'store/cart.html', {'cart': cart, 'total': total, 'categories':categories})

@login_required
def update_cart_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "increase" and item.product.quantity > item.quantity:
            item.quantity += 1
            item.save()
        elif action == "decrease" and item.quantity > 1:
            item.quantity -= 1
            item.save()

    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart')

@login_required
def checkout_selected(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_items')
        if not selected_ids:
            messages.error(request, "Please select at least one item to checkout.")
            return redirect('cart')

        selected_items = CartItem.objects.filter(id__in=selected_ids, cart__user=request.user)
        # Save selected items to session or pass them as context
        request.session['selected_item_ids'] = selected_ids
        return redirect('checkout')


def customer_reviews(request):
    categories = Category.objects.all()
    reviews = Review.objects.order_by('-created_at')  # Newest first

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.save()
                return redirect('customer_reviews')
        else:
            return redirect('login')
    else:
        form = ReviewForm()

    return render(request, 'store/review.html', {
        'reviews': reviews,
        'form': form,
        'categories':categories,
    })
    
@login_required
def change_username(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Username updated successfully.')
            return redirect('account_settings')
    else:
        form = ChangeUsernameForm(instance=request.user)
    return render(request, 'store/ch_username.html', {'form': form, 'title': 'Change Username', 'categories':categories})

@login_required
def change_name(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = ChangeNameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Name updated successfully.')
            return redirect('account_settings')
    else:
        form = ChangeNameForm(instance=request.user)
    return render(request, 'store/ch_name.html', {'form': form, 'title': 'Change Name', 'categories':categories})

@login_required
def change_email(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Email updated successfully.')
            return redirect('account_settings')
    else:
        form = ChangeEmailForm(instance=request.user)
    return render(request, 'store/ch_email.html', {'form': form, 'title': 'Change Email', 'categories':categories})

@login_required
def change_phone(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = ChangePhoneForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Phone number updated successfully.')
            return redirect('account_settings')
    else:
        form = ChangePhoneForm(instance=request.user)
    return render(request, 'store/ch_phone.html', {'form': form, 'title': 'Change Phone Number', 'categories':categories})

@login_required
def change_address(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = ChangeAddressForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('account_settings')
    else:
        form = ChangeAddressForm(instance=request.user)
    return render(request, 'store/ch_address.html', {'form': form, 'title': 'Change Address', 'categories':categories})

@login_required
def change_password(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in
            return redirect('account_settings')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'store/ch_password.html', {'form': form, 'categories':categories})

def send_otp_email(email, otp):
    send_mail(
        'Your OTP for Password Reset',
        f'Your OTP is {otp}. It will expire in 10 minutes.',
        'storemoirang@example.com',
        [email],
        fail_silently=False,
    )

def send_otp_view(request):
    now = timezone.now()
    last_sent = request.session.get('otp_last_sent')

    # Throttle OTP sending (30 seconds)
    if last_sent:
        last_sent_time = timezone.datetime.fromisoformat(last_sent)
        if now < last_sent_time + timedelta(seconds=30):
            wait_time = (last_sent_time + timedelta(seconds=30) - now).seconds
            messages.warning(request, f"Please wait {wait_time} seconds before resending OTP.")
            return redirect('verify_otp')

    # Get user from session
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, "Session expired. Try again.")
        return redirect('forgot_password')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('forgot_password')

    # Generate and send new OTP
    otp = str(random.randint(100000, 999999))
    PasswordResetOTP.objects.create(user=user, otp=otp)
    send_otp_email(user.email, otp)

    # Save to session
    request.session['otp'] = otp
    request.session['otp_last_sent'] = now.isoformat()

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('verify_otp')


def forgot_password(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                otp = str(random.randint(100000, 999999))
                PasswordResetOTP.objects.create(user=user, otp=otp)
                send_otp_email(email, otp)
                request.session['reset_user_id'] = user.id
                request.session['otp_last_sent'] = timezone.now().isoformat()  # ✅ move here
                messages.success(request, 'OTP sent to your email.')
                return redirect('verify_otp')
            except User.DoesNotExist:
                form.add_error('email', 'No account with this email.')
    else:
        form = EmailForm()

    return render(request, 'store/forgot_password.html', {'form': form, 'categories':categories})


def verify_otp(request):
    categories = Category.objects.all()
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('forgot_password')
    
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            try:
                otp_record = PasswordResetOTP.objects.filter(user=user, otp=otp).latest('created_at')
                if otp_record.is_expired():
                    messages.error(request, 'OTP has expired.')
                else:
                    user.set_password(form.cleaned_data['new_password'])
                    user.save()
                    otp_record.delete()
                    messages.success(request, 'Password changed successfully.')
                    return redirect('login')
            except PasswordResetOTP.DoesNotExist:
                messages.error(request, 'Invalid OTP.')
    else:
        form = OTPVerificationForm()
    return render(request, 'store/verify_otp.html', {'form': form, 'categories':categories})

@login_required
def checkout(request):
    user = request.user

    selected_ids = request.session.get('selected_item_ids', [])
    cart_items = CartItem.objects.filter(id__in=selected_ids, cart__user=user)

    if not cart_items:
        messages.error(request, "No items found for checkout.")
        return redirect('cart')

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    product_details = ', '.join([f"{item.product.name} x{item.quantity}" for item in cart_items])

    # 🟢 Always create Razorpay order and local order when page loads (GET)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create({
        "amount": int(total_price * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    order = Order.objects.create(
        user=user,
        name=user.first_name,
        phone=user.phone_number,
        email=user.email,
        address=user.address,
        product_details=product_details,
        amount=total_price,
        razorpay_order_id=razorpay_order['id'],
        paid=False
    )

    context = {
        'user': user,
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'razorpay_order': razorpay_order,  # full dict, not just ID
        'order_id': order.id,
        'payment_ready': True,
        'order': order,
    }
    return render(request, 'store/checkout.html', context)

    
    
@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        data = json.loads(request.body)
        order_id = data.get("order_id")

        try:
            order = Order.objects.get(id=order_id)
            order.razorpay_payment_id = data.get("razorpay_payment_id")
            order.razorpay_signature = data.get("razorpay_signature")
            order.paid = True
            order.save()

            # ✅ Save order ID to session for the success page
            request.session['paid_order_id'] = order.id

            # ✅ Delete only the cart items that were paid (stored in session)
            selected_cart_ids = request.session.get('selected_cart_items', [])
            if selected_cart_ids:
                Cart.objects.filter(id__in=selected_cart_ids, user=order.user).delete()
                # Clear it after deletion
                del request.session['selected_cart_items']

            return JsonResponse({"status": "success"})

        except Order.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Order not found."}, status=404)

    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

@login_required
def payment_success_page(request):
    order_id = request.session.get('paid_order_id')
    if not order_id:
        return redirect('home')  # fallback if session missing
    try:
        order = Order.objects.get(id=order_id)
        return render(request, "store/payment_success.html", {"order": order})
    except Order.DoesNotExist:
        return redirect('home')

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': orders})