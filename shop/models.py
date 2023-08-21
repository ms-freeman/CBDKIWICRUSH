# models.py
from django.db import models
from django.contrib.auth import get_user_model
class Category(models.Model):
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.TextField()
    category = models.ForeignKey(Category, related_name='categorie', on_delete=models.CASCADE)
    image = models.CharField(max_length=5000)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return self.title

class SearchQuery(models.Model):
    query = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query


class Cart(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total(self):
        cart_items = self.cartitem_set.all()  # Récupère tous les articles du panier
        total = sum(item.subtotal for item in cart_items)
        return total

    def save(self, *args, **kwargs):
        self.total = self.calculate_total()  # Met à jour le total avant de sauvegarder
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart #{self.id} - Total: {self.total}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    
    def save(self, *args, **kwargs):
        self.subtotal = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.title} - Quantity: {self.quantity}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
    
class BlogArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField()
    author = models.CharField(max_length=100)

    def __str__(self):
        return self.title
    
class NavigationItem(models.Model):
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title



