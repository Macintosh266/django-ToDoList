from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import render,get_object_or_404
from .add_permission import *
from rest_framework.decorators import api_view
from rest_framework.permissions import *
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import *
from configapp.serializers import *
from .make_token import *

class StaffRegister(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        if request.user.is_admin==True:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            User.objects.create_user(username=data['username'], password=data['password'])
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data={"massage":"Dostup Yo'q"},status=status.HTTP_204_NO_CONTENT)


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

        return Response({'message': 'Kod tasdiqlandi'}, status=status.HTTP_200_OK)

    
            




class LoginUser(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self,request):
        if PhoneMassage.objects.filter(phone=phoneCh, is_bool=True):
            serialize=LoginSerializer(data=request.data)
            serialize.is_valid(raise_exception=True)
            user=get_object_or_404(User,phone=serialize.validated_data.get('username'))
            token=get_tokens_for_user(user)
            return Response(data=token)
        return Response(data={"massage":"Avval telefonni tasdiqlang"},status=status.HTTP_400_BAD_REQUEST)


class Todolist(APIView):
    permission_classes = [IsAdminPermission]

    @swagger_auto_schema(request_body=ToDoListSerializer)
    def post(self,request):
        serializer=ToDoListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)



    def get(self, request):
        todo_item = get_object_or_404(ToDoList, username=request.username)

        data = {
            "item": ToDoListSerializer(todo_item).data
        }
        if not request.data.is_admin:
            if not todo_item.is_completed:
                incomplete_items = ToDoList.objects.filter(is_completed=True).exclude(phousernamene=request.username)
                data["incomplete_items"] = ToDoListSerializer(incomplete_items, many=True).data
            
        else:
            all_items = ToDoList.objects.all()
            data["all_items"] = ToDoListSerializer(all_items, many=True).data

        return Response(data=data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=LoginSerializer)
    def patch(self,request):
        response = {'success': True}
        comment = get_object_or_404(ToDoList, username=request.username)
        serializer = LoginSerializer(comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(username=request.username)
            response['date'] = serializer.data
            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


    def delete(self,request):

        commen=ToDoList.objects.filter(username=request.username,is_completed=False)
        commen.is_completed=True
        commen.save()

        return  Response(data={"massage":"O'chirildi"},status=status.HTTP_200_OK)

