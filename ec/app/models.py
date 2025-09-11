from django.db import models
from django.contrib.auth.models import User
# Create your models here.
BOULEVARD_CHOICES = (
    ('MAARIF','MAARIF'),
    ('ANCIENNE MÉDINA','ANCIENNE MÉDINA'),
    ('QUARTIER DES HABOUS','QUARTIER DES HABOUS'),
    ('LA PLACE MOHAMMED-V','LA PLACE MOHAMMED-V'),
    ('DERB GHALLEF','DERB GHALLEF'),
    ('LE BOULEVARD MOHAMMED ','LE BOULEVARD MOHAMMED '),
    ('LE MARCHÉ CENTRAL','LE MARCHÉ CENTRAL'),
    ('COLLINE ANFA','COLLINE ANFA'),
)

CATEGORY_CHOICES=(
    ('P1','Balais'),
    ('P2','Five Stars'),
    ('P3','Raclettes'),
    ('P4','Brosses'),
    ('P5','Pelles'),
    ('P6','Etagéres'),
    ('P7','Etagéres Chaussures'),
    ('P8','PASS360'),
    ('P9','RAMRAK'),
    ('P10','Cintre'),
    ('P12','Casques'),
    )

class Product(models.Model):
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    composition = models.TextField(default='')
    prodapp = models.TextField(default='')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=4)
    product_image = models.ImageField(upload_to='product')
    def __str__(self):
       return self.title
   
class Customer(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    mobile = models.IntegerField(default=0)
    zipcode = models.IntegerField()
    boulevard = models.CharField(choices=BOULEVARD_CHOICES, max_length=100)
    def __str__(self):
      return self.name
    

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_cost(self):
        # Use selling_price instead of discounted_price
        return self.quantity * self.product.selling_price



STATUS_CHOICES = (
        ('Accepted','Accepted'),
        ('Packed','Packed'),
        ('On The Way','On The Way'),
        ('Delivered','Delivered'),
        ('Cancel','Cancel'),
        ('Pending','Pending'),
    )

class Payment(models.Model):
        user = models.ForeignKey(User,on_delete=models.CASCADE)
        amount = models.FloatField()
        razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
        razorpay_payment_status = models.CharField(max_length=100, blank=True, null=True)
        razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
        paid = models.BooleanField(default=False)


class OrderPlaced(models.Model):
        user = models.ForeignKey(User,on_delete=models.CASCADE)
        customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
        product = models.ForeignKey(Product, on_delete=models.CASCADE)
        quantity = models.PositiveIntegerField(default=1)
        ordered_date = models.DateTimeField(auto_now_add=True)
        status = models.CharField(max_length=50,choices=STATUS_CHOICES , default='Pending')
        payment = models.ForeignKey(Payment, on_delete=models.CASCADE, default="")
        @property
        def total_cost(self):
            return self.quantity * self.product.selling_price

