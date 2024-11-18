from rest_framework import serializers
from .models import LeaveApplication

class LeaveApplicationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  
    manager = serializers.StringRelatedField(read_only=True)  

    class Meta:
        model = LeaveApplication
        fields = ['id', 'username', 'leave_type', 'start_date', 'end_date', 'reason', 'status', 'created_at', 'manager']
        read_only_fields = ['id', 'status', 'created_at', 'user', 'manager']  #