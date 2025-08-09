from leaflet.admin import LeafletGeoAdmin
from .models import ShopCarTehran
from django.contrib import admin

@admin.register(ShopCarTehran, site=admin.site)
class ShopCarTehranAdmin(LeafletGeoAdmin):
    list_display = ('name', 'address', 'phone', 'geom')
    search_fields = ('name', 'address')
    add_form_template = 'admin/map/shopcartehran/add_form.html'

    