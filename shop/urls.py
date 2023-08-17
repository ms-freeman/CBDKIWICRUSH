from django.urls import path, include
from shop.views import index, detail,add_to_cart, view_cart, remove_from_cart, user_login,logOut,register,activate,contact

urlpatterns = [
    path('', index, name='Home'),
    path('<int:myid>/', detail, name='Detail'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='cart'),
    path('remove_from_cart/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('register', register, name='register'),
    path('login',user_login,name ='user_login'),
    path('logout',logOut,name='logout'),
    path('activate/<uidb64>/<token>',activate,name='activate'),
    path('contact/',contact, name='contact'),
]
