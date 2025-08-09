from django.contrib.gis.db import models

from django.db import models
from django.contrib.gis.db import models as gis_models

class ShopCarTehran(models.Model):
    id = models.IntegerField(primary_key=True)
    geom = gis_models.PointField(srid=4326)
    full_id = models.CharField(max_length=255)
    osm_id = models.CharField(max_length=255)
    osm_type = models.CharField(max_length=255)
    shop = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    successful_transactions = models.IntegerField(default=0)
    score = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'shop_car_tehran_1'

    def __str__(self):
        return self.name or 'بدون نام'

#ثبت اگهی
from django.db import models
from django.contrib.auth.models import User

class Advertisement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title        
    
from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
# ایجاد مدل برای فروشندگان
class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = gis_models.PointField(null=True, blank=True)
    successful_transactions = models.IntegerField(default=0)
    score = models.FloatField(default=0.0)  # امتیاز محاسبه‌شده

    def __str__(self):
        return self.user.username            
    
#چت امن    
from django.db import models
from django.contrib.auth.models import User

class ChatRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    shop = models.ForeignKey('ShopCarTehran', on_delete=models.SET_NULL, null=True, blank=True)
    ad = models.ForeignKey('Advertisement', on_delete=models.SET_NULL, null=True, blank=True)  # اضافه کردن این خط
    message = models.TextField(default='', blank=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} (ID: {self.id})"

class ChatMessage(models.Model):
    chat_request = models.ForeignKey(ChatRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]} (ID: {self.id})"


# مدل اختصتص خودرو به هر نمایشگاه د
class Vehicle(models.Model):
    shop = models.ForeignKey(ShopCarTehran, on_delete=models.CASCADE, related_name='vehicles')
    name = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=15, decimal_places=2)
    year = models.IntegerField()
    condition = models.CharField(max_length=10, choices=[('new', 'نو'), ('used', 'دست‌دوم')])
    fuel_type = models.CharField(max_length=20, choices=[('gasoline', 'بنزین'), ('dual', 'دوگانه‌سوز')])
    mileage = models.IntegerField(default=0)  # میزان کارکرد به کیلومتر

    def __str__(self):
        return f"{self.name} - {self.base_price} تومان"

#userlocation
from django.contrib.gis.db import models
from django.contrib.auth.models import User

class UserLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.PointField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s location"

# دستورات مایگریشن:
# python manage.py makemigrations
# python manage.py migrate        