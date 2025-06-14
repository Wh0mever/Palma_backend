from django.contrib.auth.models import PermissionsMixin
from django.core.cache import cache
from django.core.validators import MaxValueValidator
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.conf import settings

from django_resized import ResizedImageField

from src.user.enums import UserType, WorkerIncomeReason, WorkerIncomeType


class MyUserQuerySet(models.QuerySet):
    def by_user_industry(self, user):
        if user.type == UserType.ADMIN:
            return self
        if not user.industry:
            return self.none()
        return self.filter(industry=user.industry)

    def get_workers(self):
        worker_types = [
            UserType.SALESMAN,
            UserType.FLORIST,
            UserType.FLORIST_PERCENT,
            UserType.MANAGER,
            UserType.CRAFTER,
            UserType.OTHER,
            UserType.FLORIST_ASSISTANT,
            UserType.CASHIER,
            UserType.NO_BONUS_SALESMAN,
        ]
        return self.filter(
            type__in=worker_types
        )


class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """

    def get_queryset(self):
        return MyUserQuerySet(self.model)

    def create_user(self, username, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user

    def _create_user(self, username, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        user = self.model(username=username, **extra_fields)
        user.is_active = True
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, password, **extra_fields)

    def by_user_industry(self, user):
        if user.type == UserType.ADMIN:
            return self
        if not user.industry:
            return self.none()
        return self.filter(industry=user.industry)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Фамилия"
    )
    email = models.EmailField(verbose_name='Почта', unique=False, blank=True)
    username = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Логин"
    )
    type = models.CharField(
        max_length=255,
        choices=UserType.choices,
        verbose_name="Тип пользователя"
    )
    avatar = ResizedImageField(
        upload_to="users/avatars/",
        size=[400, 400],
        crop=['middle', 'center'],
        blank=True,
        null=True,
        verbose_name="Фото пользователя"
    )
    birthday = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="День рождения"
    )
    industry = models.ForeignKey(
        "product.Industry",
        on_delete=models.SET_NULL,
        related_name='users',
        blank=True,
        null=True,
        verbose_name="Отрасль"
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Статус персонала"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активный"
    )
    balance = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Баланс"
    )
    salary_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Зарплата"
    )
    product_factory_create_commission = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=15000,
        verbose_name="Сумма компенсации за создание букета"
    )

    USERNAME_FIELD = 'username'
    objects = MyUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.get_full_name()}"

    def save(self, *args, **kwargs):
        if self.id:
            old_instance: User = User.objects.get(pk=self.id)
            if self.avatar and self.avatar != old_instance.avatar:
                old_instance.avatar.delete()
            cache.delete(f'auth:{self.username}:{self.password}')
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name

    def has_active_shift(self):
        from src.payment.models import CashierShift
        last_shift = CashierShift.objects.filter(end_date__isnull=True, started_user=self).first()
        return True if last_shift else False


class WorkerIncomes(models.Model):
    worker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="worker_order_incomes",
        verbose_name="Сотрудник"
    )
    order = models.ForeignKey(
        'order.Order',
        on_delete=models.CASCADE,
        related_name="worker_incomes",
        null=True,
        blank=True,
        verbose_name="Заказ"
    )
    product_factory = models.ForeignKey(
        'factory.ProductFactory',
        on_delete=models.CASCADE,
        related_name="worker_incomes",
        null=True,
        blank=True,
        verbose_name="Товар из производства"
    )
    total = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма начисления"
    )
    income_type = models.CharField(
        max_length=255,
        choices=WorkerIncomeType.choices,
        verbose_name="Тип начисления"
    )
    reason = models.CharField(
        max_length=255,
        choices=WorkerIncomeReason.choices,
        verbose_name="Причина начисления"
    )
    salary_info = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Информация о зарплате"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Насичление сотрудкику"
        verbose_name_plural = "Насичления сотрудкику"

    def __str__(self):
        return f"Начисление {self.worker} - {self.created_at.strftime('%d/%m/%Y')}"


class ViewPermission(models.Model):
    view_name = models.CharField(verbose_name='Класс отоброжение', max_length=255)
    path_name = models.CharField(verbose_name='Url name', max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Окно доступа'
        verbose_name_plural = 'Окна доступов'

    def __str__(self):
        return f'{self.path_name} - {self.view_name}'


class ViewPermissionRule(models.Model):
    title = models.CharField(verbose_name='Название', max_length=255)
    permission = models.OneToOneField('ViewPermission', verbose_name='Окно доступа',
                                      on_delete=models.CASCADE, related_name='permission_rule')
    category = models.ForeignKey('ViewPermissionRuleCategory', verbose_name='Категория',
                                 on_delete=models.CASCADE, related_name='permission_rule',
                                 null=True, blank=True)
    position = models.SmallIntegerField(verbose_name='Позиция', default=30)

    class Meta:
        verbose_name = 'Доступ'
        verbose_name_plural = 'Доступы'

    def __str__(self):
        return self.title


class ViewPermissionRuleCategory(models.Model):
    title = models.CharField(verbose_name='Название', max_length=255)
    position = models.SmallIntegerField(verbose_name='Позиция', default=30)

    class Meta:
        verbose_name = 'Категория доступа'
        verbose_name_plural = 'Категории доступов'

    def __str__(self):
        return self.title


class ViewPermissionRuleGroup(models.Model):
    title = models.CharField(verbose_name='Название', max_length=255)
    permissions = models.ManyToManyField('ViewPermissionRule', verbose_name='Доступы')

    class Meta:
        verbose_name = 'Группа доступа'
        verbose_name_plural = 'Группы доступов'

    def __str__(self):
        return self.title


class ViewPermissionRuleToUser(models.Model):
    user = models.ForeignKey('User', verbose_name='Пользователь',
                             on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey('ViewPermissionRule', verbose_name='Доступ',
                                   on_delete=models.CASCADE, related_name='users')

    class Meta:
        verbose_name = 'Доступа'
        verbose_name_plural = 'Доступы'


class ViewPermissionRuleGroupToUser(models.Model):
    user = models.ForeignKey('User', verbose_name='Пользователь',
                             on_delete=models.CASCADE, related_name='permission_groups')
    group = models.ForeignKey('ViewPermissionRuleGroup', verbose_name='Доступ',
                              on_delete=models.CASCADE, related_name='users')

    class Meta:
        verbose_name = 'Группа доступа'
        verbose_name_plural = 'Группы доступов'
