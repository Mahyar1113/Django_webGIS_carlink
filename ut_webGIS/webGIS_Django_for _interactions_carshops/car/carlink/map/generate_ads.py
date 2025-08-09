import random
from django.contrib.auth.models import User
from map.models import Advertisement
from faker import Faker
import os
import django

# تنظیمات Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carlink.settings')
django.setup()

fake = Faker('fa_IR')  # برای تولید داده‌های فارسی
admin_user = User.objects.get(username='admin')  # فرض می‌کنیم ادمین با این نام هست

# لیست عناوین و توضیحات فرضی
titles = ['دنا اتوماتیک', 'پژو 206', 'سمند LX', 'تیبا 2', 'پراید 131', 'هایما S7', 'تارا', 'سورن پلاس', 'دنا پلاس', 'پارس ELX']
descriptions = ['خودرو صفر، رنگ سفید، بیمه تکمیل', 'مدل 1402، کم‌کارکرد، سالم', 'اتوماتیک، شاسی‌بلند، رنگ مشکی']
prices = [random.randint(500000000, 1500000000) for _ in range(15)]

# ثبت 15 آگهی
for i in range(15):
    ad = Advertisement(
        user=admin_user,
        title=random.choice(titles) + f' {random.randint(1400, 1403)}',
        description=random.choice(descriptions),
        price=prices[i] / 100,  # تبدیل به اعشار (مثلاً 500000000 → 5000000.00)
        is_approved=random.choice([True, False])
    )
    ad.save()
    print(f"آگهی {ad.title} با قیمت {ad.price} ثبت شد.")

print("15 آگهی فرضی با موفقیت ثبت شدند!")