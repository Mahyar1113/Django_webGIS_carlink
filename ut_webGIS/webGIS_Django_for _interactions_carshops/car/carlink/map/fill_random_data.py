import random
from .models import ShopCarTehran

# لیست‌های تصادفی برای ساخت آدرس
streets = ["خیابان آزادی", "خیابان انقلاب", "خیابان ولیعصر", "بلوار کشاورز", "خیابان شریعتی"]
neighborhoods = ["تجریش", "ونک", "جنت‌آباد", "سعادت‌آباد", "تهرانپارس"]
postal_codes = ["1234567890", "1456789012", "1678901234", "1890123456", "2012345678"]

def fill_random_data():
    # پر کردن phone
    empty_phones = ShopCarTehran.objects.filter(phone__isnull=True)
    for shop in empty_phones:
        random_number = f"021-{random.randint(100, 999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        shop.phone = random_number
        shop.save()

    # پر کردن address
    empty_addresses = ShopCarTehran.objects.filter(address__isnull=True)
    for shop in empty_addresses:
        random_address = f"{random.choice(streets)}, {random.choice(neighborhoods)}, کد پستی: {random.choice(postal_codes)}"
        shop.address = random_address
        shop.save()

    print(f"{empty_phones.count()} شماره و {empty_addresses.count()} آدرس رندم تولید و ذخیره شد.")

if __name__ == "__main__":
    fill_random_data()