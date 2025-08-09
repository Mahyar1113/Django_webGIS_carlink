from django.shortcuts import render
from .models import ShopCarTehran, UserLocation
import json
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import redirect
from .models import ChatRequest, ShopCarTehran, Vehicle, Advertisement, ChatMessage
from django.db.models import Avg, Count
from django.contrib.gis.db.models.functions import Distance
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.gis.geos import Point, GEOSGeometry
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_template(request):
    return render(request, 'map/base.html')

def index_view(request):
    return render(request, 'index.html')



@login_required
def condition_analysis(request):
    if not request.user.is_authenticated:
        return redirect('index')
    return render(request, 'carlink/condition-analysis.html')    

def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def map_view(request):
    if not request.user.is_authenticated:
        return render(request, 'map/index.html')  
    if is_admin(request.user):
        return redirect('/admin/')
    shops = ShopCarTehran.objects.all()
    shops_data = [
        {
            'latitude': shop.geom.y,
            'longitude': shop.geom.x,
            'name': shop.name if shop.name else 'ناشناخته',
            'address': shop.address if shop.address else 'آدرس موجود نیست',
            'phone': shop.phone if shop.phone else 'شماره موجود نیست',
            'is_active': shop.is_active,
            'avg_price': float(shop.vehicles.aggregate(avg_price=Avg('base_price'))['avg_price'] or 0)
        } for shop in shops if shop.vehicles.exists()
    ]
    print(f"Shops data sent to template: {shops_data}")
    ads = Advertisement.objects.filter(is_approved=True).select_related('user')
    
    # دریافت موقعیت کاربر
    user_location = UserLocation.objects.filter(user=request.user).first()
    location_coords = user_location.location.coords if user_location and user_location.location else None

    context = {
        'shops': json.dumps(shops_data),
        'ads': ads,
        'is_admin': is_admin(request.user),
        'location_coords': location_coords
    }
    return render(request, 'map/map.html', context)



@login_required
def save_user_location(request):
    if request.method == "POST":
        data = json.loads(request.body)
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
        location = Point(lng, lat)

        user_location, created = UserLocation.objects.update_or_create(
            user=request.user,
            defaults={'location': location}
        )
        return JsonResponse({'status': 'success', 'message': 'موقعیت با موفقیت ذخیره شد.'})
    return JsonResponse({'status': 'error', 'message': 'درخواست نامعتبر است.'}, status=400)

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('index')
    ads = Advertisement.objects.filter(user=request.user)
    sent_requests = ChatRequest.objects.filter(sender=request.user, is_accepted=True).prefetch_related('messages')
    received_requests = ChatRequest.objects.filter(receiver=request.user, is_accepted=True).prefetch_related('messages')
    all_requests = list(sent_requests) + list(received_requests)

    user_location = UserLocation.objects.filter(user=request.user).first()
    location_coords = user_location.location.coords if user_location and user_location.location else None

    context = {
        'user': request.user,
        'ads': ads,
        'all_requests': all_requests,
        'location_coords': location_coords
    }
    return render(request, 'map/profile.html', context)

def shop_map_view(request):
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT id, ST_X(geom) as lon, ST_Y(geom) as lat, name, address, phone FROM shop_car_tehran_1")
            rows = cursor.fetchall() or []
            print(f"DB rows: {rows}")
            shops = [
                {'id': row[0], 'latitude': row[2], 'longitude': row[1], 'name': row[3], 'address': row[4], 'phone': row[5]}
                for row in rows
            ]
        except Exception as e:
            print(f"Error: {e}")
            shops = []  
    return render(request, 'admin/map/shopcartehran/add_form.html', {'shops': shops})

@csrf_exempt
def update_location(request):
    if request.method == "POST":
        location_id = request.POST.get('id')
        geom = request.POST.get('geom')
        name = request.POST.get('name', '')
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE shop_car_tehran_1 SET geom = ST_GeomFromText(%s, 4326), name = %s, address = %s, phone = %s WHERE id = %s",
                    [geom, name, address, phone, location_id]
                )
            return JsonResponse({'status': 'success', 'message': 'نقطه با موفقیت به‌روزرسانی شد'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'درخواست نامعتبر'})

@csrf_exempt
def delete_location(request):
    if request.method == "POST":
        location_id = request.POST.get('id')
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM shop_car_tehran_1 WHERE id = %s", [location_id])
            return JsonResponse({'status': 'success', 'message': 'نقطه با موفقیت حذف شد'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'درخواست نامعتبر'})

@csrf_exempt
def save_location(request):
    if request.method == "POST":
        geom = request.POST.get('geom')
        name = request.POST.get('name', '')
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO shop_car_tehran_1 (geom, name, address, phone) VALUES (ST_GeomFromText(%s, 4326), %s, %s, %s)",
                    [geom, name, address, phone]
                )
            return JsonResponse({'status': 'success', 'message': 'نمایشگاه با موفقیت اضافه شد'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'درخواست نامعتبر'})

def get_shop_data(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, ST_X(geom) as lon, ST_Y(geom) as lat, name, address, phone FROM shop_car_tehran_1")
        rows = cursor.fetchall() or []
        shops = [
            {'id': row[0], 'latitude': row[2], 'longitude': row[1], 'name': row[3], 'address': row[4], 'phone': row[5]}
            for row in rows
        ]
    return JsonResponse({'shops': shops})

@login_required
def create_advertisement(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        ad = Advertisement(user=request.user, title=title, description=description, price=price)
        ad.save()
        messages.success(request, 'درخواست شما با موفقیت ثبت شد. بعد از تأیید ادمین در لیست آگهی‌ها نمایش داده خواهد شد.')
        return redirect('create_ad')
    return render(request, 'map/create_ad.html')

@login_required
def ad_list(request):
    if not request.user.is_authenticated:
        return render(request, 'map/index.html')  
    if is_admin(request.user):
        return redirect('/admin/')
    ads = Advertisement.objects.filter(is_approved=True)
    return render(request, 'map/ad_list.html', {'ads': ads})

@staff_member_required
def manage_ads(request):
    ads = Advertisement.objects.all()
    if request.method == "POST":
        ad_id = request.POST.get('ad_id')
        action = request.POST.get('action')
        ad = Advertisement.objects.get(id=ad_id)
        if action == 'approve':
            ad.is_approved = True
        elif action == 'reject':
            ad.is_approved = False
        ad.save()
        return JsonResponse({'status': 'success', 'message': f'آگهی {action} شد'})
    return render(request, 'map/manage_ads.html', {'ads': ads})

def update_seller_scores():
    sellers = ShopCarTehran.objects.all()
    for seller in sellers:
        transaction_score = seller.successful_transactions * 0.5
        nearby_sellers = ShopCarTehran.objects.exclude(id=seller.id).annotate(
            distance=Distance('geom', seller.geom)
        ).filter(distance__lt=1000).count()
        density_score = min(nearby_sellers * 0.2, 2.0)
        seller.score = transaction_score + density_score
        seller.save()

def seller_map(request):
    update_seller_scores()
    sellers = ShopCarTehran.objects.all()
    return render(request, 'map/seller_map.html', {'sellers': sellers})

@login_required
def chat_room(request, request_id=None):
    logger.debug(f"درخواست برای chat-room با ID {request_id} دریافت شد")
    chat_request = None
    users = User.objects.exclude(id=request.user.id)
    received_requests = ChatRequest.objects.filter(receiver=request.user)
    if request_id:
        try:
            chat_request = ChatRequest.objects.get(id=request_id)
            if not chat_request.is_accepted or (request.user != chat_request.sender and request.user != chat_request.receiver):
                logger.error(f"خطا: دسترسی غیرمجاز به درخواست ID {request_id} توسط {request.user.username}")
                return JsonResponse({'status': 'error', 'error': 'دسترسی غیرمجاز'}, status=403)
        except ChatRequest.DoesNotExist as e:
            logger.error(f"خطا: درخواست با ID {request_id} پیدا نشد: {e}")
            return JsonResponse({'status': 'error', 'error': 'درخواست پیدا نشد'}, status=404)
    return render(request, 'map/chat_room.html', {'chat_request': chat_request, 'users': users, 'received_requests': received_requests})

@login_required
def accept_chat_request(request, request_id):
    logger.debug(f"درخواست پذیرش دریافت شد: request_id={request_id}, user={request.user.username}")
    if request.method == "POST":
        try:
            chat_request = ChatRequest.objects.get(id=request_id, receiver=request.user)
            if chat_request.is_accepted:
                logger.warning(f"هشدار: درخواست با ID {request_id} قبلاً پذیرفته شده")
                return JsonResponse({'status': 'error', 'error': 'درخواست قبلاً پذیرفته شده'}, status=400)
            chat_request.is_accepted = True
            chat_request.save()
            logger.debug(f"درخواست با ID {request_id} پذیرفته شد")
            return redirect(f'/chat-room/{request_id}/')
        except ChatRequest.DoesNotExist as e:
            logger.error(f"خطا: درخواست با ID {request_id} پیدا نشد: {e}")
            return JsonResponse({'status': 'error', 'error': 'درخواست پیدا نشد'}, status=404)
        except Exception as e:
            logger.error(f"خطای ناشناخته در پذیرش: {e}")
            return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
    logger.debug("درخواست غیرمجاز، ریدایرکت به chat-request")
    return redirect('chat_request')

@login_required
def reply_message(request, request_id):
    logger.debug(f"درخواست پاسخ به پیام با ID {request_id} دریافت شد")
    if request.method == "POST":
        try:
            chat_request = ChatRequest.objects.get(id=request_id)
            if request.user != chat_request.sender and request.user != chat_request.receiver:
                logger.error(f"خطا: دسترسی غیرمجاز به پاسخ برای درخواست ID {request_id} توسط {request.user.username}")
                return JsonResponse({'status': 'error', 'error': 'دسترسی غیرمجاز'}, status=403)
            reply_message = request.POST.get('reply_message', '').strip()
            if not reply_message:
                logger.error("خطا: پاسخ خالی است")
                return JsonResponse({'status': 'error', 'error': 'پاسخ خالی است'}, status=400)
            ChatMessage.objects.create(chat_request=chat_request, sender=request.user, message=reply_message)
            logger.debug(f"پاسخ با موفقیت برای درخواست ID {request_id} ثبت شد: {reply_message}")
            return redirect(f'/profile/')
        except ChatRequest.DoesNotExist as e:
            logger.error(f"خطا: درخواست با ID {request_id} پیدا نشد: {e}")
            return JsonResponse({'status': 'error', 'error': 'درخواست پیدا نشد'}, status=404)
        except Exception as e:
            logger.error(f"خطای ناشناخته در پاسخ: {e}")
            return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
    logger.debug("درخواست غیرمجاز برای پاسخ")
    return JsonResponse({'status': 'error', 'error': 'فقط POST مجاز است'}, status=405)

@login_required
def request_chat_or_call(request):
    logger.debug(f"درخواست_detail: method={request.method}, user={request.user.username}")
    if request.method == "POST":
        try:
            receiver_id = request.POST.get('receiver_id')
            shop_id = request.POST.get('shop_id')
            message = request.POST.get('message', '').strip()
            logger.debug(f"داده‌های POST: receiver_id={receiver_id}, shop_id={shop_id}, message={message}")
            if not receiver_id:
                logger.error("خطا: receiver_id خالی است")
                return JsonResponse({'status': 'error', 'error': 'کاربر گیرنده مشخص نشده'}, status=400)
            if not message:
                logger.error("خطا: پیام خالی است")
                return JsonResponse({'status': 'error', 'error': 'پیام خالی است'}, status=400)
            receiver = User.objects.get(id=receiver_id)
            shop = ShopCarTehran.objects.filter(id=shop_id).first() if shop_id and shop_id != '0' else None
            ad = Advertisement.objects.filter(user=receiver).first()
            chat_request = ChatRequest.objects.create(
                sender=request.user,
                receiver=receiver,
                shop=shop,
                ad=ad,
                message=message,
                is_accepted=True
            )
            logger.debug(f"درخواست چت با ID {chat_request.id} ایجاد شد")
            return JsonResponse({'status': 'success', 'request_id': chat_request.id})
        except User.DoesNotExist as e:
            logger.error(f"خطا: کاربر با ID {receiver_id} پیدا نشد: {e}")
            return JsonResponse({'status': 'error', 'error': 'کاربر گیرنده پیدا نشد'}, status=400)
        except Exception as e:
            logger.error(f"خطای ناشناخته: {e}")
            return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
    shops = ShopCarTehran.objects.all()
    users = User.objects.exclude(id=request.user.id)
    received_requests = ChatRequest.objects.filter(receiver=request.user, is_accepted=True)
    sent_requests = ChatRequest.objects.filter(sender=request.user)
    logger.debug(f"داده‌های رندر: تعداد کاربران={users.count()}, دریافتی={received_requests.count()}, ارسال‌شده={sent_requests.count()}")
    return render(request, 'map/chat_request.html', {'shops': shops, 'users': users, 'received_requests': received_requests, 'sent_requests': sent_requests})

def condition_chart_data(request):
    condition_data = list(Vehicle.objects.values('condition').annotate(count=Count('condition')))
    return JsonResponse({'condition_data': condition_data})

def shop_chart_data(request):
    shop_data = list(Vehicle.objects.values('shop_id', 'shop__name').annotate(count=Count('shop__name')).filter(shop__name__isnull=False))
    print("داده‌های shop_data:", shop_data)
    return JsonResponse({'shop_data': shop_data})

def shop_avg_price_data(request):
    avg_price_data = list(Vehicle.objects.values('shop__name').annotate(avg_price=Avg('base_price')).filter(shop__name__isnull=False))
    return JsonResponse({'avg_price_data': avg_price_data})

def shop_count(request):
    total_shops = ShopCarTehran.objects.count()
    return JsonResponse({'total_shops': total_shops})

def shop_vehicle_details(request, shop_id):
    vehicles = Vehicle.objects.filter(shop_id=shop_id).values('name', 'base_price', 'year', 'condition', 'fuel_type', 'mileage')
    shop_name = ShopCarTehran.objects.get(id=shop_id).name or 'نامشخص'
    return render(request, 'map/shop_vehicle_details.html', {'shop_name': shop_name, 'vehicles': vehicles})

def shop_map_link(request, shop_id):
    try:
        shop = ShopCarTehran.objects.get(id=shop_id)
        if shop.geom:
            lat = shop.geom.y
            lng = shop.geom.x
            map_link = f"javascript:flyTo({lat}, {lng});"
        else:
            map_link = "#"
        return JsonResponse({'map_link': map_link})
    except ShopCarTehran.DoesNotExist:
        return JsonResponse({'map_link': '#'}, status=404)

def search_view(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('search_type', 'all').strip().lower()
    results = {
        'ads': [],
        'shops': []
    }
    if query:
        if search_type in ['all', 'title', 'description', 'price']:
            if search_type == 'all':
                results['ads'] = Advertisement.objects.filter(
                    title__icontains=query
                ) | Advertisement.objects.filter(
                    description__icontains=query
                ) | Advertisement.objects.filter(
                    price__icontains=query.replace(',', '')
                )
            elif search_type == 'title':
                results['ads'] = Advertisement.objects.filter(title__icontains=query)
            elif search_type == 'description':
                results['ads'] = Advertisement.objects.filter(description__icontains=query)
            elif search_type == 'price':
                results['ads'] = Advertisement.objects.filter(price__icontains=query.replace(',', ''))
        
        if search_type in ['all', 'shop_name', 'shop_address', 'shop_phone']:
            if search_type == 'all':
                results['shops'] = ShopCarTehran.objects.filter(
                    name__icontains=query
                ) | ShopCarTehran.objects.filter(
                    address__icontains=query
                ) | ShopCarTehran.objects.filter(
                    phone__icontains=query
                )
            elif search_type == 'shop_name':
                results['shops'] = ShopCarTehran.objects.filter(name__icontains=query)
            elif search_type == 'shop_address':
                results['shops'] = ShopCarTehran.objects.filter(address__icontains=query)
            elif search_type == 'shop_phone':
                results['shops'] = ShopCarTehran.objects.filter(phone__icontains=query)
    return render(request, 'map/search_results.html', {'query': query, 'results': results})

def region_shop_count(request):
    region_no = request.GET.get('region')
    if not region_no:
        with open('static/geojson/region_22.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        shop_counts = {}
        for feature in geojson_data['features']:
            region_geom = GEOSGeometry(json.dumps(feature['geometry']))
            shop_counts[str(feature['properties']['reg_no'])] = ShopCarTehran.objects.filter(geom__within=region_geom).count()
        return JsonResponse({'shop_counts': shop_counts})

    with open('static/geojson/region_22.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    for feature in geojson_data['features']:
        if str(feature['properties']['reg_no']) == region_no:
            region_geom = GEOSGeometry(json.dumps(feature['geometry']))
            shop_count = ShopCarTehran.objects.filter(geom__within=region_geom).count()
            return JsonResponse({'shop_count': shop_count})

    return JsonResponse({'shop_count': 0})

from django.http import JsonResponse
from .models import UserLocation

@login_required
def get_user_location(request, user_id):
    try:
        user_location = UserLocation.objects.get(user_id=user_id)
        location = user_location.location.coords if user_location.location else None
        return JsonResponse({
            'status': 'success',
            'location': list(location) if location else None,
            'username': User.objects.get(id=user_id).username
        })
    except UserLocation.DoesNotExist:
        return JsonResponse({'status': 'error', 'location': None, 'username': User.objects.get(id=user_id).username})
    except Exception as e:
        return JsonResponse({'status': 'error', 'location': None, 'error': str(e)})    



