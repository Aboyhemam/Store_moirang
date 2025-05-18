from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('category/<int:category_id>/', views.category_items, name='category_items'),
    path('search/', views.search, name='search'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('terms/', views.terms, name='terms'),
    path('cancelation/', views.cancel, name='cancel'),
    path('shipping/', views.shipping, name='shipping'),
    path('support/', views.support, name='support'),
    path('privacy/', views.privacy, name='privacy'),
    path('review/', views.customer_reviews, name='review'),
    path('account/settings/', views.account_settings, name='account_settings'),
    path('account/change-username/', views.change_username, name='change_username'),
    path('account/change-name/', views.change_name, name='change_name'),
    path('account/change-email/', views.change_email, name='change_email'),
    path('account/change-phone/', views.change_phone, name='change_phone'),
    path('account/change-address/', views.change_address, name='change_address'),
    path('account/change-password/', views.change_password, name='change_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.send_otp_view, name='send_otp'),
    path('checkout-selected/', views.checkout_selected, name='checkout_selected'),




    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
