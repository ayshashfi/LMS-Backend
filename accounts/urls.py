from django.urls import path
from .views import RegisterUser, LoginUser, BlockUnblockUserView, UserListView, ProfileView, DepartmentListView, DepartmentEmployeesView, ProfileUpdateView
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', jwt_views.TokenVerifyView.as_view(), name='token_verify'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:user_id>/block-unblock/', BlockUnblockUserView.as_view(), name='block-unblock-user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),  # For updating the profile
    path('departments/', DepartmentListView.as_view(), name='department-list'),
    path('employees/department/', DepartmentEmployeesView.as_view(), name='department-employees'),
 
]
