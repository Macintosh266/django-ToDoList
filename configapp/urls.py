from django.urls import path
from configapp.views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

from rest_framework_simplejwt.views import TokenVerifyView


urlpatterns=[
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/', LoginUser.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('todaolist/',Todolist.as_view(),name='todolist'),
]