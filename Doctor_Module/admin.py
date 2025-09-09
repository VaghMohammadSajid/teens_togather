from django.contrib import admin
from .models import DoctorProfileModel,AvailableTime,ReviewAndRating,DoctorProfileModelEdit, DoctorProfileFieldEdit

# Register your models here.
admin.site.register(DoctorProfileModel)
admin.site.register(AvailableTime)
admin.site.register(ReviewAndRating)


class DoctorProfileFieldEditInline(admin.TabularInline):
    model = DoctorProfileFieldEdit
    extra = 1  

class DoctorProfileModelEditAdmin(admin.ModelAdmin):
    list_display = ('accounts', 'status', 'created_at', 'rejection_reason')  
    list_filter = ('status', 'created_at')  
    inlines = [DoctorProfileFieldEditInline]  

class DoctorProfileFieldEditAdmin(admin.ModelAdmin):
    list_display = ('doctor_profile_edit', 'field_name', 'field_value')
    search_fields = ('field_name', 'field_value')

admin.site.register(DoctorProfileModelEdit, DoctorProfileModelEditAdmin)
admin.site.register(DoctorProfileFieldEdit, DoctorProfileFieldEditAdmin)
