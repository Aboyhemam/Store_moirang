from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Cart, CartItem, FAQ, Review, PasswordResetOTP
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
import random



User = get_user_model()

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'store\home.html', {'products': products, 'categories': categories})

def about(request):
    return render(request, 'store/about.html')

def terms(request):
    return render(request, 'store/terms.html')

def cancel(request):
    return render(request, 'store/cancelation_refund.html')

def shipping(request):
    return render(request, 'store/shipping.html')


def support(request):
    faqs = FAQ.objects.all().order_by('created_at')
    context = {
        'faqs': faqs,
        'support_phone': '9362843841',
        'support_email': 'storemoirang@gmail.com'
    }
    return render(request, 'store/support.html', context)

def privacy(request):
    return render(request, 'store/privacy.html')

def contact(request):
    return render(request, 'store/contact.html')

@login_required
def account_settings(request):
    return render(request, 'store/account_settings.html')

def category_items(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, 'store\home.html', {'products': products, 'categories': categories})

def search(request):
    query = request.GET.get('q')
    products = Product.objects.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
    categories = Category.objects.all()
    return render(request, 'store\home.html', {'products': products, 'categories': categories})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'store/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = CustomLoginForm()
    return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
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
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.items.count()

    return render(request, 'store/your_template.html', {
        'cart_count': cart_count,
        # other context variables
    })

@login_required
def cart(request):
    cart = Cart.objects.prefetch_related('items__product').filter(user=request.user).first()
    total = sum(item.product.price * item.quantity for item in cart.items.all()) if cart else 0
    return render(request, 'store/cart.html', {'cart': cart, 'total': total})

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
        'form': form
    })
    
@login_required
def change_username(request):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Username updated successfully.')
            return redirect('account_settings')
    else:
        form = ChangeUsernameForm(instance=request.user)
    return render(request, 'store/ch_username.html', {'form': form, 'title': 'Change Username'})

@login_required
def change_name(request):
    if request.method == 'POST':
        form = ChangeNameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Name updated successfully.')
            return redirect('account_settings')
    else:
        form = ChangeNameForm(instance=request.user)
    return render(request, 'store/ch_name.html', {'form': form, 'title': 'Change Name'})

@login_required
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Email updated successfully.')
            return redirect('account_settings')
    else:
        form = ChangeEmailForm(instance=request.user)
    return render(request, 'store/ch_email.html', {'form': form, 'title': 'Change Email'})

@login_required
def change_phone(request):
    if request.method == 'POST':
        form = ChangePhoneForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Phone number updated successfully.')
            return redirect('account_settings')
    else:
        form = ChangePhoneForm(instance=request.user)
    return render(request, 'store/ch_phone.html', {'form': form, 'title': 'Change Phone Number'})

@login_required
def change_address(request):
    if request.method == 'POST':
        form = ChangeAddressForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('account_settings')
    else:
        form = ChangeAddressForm(instance=request.user)
    return render(request, 'store/ch_address.html', {'form': form, 'title': 'Change Address'})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in
            return redirect('account_settings')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'store/ch_password.html', {'form': form})

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

    return render(request, 'store/forgot_password.html', {'form': form})


def verify_otp(request):
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
    return render(request, 'store/verify_otp.html', {'form': form})