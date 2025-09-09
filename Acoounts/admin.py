from django.contrib import admin
from .models import Accounts,TeenagerAndParent,StoreOtpForEmail,Concentrate, StoreOtpForPhone,FeatureToggles
# Register your models here.


admin.site.register(Accounts)
admin.site.register(TeenagerAndParent)
admin.site.register(StoreOtpForEmail)
admin.site.register(StoreOtpForPhone)

admin.site.register(Concentrate)
admin.site.register(FeatureToggles)