from django.db import models


class ActionPermissionRequestType(models.TextChoices):
    PRODUCT_WRITE_OFF = "PRODUCT_WRITE_OFF", "Списание товара"
