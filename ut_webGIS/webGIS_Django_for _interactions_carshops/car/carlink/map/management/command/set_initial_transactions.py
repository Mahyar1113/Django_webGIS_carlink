# توی map/management/commands/set_initial_transactions.py
from django.core.management.base import BaseCommand
from map.models import ShopCarTehran
import random

class Command(BaseCommand):
    help = 'Sets initial random transaction counts for sellers'

    def handle(self, *args, **options):
        sellers = ShopCarTehran.objects.all()
        for seller in sellers:
            seller.successful_transactions = random.randint(0, 20)
            seller.save()
        self.stdout.write(self.style.SUCCESS('Successfully set initial transactions'))