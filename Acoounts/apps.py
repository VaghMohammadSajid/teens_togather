from django.apps import AppConfig

import logging


logger = logging.getLogger(__name__)

BLOCKLIST = []
class AcoountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Acoounts'


    def ready(self):
        from .models import FeatureToggles  
        try:
            global BLOCKLIST
            BLOCKLIST = list( FeatureToggles.objects.all().values_list('disable_feature',flat=True))
            
            
        except Exception:
            logger.critical("Undefined global variabile",exc_info=True)