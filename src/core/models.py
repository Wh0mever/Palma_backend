from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator
from django.db import models, ProgrammingError
from django.contrib.auth import get_user_model

from src.core.enums import ActionPermissionRequestType

User = get_user_model()


class Settings(models.Model):
    product_sale_commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name="Процент с продажи товара"
    )
    product_factory_sale_commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name="Процент с продажи букета"
    )
    # multiple_product_sale_commission_percentage = models.DecimalField(
    #     max_digits=5,
    #     decimal_places=2,
    #     default=0,
    #     validators=[MaxValueValidator(100)],
    #     verbose_name="Процент с продажи товаров из нескольких магазинов"
    # )
    store_product_factory_sale_commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name="Процент с продажи букета флористу"
    )
    showcase_product_factory_sale_commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name="Процент с продажи букета с витрины флористу"
    )
    congratulations_product_factory_sale_commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name="Процент с продажи букета для праздника флористу"
    )
    product_factory_create_commission_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма компенсации флористу за создание букета"
    )
    # product_factory_charge_percent = models.DecimalField(
    #     max_digits=5,
    #     decimal_places=2,
    #     default=0,
    #     validators=[MaxValueValidator(100)],
    #     verbose_name="Процент наценки на букет"
    # )
    store_sweets_create_commission_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма компенсации за создание набора из сладостей для магазина"
    )
    congratulations_sweets_create_commission_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма компенсации за создание набора из сладостей на поздравление"
    )
    write_off_permission_granted_industries = ArrayField(
        base_field=models.SmallIntegerField(),
        verbose_name="Отрасли для которых разрешены списания"
    )
    permission_notification_receivers = ArrayField(
        base_field=models.CharField(),
        null=True,
        blank=True,
        verbose_name="ТГ аккаунты которым приходит оповещения о подтверждении",
    )

    def __str__(self):
        return "Настройки"

    @classmethod
    def load(cls):
        try:
            if not cls.objects.exists():
                return cls.objects.create()
            return cls.objects.first()
        except ProgrammingError:
            return None


class BotMessage(models.Model):
    text = models.TextField(
        verbose_name="Текст"
    )
    is_sent = models.BooleanField(
        default=False,
        verbose_name="Отправлен"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return f"Уведомление | {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class ActionPermissionRequest(models.Model):
    request_type = models.CharField(
        max_length=50,
        choices=ActionPermissionRequestType.choices,
        verbose_name="Тип запроса"
    )
    wh_product_write_off = models.ForeignKey(
        'warehouse.WarehouseProductWriteOff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permission_requests',
        verbose_name="Списание товара"
    )
    is_sent = models.BooleanField(
        default=False,
        verbose_name="Доставлен"
    )
    is_answered = models.BooleanField(
        default=False,
        verbose_name="Отвечен"
    )
    is_accepted = models.BooleanField(
        default=False,
        verbose_name="Разрешение дано"
    )
    created_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="permission_requests",
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )


class PermissionRequestTgMessage(models.Model):
    chat_id = models.CharField(
        verbose_name="Chat id"
    )
    message_id = models.CharField(
        verbose_name="Message id"
    )
    action_permission_request = models.ForeignKey(
        'core.ActionPermissionRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Обычный запрос"
    )
    factory_permission_request = models.ForeignKey(
        'factory.FactoryTakeApartRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Запрос на действие с букетом"
    )