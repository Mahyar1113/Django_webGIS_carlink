from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_user_by_phone(self, phone):
        # این متد فعلاً پشتیبانی نمی‌شه، پس None برمی‌گردونه
        return None

    def set_phone(self, user, phone):
        # ذخیره مقدار phone توی مدل کاربر
        User = get_user_model()
        if not hasattr(user, 'phone'):
            raise NotImplementedError("Model does not have a phone field")
        user.phone = phone
        user.save()
        return user