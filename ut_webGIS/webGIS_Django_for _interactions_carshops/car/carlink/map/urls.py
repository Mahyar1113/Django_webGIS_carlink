from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    
    path('', views.test_template, name='test_template'),# invoke base.html
    path('login/', views.index_view, name='login'),
    
    path('map/', views.map_view, name='map_view'),
    path('get-shop-data/', views.get_shop_data, name='shop_data'),
    path('save-location/', views.save_location),
    path('delete-location/', views.delete_location),
    path('update-location/', views.update_location),
    path('profile/', views.profile_view, name='profile'),
    path('search/', views.search_view, name='search'),
    path('create-ad/', views.create_advertisement, name='create_ad'),
    path('ad-list/', views.ad_list, name='ad_list'),
    path('manage-ads/', views.manage_ads, name='manage_ads'),
    path('seller-map/', views.seller_map, name='seller_map'),
    path('chat/', views.request_chat_or_call, name='chat_request'),
    path('chat/accept/<int:request_id>/', views.accept_chat_request, name='accept_chat_request'),
    path('chat/room/<int:request_id>/', views.chat_room, name='chat_room'),
    path('reply/<int:request_id>/', views.reply_message, name='reply_message'),  # اضافه شده
    path('condition-chart-data/', views.condition_chart_data, name='condition_chart_data'),
    path('shop-chart-data/', views.shop_chart_data, name='shop_chart_data'),
    path('condition-analysis/', TemplateView.as_view(template_name='condition_analysis.html')),
    path('shop-avg-price-data/', views.shop_avg_price_data, name='shop_avg_price_data'),
    path('shop-count/', views.shop_count, name='shop_count'),
    path('shop-vehicle-details/<int:shop_id>/', views.shop_vehicle_details, name='shop_vehicle_details'),
    path('shop/<int:shop_id>/map-link/', views.shop_map_link, name='shop_map_link'),
    path('condition-analysis/', views.condition_analysis, name='condition_analysis'),
    path('region-shop-count/', views.region_shop_count, name='region_shop_count'),
    path('save-user-location/', views.save_user_location, name='save_user_location'),
    path('logout/', auth_views.LogoutView.as_view(next_page=''), name='logout'),
    path('get-user-location/<int:user_id>/', views.get_user_location, name='get_user_location'),
   

]