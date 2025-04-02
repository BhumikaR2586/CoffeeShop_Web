from django.contrib import admin
from .models import Coffee
# admin-12345678 admin@gmail.com

class CoffeeAdmin(admin.ModelAdmin):
    list_display  = ('name' , 'price', 'qauntity')

admin.site.register(Coffee, CoffeeAdmin)