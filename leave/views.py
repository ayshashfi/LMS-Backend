from rest_framework import generics, permissions
from .models import LeaveApplication
from .serializers import LeaveApplicationSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.exceptions import ValidationError
from accounts.models import CustomUser
from django.db.models import  Q
from rest_framework.permissions import IsAuthenticated




class LeaveApplicationCreateView(generics.CreateAPIView):
    queryset = LeaveApplication.objects.all()
    serializer_class = LeaveApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        department = user.department

        if not department:
            raise ValidationError({"department": "Your department is not assigned."})
        
        # Find a manager in the same department
        manager = CustomUser.objects.filter(department=department, is_manager=True).first()
        if not manager:
            raise ValidationError({"manager": "No manager found in your department."})

        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        # Check for overlapping leave periods
        overlapping_leaves = LeaveApplication.objects.filter(
            Q(user=user) & 
            (
                Q(start_date__lte=end_date, end_date__gte=start_date)
            )
        )
        
        if overlapping_leaves.exists():
            raise ValidationError({"dates": "You already have an overlapping leave application for the selected dates."})

        # Save the leave application
        serializer.save(user=user, manager=manager)





class LeaveApplicationListView(generics.ListAPIView):
    serializer_class = LeaveApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = LeaveApplication.objects.filter(user=self.request.user)
        if not queryset.exists():
            logger.info(f"No leave applications found for user {self.request.user.username}")

        return queryset




import logging

logger = logging.getLogger(__name__)

class ManagerLeaveApplicationListView(generics.ListAPIView):
    serializer_class = LeaveApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        logger.info(f"Authenticated user: {user.username}")
        
        if not user.is_manager:
            logger.warning(f"User {user.username} tried to access manager-only resource.")
            raise PermissionDenied("You do not have permission to view this resource.")
        
        # Only allow managers to see leave applications of their department and pending status
        queryset = LeaveApplication.objects.filter(
            manager=user, 
            user__department=user.department, 
            status='Pending'
        )
        
        if not queryset.exists():
            logger.info(f"No pending leave applications found for manager {user.username} in their department.")
        
        return queryset




class UpdateLeaveStatusView(UpdateAPIView):
    queryset = LeaveApplication.objects.all()
    serializer_class = LeaveApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        leave_application = self.get_object()

        # Ensure only the manager of the employee and in the same department can update
        if leave_application.manager != self.request.user or leave_application.user.department != self.request.user.department:
            logger.warning(f"Unauthorized update attempt by {self.request.user.username} on leave application ID {leave_application.id}")
            raise PermissionDenied("You do not have permission to update this leave request.")
        
        # Validate the status
        status = self.request.data.get('status')
        if status not in ['Approved', 'Rejected']:
            raise ValidationError("Invalid status. Allowed values are 'Approved' or 'Rejected'.")
        
        # Save the updated status
        logger.info(f"Leave application ID {leave_application.id} status updated to {status} by manager {self.request.user.username}")
        serializer.save(status=status)






class RemainingLeaveDaysView(APIView):
    """
    API endpoint to fetch the remaining leave days for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Default total leave days for the user
        total_leave_days = 30  

        # Calculate used leave days
        leave_applications = LeaveApplication.objects.filter(
            user=user, 
            status='Approved'
        )
        used_leave_days = sum(
            (leave.end_date - leave.start_date).days + 1 for leave in leave_applications
        )

        # Calculate remaining leave days
        remaining_leave_days = total_leave_days - used_leave_days

        return Response({
            "remaining_leave_days": remaining_leave_days
        })



class TotalLeavesReportView(APIView):
    """
    API View to generate a total leaves report for employees in a manager's department.
    Only the manager can view the leave data for their department's employees.
    """
    permission_classes = [IsAuthenticated]

    def get_leave_report(self, manager):
        """
        This method fetches leave data for employees in the manager's department,
        including total leave days for each employee, grouped by leave type and status.
        """
        department_employees = CustomUser.objects.filter(department=manager.department)
        
        # Filter leave applications for employees in the manager's department
        leave_report = LeaveApplication.objects.filter(user__in=department_employees) \
            .values('user__username', 'leave_type', 'status', 'start_date', 'end_date') \
            .order_by('user__username', 'leave_type', 'status')

        return leave_report

    def get(self, request, *args, **kwargs):
        manager = request.user  # The logged-in user (manager)
        
        if not manager.is_manager:
            return Response({"error": "You are not authorized to view this report."}, status=403)
        
        leave_report = self.get_leave_report(manager)

        # Calculate leave days for each leave application dynamically
        report_data = []
        for entry in leave_report:
            leave_application = LeaveApplication.objects.get(
                user__username=entry['user__username'], 
                leave_type=entry['leave_type'], 
                status=entry['status'],
                start_date=entry['start_date'],  # Ensure the correct instance is fetched
                end_date=entry['end_date']
            )
            # Dynamically calculate the leave days
            leave_days = leave_application.calculate_leave_days()
            entry['total_leave_days'] = leave_days
            report_data.append(entry)
        
        return Response(report_data)
