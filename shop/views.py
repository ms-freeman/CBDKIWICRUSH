from .forms import ContactForm
from django.shortcuts import render,redirect,get_object_or_404
from .models import Product, SearchQuery, ContactMessage,Category
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model,login, authenticate,logout
from django.contrib.auth.models import User
from ecommerce import settings
from django.core.mail import send_mail, EmailMessage
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .token import generatorToken
from django.contrib.auth import get_user_model,login,authenticate,logout
from .models import Cart, CartItem
from decimal import Decimal
from django.http import JsonResponse
                        #Accueil
def index(request):
    products_object=Product.objects.all()
    item_name = request.GET.get('item-name')
    if item_name != '' and item_name is not None:
        products_object = Product.objects.filter(title__icontains =item_name )
    return render(request, 'shop/index.html', {'product_object': products_object})
                        #FIN Accueil             
                        #fiche produits
def detail(request,myid):
    products_object = Product.objects.get(id=myid)
    return render(request,'shop/detail.html',{'product': products_object})
                        #Fin fiche produits
                     # PANIER + options
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
    cart_item.delete()
    cart.save()
    return redirect('cart')
def adjust_cart_quantity(request):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        cart_item_id = request.POST.get('cart_item_id')
        new_quantity = int(request.POST.get('new_quantity'))
        if request.user.is_authenticated:
            user_cart = Cart.objects.get(user=request.user)
        else:
            session_key = request.session.session_key
            user_cart, created = Cart.objects.get_or_create(session_key=session_key)
        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.quantity = new_quantity
        cart_item.save()
        new_total = user_cart.calculate_total()
        response_data = {
            'success': True,
            'new_subtotal': cart_item.subtotal,
            'new_total': new_total,
        }
        
        return JsonResponse(response_data)
    else:
        return JsonResponse({'success': False})
                        # FIN PANIER
                        # Enregistrement et connection des utilisateurs + ACTIVATION MESSAGES
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
                                # fin enregistrement et connection des utilisateurs + ACTIVATION MESSAGES
                                # FORMULAIRE DE CONTACT
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
                            # FIN FORMULAIRE DE CONTACT
                                                            
                            # MENU PRINCIPAL
def graines_cannabis_view(request):
    category = Category.objects.get(name="Graines de Cannabis")
    products = Product.objects.filter(category=category)
    context = {
        'products': products,
    }
    return render(request, 'shop/grainesdecannabis.html', context)

def graines_feminisees_view(request):
    category = Category.objects.get(name="Graines Féminisées")
    products = Product.objects.filter(category=category)
    context = {
        'products': products,
    }
    return render(request, 'shop/grainesfeminisees.html', context)

def graines_autofloraison_view(request):
    category = Category.objects.get(name="Graines Autofloraison")
    products = Product.objects.filter(category=category)
    context = {
        'products': products,
    }
    return render(request, 'shop/grainesautofloraison.html', context)

def breeding_grounds_view(request):
    category = Category.objects.get(name="Breeding Grounds")
    products = Product.objects.filter(category=category)
    context = {
        'products': products,
    }
    return render(request, 'shop/breedinggrounds.html', context)

def produits_cbd_view(request):
    category = Category.objects.get(name="Produits CBD")
    products = Product.objects.filter(category=category)
    context = {
        'products': products,
    }
    return render(request, 'shop/produitscbd.html', context)

def sensi_weeds_view(request):
    category = Category.objects.get(name="Sensi Weeds")
    products = Product.objects.filter(category=category)
    context = {
        'products': products,
    }
    return render(request, 'shop/sensiweeds.html', context)

def marchandises_view(request):
    category = Category.objects.get(name="Marchandises")
    products = Product.objects.filter(category=category)
    context = {
        'products': products,
    }
    return render(request, 'shop/marchandises.html', context)

def vaporisateur_view(request):
    category = Category.objects.get(name="Vaporisateurs")
    products = Product.objects.filter(category=category)
    context = {
        'products': products,
    }
    return render(request, 'shop/vaporisateurs.html', context)

                        # FIN MENU PRINCIPAL








