from django.db.models.signals import post_save
from django.dispatch import receiver

from src.core.helpers import create_action_notification
from src.payment.enums import PaymentType
from src.payment.models import Payment


@receiver(post_save, sender=Payment)
def my_model_post_save(sender, instance, created, **kwargs):
    pass
    # if created and instance.payment_type == PaymentType.OUTCOME:
        # create_action_notification(
        #     obj_name=str(instance),
        #     action="Расход денежных средств",
        #     user=instance.created_user.get_full_name(),
        #     details=f"Тип платежа: {instance.get_payment_type_display()}.\n"
        #             f"Причина платежа: {instance.get_payment_model_type_display()}\n"
        #             f"Сумма: {instance.amount}"
        # )