from celery import shared_task

import logging




import logging

logger = logging.getLogger(__name__)

@shared_task
def appointmeant_delete_task(id):
    from .models import Appointment,Payment
    app_obj = Appointment.objects.get(id=id)
    if not Payment.objects.filter(appointment=app_obj).exists():
        logger.debug(f"appointmeant deleted{app_obj.id}")
        app_obj.delete()
        

    