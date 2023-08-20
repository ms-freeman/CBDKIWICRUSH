from django.contrib import admin
from .models import Category, Product, ContactMessage,NavigationItem

# Register your models here.
class AdminCategorie(admin.ModelAdmin):
    list_display = ('name', 'date_added')

class AdminProduct(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'date_added')

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'formatted_timestamp')
    list_filter = ('timestamp',)
    search_fields = ('name', 'email', 'subject', 'message')

    def formatted_timestamp(self, obj):
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')

class AdminNavigationItem(admin.ModelAdmin):
    list_display = ('title', 'link', 'order')

admin.site.register(Product, AdminProduct)
admin.site.register(Category, AdminCategorie)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(NavigationItem, AdminNavigationItem)
