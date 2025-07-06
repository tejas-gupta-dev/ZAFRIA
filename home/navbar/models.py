from django.db import models
from cloudinary.models import CloudinaryField

class Users(models.Model):
    user= models.OneToOneField('auth.user', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    password = models.CharField(max_length=100)
    phone_number = models.BigIntegerField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)



    def __str__(self):
        return self.name


class Offer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = CloudinaryField('image')  # stored in MEDIA_ROOT/offers/
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    pro_image = CloudinaryField('image')
    description = models.TextField()
    price = models.IntegerField()
    color = models.TextField()
    size = models.TextField()
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'Product {self.id}- {self.description[:20]}'
    
class CartItem(models.Model):
    Users = models.ForeignKey(Users, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    selected_size = models.CharField(max_length=50, blank=True)
    selected_color = models.CharField(max_length=50, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_on = models.DateTimeField(auto_now_add=True)
    payment_done = models.BooleanField(default=False)
    
    def __str__(self):
        return super().__str__()
