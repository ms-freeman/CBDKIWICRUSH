from django.urls import path, include
from shop.views import index, detail,add_to_cart, view_cart, remove_from_cart, user_login,logOut,register,activate,contact,graines_cannabis_view,graines_feminisees_view,graines_autofloraison_view,breeding_grounds_view,produits_cbd_view,sensi_weeds_view,marchandises_view,vaporisateur_view,adjust_cart_quantity

urlpatterns = [
    path('', index, name='Home'),
    
    path('<int:myid>/', detail, name='detail'),
    
    
    
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='cart'),
    path('remove_from_cart/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    
    
    path('register', register, name='register'),
    path('login',user_login,name ='user_login'),
    path('logout',logOut,name='logout'),
    path('activate/<uidb64>/<token>',activate,name='activate'),
    
    
    path('contact/',contact, name='contact'),
    
    
    
    path('graines-de-cannabis/',graines_cannabis_view , name='graines_cannabis_view'),
    path('graines-feminisees/', graines_feminisees_view, name='graines_feminisees_view'),
    path('graines-autofloraison/', graines_autofloraison_view, name='graines_autofloraison_view'),
    path('breeding-grounds/', breeding_grounds_view, name='breeding_grounds_view'),
    path('produits-cbd/', produits_cbd_view, name='produits_cbd_view'),
    path('sensi-weeds/',sensi_weeds_view , name='sensi_weeds_view'),
    path('marchandises/', marchandises_view, name='marchandises_view'),
    path('vaporisateurs/',vaporisateur_view , name='vaporisateur_view'),
    
    
    
    path('adjust_cart_quantity/', adjust_cart_quantity, name='adjust_cart_quantity'),


]
