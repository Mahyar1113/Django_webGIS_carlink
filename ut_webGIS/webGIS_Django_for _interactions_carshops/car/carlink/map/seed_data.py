import random
from .models import ShopCarTehran, Vehicle

def seed_data():
    # گرفتن همه نمایشگاه‌ها
    shops = list(ShopCarTehran.objects.all())
    if not shops:
        print("هیچ نمایشگاهی پیدا نشد!")
        return

    # لیست خودروها
    base_vehicles = [
        {'name': 'پراید 131', 'base_price': 200000000, 'year': 1395, 'condition': 'used', 'fuel_type': 'gasoline'},
        {'name': 'پژو 206 تیپ 2', 'base_price': 350000000, 'year': 1398, 'condition': 'used', 'fuel_type': 'gasoline'},
        {'name': 'تیبا 2', 'base_price': 280000000, 'year': 1400, 'condition': 'new', 'fuel_type': 'gasoline'},
        {'name': 'سمند LX', 'base_price': 400000000, 'year': 1397, 'condition': 'used', 'fuel_type': 'gasoline'},
        {'name': 'دنا پلاس', 'base_price': 600000000, 'year': 1402, 'condition': 'new', 'fuel_type': 'gasoline'},
        {'name': 'رانا پلاس', 'base_price': 500000000, 'year': 1401, 'condition': 'new', 'fuel_type': 'gasoline'},
        {'name': 'تارا', 'base_price': 700000000, 'year': 1403, 'condition': 'new', 'fuel_type': 'gasoline'},
        {'name': 'سورن پلاس', 'base_price': 450000000, 'year': 1399, 'condition': 'used', 'fuel_type': 'gasoline'},
        {'name': 'پژو 405 GLX', 'base_price': 300000000, 'year': 1396, 'condition': 'used', 'fuel_type': 'gasoline'},
        {'name': 'تیبا هاچ‌بک', 'base_price': 320000000, 'year': 1401, 'condition': 'new', 'fuel_type': 'gasoline'},
        {'name': 'پارس تندر', 'base_price': 380000000, 'year': 1398, 'condition': 'used', 'fuel_type': 'gasoline'},
        {'name': 'کوئیک R', 'base_price': 400000000, 'year': 1402, 'condition': 'new', 'fuel_type': 'gasoline'},
        {'name': 'ساینا', 'base_price': 290000000, 'year': 1400, 'condition': 'new', 'fuel_type': 'gasoline'},
        {'name': 'دنا معمولی', 'base_price': 550000000, 'year': 1401, 'condition': 'new', 'fuel_type': 'gasoline'},
        {'name': 'برلیانس H330', 'base_price': 420000000, 'year': 1399, 'condition': 'used', 'fuel_type': 'gasoline'},
        {'name': 'جک J4', 'base_price': 650000000, 'year': 1402, 'condition': 'new', 'fuel_type': 'gasoline'},
        {'name': 'چانگان CS35', 'base_price': 800000000, 'year': 1403, 'condition': 'new', 'fuel_type': 'gasoline'},
        {'name': 'ام وی ام 315', 'base_price': 360000000, 'year': 1397, 'condition': 'used', 'fuel_type': 'gasoline'},
        {'name': 'لیفان X60', 'base_price': 480000000, 'year': 1398, 'condition': 'used', 'fuel_type': 'gasoline'},
        {'name': 'هایما S7', 'base_price': 750000000, 'year': 1402, 'condition': 'new', 'fuel_type': 'gasoline'},
    ]

    # اختصاص حداقل یک خودرو به هر نمایشگاه
    for shop in shops:
        vehicle_data = random.choice(base_vehicles)
        Vehicle.objects.create(
            shop=shop,
            name=vehicle_data['name'],
            base_price=vehicle_data['base_price'],
            year=vehicle_data['year'],
            condition=vehicle_data['condition'],
            fuel_type=vehicle_data['fuel_type'],
            mileage=random.randint(0, 150000)  # کارکرد تصادفی
        )

    # اضافه کردن خودروهای اضافی برای تنوع
    additional_count = 180  # برای رسیدن به حدود 200 خودرو (هر نمایشگاه به‌طور متوسط 1-2 خودرو)
    for _ in range(additional_count):
        shop = random.choice(shops)
        vehicle_data = random.choice(base_vehicles)
        Vehicle.objects.create(
            shop=shop,
            name=vehicle_data['name'],
            base_price=vehicle_data['base_price'],
            year=vehicle_data['year'],
            condition=vehicle_data['condition'],
            fuel_type=vehicle_data['fuel_type'],
            mileage=random.randint(0, 150000)
        )

    print(f"داده‌ها با موفقیت وارد شدند! تعداد کل خودروها: {Vehicle.objects.count()}")

if __name__ == "__main__":
    seed_data()