from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser,Department
from .serializers import UserRegistrationSerializer, LoginSerializer, UserSerializer, EmployeeSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status



# Register a new user
class RegisterUser(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LoginUser(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)

                if user.is_manager:
                    employees = CustomUser.objects.filter(manager=user)
                    employee_data = UserSerializer(employees, many=True).data
                    department = user.department.name if user.department else None
                else:
                    department = user.department.name if user.department else None
                    employee_data = []

                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'designation': user.designation,
                    'department': department,
                    'employees': employee_data,
                }, status=status.HTTP_200_OK)
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# View to list all users (Admin-only access)
class UserListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




# View to block or unblock a user (Admin-only access)
class BlockUnblockUserView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = not user.is_active  # Toggle active status
            user.save()
            return Response({'message': f'User has been {"unblocked" if user.is_active else "blocked"} successfully.'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)




class ProfileView(APIView):
    """
    Retrieve the profile of the logged-in user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        """
        Update the profile of the logged-in user
        """
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)  # Use partial=True for partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class ProfileUpdateView(APIView):
    """
    Update the profile of the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """
        Update the logged-in user's profile data.
        """
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)  # Use partial=True for partial updates
        
        if serializer.is_valid():
            # Handle the 'department_name' field if necessary
            department_name = request.data.get('department_name')
            if department_name:
                try:
                    department_instance = Department.objects.get(name=department_name)
                    user.department = department_instance
                except Department.DoesNotExist:
                    return Response({'detail': 'Department not found.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Save updated user profile
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class DepartmentListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        departments = Department.objects.all()
        department_data = [
            {'name': dept.name, 'employee_count': dept.customuser_set.count()}  # Assuming the reverse relation from CustomUser to Department
            for dept in departments
        ]
        return Response(department_data)





class DepartmentEmployeesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the logged-in manager
        manager = request.user

        # Ensure the user is a manager
        if not manager.is_manager:
            return Response({"error": "Only managers can view department employees."}, status=403)

        # Retrieve all employees in the same department as the manager
        employees = CustomUser.objects.filter(department=manager.department, designation='Employee')
        
        # Serialize the data including the department name
        serializer = EmployeeSerializer(employees, many=True)
        
        return Response(serializer.data)

