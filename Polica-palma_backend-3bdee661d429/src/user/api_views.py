from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from src.base.api_views import MultiSerializerViewSetMixin
from src.user.enums import UserType, WorkerIncomeType, WorkerIncomeReason
from src.user.serializers import UserProfileSerializer, UserChangePasswordSerializer, UserLoginSerializer, \
    UserRegistrationSerializer, UserListSerializer

User = get_user_model()


class UserProfileViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserChangePasswordView(UpdateAPIView):
    serializer_class = UserChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data.get('password'))
        user.save()
        return Response(data={"message": "Password updated successfully"}, status=200)


class UserLoginView(APIView):
    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            400: "User does not exist",
            200: "User is successfully authenticated"
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"error", "User does not exist"}, status=400)

        return Response(UserProfileSerializer(instance=user).data, status=200)


class UserRegistrationView(APIView):
    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={
            200: UserProfileSerializer()
        }
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(data=UserProfileSerializer(instance=user).data, status=200)


class UserViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_action_classes = {
        "list": UserListSerializer,
        "workers": UserListSerializer,
        "product_factory_creators": UserListSerializer,
        "have_orders": UserListSerializer,
        "have_orders_created": UserListSerializer,
        "salesmen_list": UserListSerializer,
        "payment_creators": UserListSerializer,
    }
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_fields = ('type', 'industry')

    def get_queryset(self):
        qs = super().get_queryset()
        # qs = qs.by_user_industry(self.request.user)
        return qs

    def workers(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset().get_workers())
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=200)

    def product_factory_creators(self, request):
        users = self.get_queryset()
        users = users.filter(
            type__in=[UserType.FLORIST, UserType.FLORIST_PERCENT, UserType.CRAFTER, UserType.FLORIST_ASSISTANT])
        if request.user.type == UserType.WAREHOUSE_MASTER:
            users = users.filter(type__in=[UserType.FLORIST, UserType.FLORIST_PERCENT, UserType.FLORIST_ASSISTANT])
        elif request.user.type == UserType.CRAFTER:
            users = users.filter(type=UserType.CRAFTER)

        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data, status=200)

    def salesmen_list(self, reqeust):
        users = self.get_queryset()
        users = users.filter(type__in=[
            UserType.SALESMAN, UserType.FLORIST_PERCENT, UserType.NO_BONUS_SALESMAN, UserType.MANAGER, UserType.ADMIN
        ])
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data, status=200)

    def have_orders(self, request):
        salesman_list = User.objects.filter(attached_orders__isnull=False).distinct()
        serializer = self.get_serializer(salesman_list, many=True)
        return Response(serializer.data, status=200)

    def have_orders_created(self, request):
        salesman_list = User.objects.filter(
            Q(orders__isnull=False)
            | Q(type__in=[UserType.ADMIN, UserType.CASHIER, UserType.MANAGER])
        ).distinct()
        serializer = self.get_serializer(salesman_list, many=True)
        return Response(serializer.data, status=200)

    def payment_creators(self, request):
        users = User.objects.filter(type__in=[UserType.MANAGER, UserType.ADMIN, UserType.CASHIER])
        serializers = self.get_serializer(users, many=True)
        return Response(serializers.data, status=200)

    def has_active_shift(self, request):
        from src.payment.models import CashierShift
        last_shift: CashierShift = CashierShift.objects.filter(end_date__isnull=True, started_user=request.user).first()
        if last_shift:
            return Response(data={'has_shift': True}, status=200)
        return Response(data={'has_shift': False}, status=200)


class UserTypeOptionsView(APIView):
    def get(self, request, *args, **kwargs):
        user_type_choices = [{"value": choice[0], "label": choice[1]} for choice in UserType.choices]
        return Response(user_type_choices, status=200)


class WorkerIncomeTypeOptionsView(APIView):
    def get(self, request, *args, **kwargs):
        worker_income_type_choices = [{"value": choice[0], "label": choice[1]} for choice in WorkerIncomeType.choices]
        return Response(worker_income_type_choices, status=200)


class WorkerIncomeReasonOptionsView(APIView):
    def get(self, request, *args, **kwargs):
        worker_income_type_choices = [{"value": choice[0], "label": choice[1]} for choice in WorkerIncomeReason.choices]
        return Response(worker_income_type_choices, status=200)
