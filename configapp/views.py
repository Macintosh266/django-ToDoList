from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import PhoneMassageSerializer, VerifyCodeSerializer, UserSerializer, LoginSerializer, ToDoListSerializer
from .make_token import get_tokens_for_user
from .add_permission import IsAdminPermission


class PhoneSendMassage(APIView):
    @swagger_auto_schema(request_body=PhoneMassageSerializer)
    def post(self, request):
        serializer = PhoneMassageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data.get('phone')
        phone_obj, created = PhoneMassage.objects.get_or_create(phone=phone_number)

        code = phone_obj.set_reset_code()
        print(f"Phone: {phone_number}, Code: {code}")

        return Response(data={'message': 'Kod yuborildi'}, status=status.HTTP_200_OK)

phoneCh=None

class VerifyPhoneCode(APIView):
    @swagger_auto_schema(request_body=VerifyCodeSerializer)
    def post(self, request):
        global phoneCh
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        try:
            phone_obj = PhoneMassage.objects.get(phone=phone, time_password=code)
        except PhoneMassage.DoesNotExist:
            return Response({'error': 'Kod noto‘g‘ri yoki telefon raqam topilmadi'}, status=status.HTTP_400_BAD_REQUEST)

        phone_obj.is_bool = True
        phone_obj.save()
        phoneCh=phone

        return Response({'message': 'Kod tasdiqlandi', 'phone': phone}, status=status.HTTP_200_OK)


class StaffRegister(APIView):
    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        phone = data['phone']
        try:
            otp_obj = PhoneMassage.objects.get(phone=phoneCh)
        except PhoneMassage.DoesNotExist:
            return Response({"error": "Bu telefon raqam uchun OTP yuborilmagan"}, status=status.HTTP_400_BAD_REQUEST)

        if not otp_obj.is_bool:
            return Response({"error": "Telefon raqam OTP orqali tasdiqlanmagan"}, status=status.HTTP_400_BAD_REQUEST)

        user=User.objects.filter(phone=phone)
        if not user:
            User.objects.create_user(
                phone=phone,
                password=data['password']
            )
        else:
            return Response(data={'message':'Phone allaqachon mavjud!'})

        otp_obj.delete()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)



class LoginUser(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get('phone')
        password = serializer.validated_data.get('password')

        user = get_object_or_404(User, phone=phone)

        if not user.check_password(password):
            return Response({'error': "Parol noto‘g‘ri! Agar eslay olmasangiz qayta tiklashga harakat qilib ko'ring"}, status=status.HTTP_400_BAD_REQUEST)

        token = get_tokens_for_user(user)
        return Response(data=token, status=status.HTTP_200_OK)

    def get(self,request):
        phone = request.data.get('phone')
        if not phone:
            return Response({"error": "Telefon raqam yuborilmadi!"}, status=status.HTTP_400_BAD_REQUEST)

        pmm = PhoneMassage.objects.filter(phone=phone).first()
        if not pmm or not pmm.is_bool:
            return Response({"error": "Avval telefon raqamni tasdiqlang!"}, status=status.HTTP_403_FORBIDDEN)

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data.get('phone')

        user = get_object_or_404(User, phone=phone)

        return Response(data={"massage":user.password},status=status.HTTP_200_OK)



class Todolist(APIView):
    permission_classes = [IsAuthenticated, IsAdminPermission]

    @swagger_auto_schema(request_body=ToDoListSerializer)
    def post(self, request):
        serializer = ToDoListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        user = request.user
        data = {}

        if not user.is_staff:
            try:
                todo_item = ToDoList.objects.get(username=user.username)
                data['item'] = ToDoListSerializer(todo_item).data
                incomplete_items = ToDoList.objects.filter(is_completed=False).exclude(username=user.username)
                data["incomplete_items"] = ToDoListSerializer(incomplete_items, many=True).data
            except ToDoList.DoesNotExist:
                data["message"] = "ToDo item topilmadi."
        else:
            all_items = ToDoList.objects.all()
            data["all_items"] = ToDoListSerializer(all_items, many=True).data

        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=LoginSerializer)
    def patch(self, request):
        user = request.user
        comment = get_object_or_404(ToDoList, user=user.user)

        serializer = LoginSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(username=user.username)

        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request):
        user = request.user
        comments = ToDoList.objects.filter(username=user.username, is_completed=False)
        deleted_count = comments.update(is_completed=True)

        return Response(data={"message": f"{deleted_count} ta vazifa o'chirildi"}, status=status.HTTP_200_OK)
