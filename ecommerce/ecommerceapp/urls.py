from django.urls import path
from ecommerceapp import views


urlpatterns = [
    path('',views.index,name="index"),
    path('contact',views.contact,name="contact"),
    path('checkout/',views.checkout,name="checkout"),
    path('profile',views.profile,name="profile"),
    path('verify_payment/', views.verify_payment, name='verify_payment'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'), 
   
   

]
