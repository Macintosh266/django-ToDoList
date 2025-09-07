from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import *

class ToDoListSerializer(serializers.ModelSerializer):
    class Meta:
        model=ToDoList
        fields=['user','title','description','is_completed']
        read_only_fields = ['user']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

    def validate(self,attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        try:
            user=User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {
                "succes":False,
                "detail":"User does not exist!"

            })
        auth_phone=authenticate(username=user.username,password=password)

        if auth_phone is None:
            raise serializers.ValidationError(
                {
                    "succes":False,
                    "detail":"Username or Password is invalid!"
                }
            )

        attrs['user']=auth_phone
        return attrs



class PhoneMassageSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ "username", "email", "password"]
        read_only_fields = ["is_admin", "is_staff","is_user", "is_active"]

class VerifyCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=5)