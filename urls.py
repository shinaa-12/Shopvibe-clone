from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "app1"

urlpatterns = [
    path("", auth_views.LoginView.as_view(template_name="app1/login.html"), name="login"),
    path("home/", views.home, name="home"),
    path("checkout/", views.checkout, name="checkout"),
    path('signup/', views.signup, name='signup'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path("customers/", views.customer_list, name="customer_list"),
    # path("products/", views.products, name="products"),
    path("product/<int:pk>/edit/", views.edit_product, name="edit_product"),
    path("shop/", views.shop, name="shop"),
    path('logout/', views.logout_view, name='logout'),
    path('delete-order/<int:order_id>/', views.delete_order, name='delete_order'),
    path("cart/", views.cart_page, name="cart_page"),



]


