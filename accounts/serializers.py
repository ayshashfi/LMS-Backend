from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Department
from rest_framework import serializers
from .models import CustomUser, Department


CustomUser = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    department = serializers.CharField()
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'department', 'manager', 'designation', 'department_name']
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is not returned in response
        }

    def validate_department(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")
        try:
            department = Department.objects.get(name=value)
        except Department.DoesNotExist:
            raise serializers.ValidationError(f"Department '{value}' does not exist.")
        return department.id

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def create(self, validated_data):
        department_id = validated_data.pop('department')
        validated_data['department'] = Department.objects.get(id=department_id)
        
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)

        # Set the user designation logic
        designation = validated_data.get('designation', '').lower()
        if designation == 'manager':
            user.is_manager = True
            user.is_employee = False
        else:  # Assuming anything other than 'manager' is an employee
            user.is_manager = False
            user.is_employee = True

        user.set_password(password)  # Hash the password
        user.save()
        return user




# User Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)



# User Serializer (for listing)
class UserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    is_admin = serializers.SerializerMethodField()

    def get_is_admin(self, obj):
        return obj.is_staff 

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'designation', 'phone_number','is_active', 'is_admin', 'department', 'manager','department_name']




class EmployeeSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'designation', 'department']
