from rest_framework.permissions import BasePermission
from .models import *

class IsAdminPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_admin:
            return True
        else:
            return request.method in ['GET','POST'] and request.user.is_staff
        

