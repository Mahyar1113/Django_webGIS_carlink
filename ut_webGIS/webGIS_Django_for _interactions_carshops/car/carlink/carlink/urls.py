from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from map import views  # تغییر از from . import views

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),  # برگردوندن مسیر ادمین
    path('admin/map/shopcartehran/add/', views.shop_map_view,),  # ویو سفارشی
    path('', include('map.urls')),
    
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)