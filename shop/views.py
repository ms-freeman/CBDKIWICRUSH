from .forms import ContactForm
from django.shortcuts import render,redirect
from .models import Product, SearchQuery, ContactMessage
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.models import User
from ecommerce import settings
from django.core.mail import send_mail, EmailMessage
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .token import generatorToken
# Create your views here.
def index(request):


    products_object=Product.objects.all()
    item_name = request.GET.get('item-name')
    if item_name != '' and item_name is not None:
        products_object = Product.objects.filter(title__icontains =item_name )
       

    return render(request, 'shop/index.html', {'product_object': products_object})


def detail(request,myid):
    products_object = Product.objects.get(id=myid)
    return render(request,'shop/detail.html',{'product': products_object})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model,login,authenticate,logout
from .models import Cart, CartItem
from shop.models import Product
from decimal import Decimal

User = get_user_model()

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        # Utilisateur authentifié
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Utilisateur non authentifié, vérifier si un panier temporaire est déjà créé pour la session
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(user=None)

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    cart.total = sum(item.subtotal for item in cart.cartitem_set.all())
    cart.save()

    return redirect('cart')





def view_cart(request):
    # Récupérer l'utilisateur actuel
    user = request.user

    # Vérifier si l'utilisateur est authentifié
    if user.is_authenticated:
        # Utilisateur authentifié, récupérer le panier lié à l'utilisateur
        cart, created = Cart.objects.get_or_create(user=user)
    else:
        # Utilisateur anonyme, créer un nouveau panier sans utilisateur
        cart, created = Cart.objects.get_or_create(user=None)

    cart_items = cart.cartitem_set.all()

    return render(request, 'shop/cart.html', {'cart': cart, 'cart_items': cart_items})

def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart = cart_item.cart

    # Soustraire le prix du produit du total du panier

    cart.total -= cart_item.subtotal
    cart_item.delete()
    cart.save()

    return redirect('cart')



def register(request):
    if request.method=="POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        password1 = request.POST['password1']
        if User.objects.filter(username=username):
            messages.error(request,'Username indisponible')
            return redirect('register')
        if User.objects.filter(email=email):
            messages.error(request,'email indisponible')
            return redirect('register')
        if not username.isalnum():
            messages.error(request,'Mauvais caractere')
            return redirect('register')
        if password != password1:
            messages.error(request,'Les mots de passe ne sont pas similaire')
            return redirect('register')

        nom_utilisateur = User.objects.create_user(username=username, email=email, password=password)
        nom_utilisateur.first_name=firstname
        nom_utilisateur.last_name=lastname
        nom_utilisateur.is_active = False
        nom_utilisateur.save()
        messages.success(request,'Votre compte a bien été enregistrer !')
        #envoie mail
        subject ="Bienvenue sur OGSEED ! "
        message="Bienvenue a toi "+nom_utilisateur.first_name+" "+nom_utilisateur.last_name+"\n Nous somme heureux de vous compter parmi nous\n\n\n"
        from_email = settings.EMAIL_HOST_USER
        to_list =[nom_utilisateur.email]
        send_mail(subject,message,from_email,to_list,fail_silently=False)  
        #email confirm
        current_site= get_current_site(request)
        email_subject ="Confirmation de l'adresse mail OGseed"
        messageConfirm= render_to_string('shop/emailconfirm.html',{
             "name" : nom_utilisateur.first_name,
             'domain' : current_site.domain,
             'uid':urlsafe_base64_encode(force_bytes(nom_utilisateur.pk)),
             'token': generatorToken.make_token(nom_utilisateur)
        })
        email = EmailMessage(
            email_subject,
            messageConfirm,
            settings.EMAIL_HOST_USER,
            [nom_utilisateur.email]
        )
        email.fail_silently = False
        email.send()
         
        return redirect('user_login')
    return render(request,'shop/register.html')

#def user_login(request):
    #if request.method=="POST":
        #username = request.POST['username']
        #password = request.POST['password']
        #user = authenticate(username=username, password = password)
        #my_user = User.objects.get(username = username)
        #if user is not None:
            #login(request,user)
            #firstname = user.first_name
            #return redirect('user_login')
        #elif my_user.is_active == False:
            #messages.error(request,'Veuillez confirmer votre adresse email avant de vous connectez')
        #else:
            #messages.error(request,'INCORRECT')
            #return redirect('user_login')
    #elif request.method == "GET":
        #return render(request, 'shop/user_login.html')
    
def user_login(request):
    # Nettoyer les messages stockés dans la session
    storage = messages.get_messages(request)
    for message in storage:
        pass  # Consume the messages
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                firstname = user.first_name
                return redirect('Home')
            else:
                messages.error(request, 'Veuillez confirmer votre adresse email avant de vous connecter.')
                return redirect('user_login')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
            return redirect('user_login')
    elif request.method == "GET":
        return render(request, 'shop/user_login.html')

def logOut(request):
    # Nettoyer les messages stockés dans la session
    storage = messages.get_messages(request)
    for message in storage:
        pass  # Consume the messages

    logout(request)
    messages.success(request, 'Vous avez été déconnecté')
    return redirect('user_login')



def activate(request,uidb64,token):
    try:
        uid=force_text(urlsafe_base64_decode(uidb64))
        user=User.objects.get(pk=uid)
    except(TypeError, ValueError,OverflowError,User.DoesNotExist):
        user =None
    if user is not None and generatorToken.check_token(user,token):
        user.is_active= True
        user.save()
        messages.success(request,"Votre compte a bien ete active, felicitation !")
        return redirect('user_login')
    else:
        messages.error(request, 'Activation echoue')
        return redirect('Home')
    
    
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Formulaire envoyé !")
            return redirect('contact')  # Redirigez vers la page de contact après avoir enregistré le message
        else:
            messages.error(request, "Le formulaire n'a pas été envoyé.")
    else:
        form = ContactForm()

    return render(request, 'shop/contact.html', {'form': form})



