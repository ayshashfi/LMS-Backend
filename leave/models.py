from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import timedelta


class LeaveApplication(models.Model):
    # Choices for leave types
    LEAVE_TYPE_CHOICES = [
        ('Sick Leave', 'Sick Leave'),
        ('Annual Leave', 'Annual Leave'),
        ('Casual Leave', 'Casual Leave'),
    ]

    # Choices for leave status
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_applications")
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_leave_requests')

    def clean(self):
        # Ensure the start date is not after the end date
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be later than end date.")
    
    def __str__(self):
        # String representation to show user and leave type
        return f"{self.user.username} - {self.leave_type[:10]}... ({self.status})"

    def calculate_leave_days(self):
        """Calculate the number of valid leave days, excluding weekends (Sundays)."""
        current_date = self.start_date
        total_days = 0
        while current_date <= self.end_date:
            if current_date.weekday() != 6:  # Exclude Sundays (Sunday = 6)
                total_days += 1
            current_date += timedelta(days=1)
        return total_days


    def approve_leave(self):
        """Approve the leave and deduct the leave days from the user's balance."""
        if self.status != 'Pending':
            raise ValidationError("Leave application has already been processed.")
        
        leave_days = self.calculate_leave_days()

        # Log the current leave balance and calculated leave days
        print(f"User's leave balance: {self.user.leave_balance}")
        print(f"Calculated leave days: {leave_days}")

        if self.user.leave_balance >= leave_days:
            self.user.leave_balance -= leave_days  # Deduct leave balance
            self.user.save()  # Save the user after updating the balance
            self.status = 'Approved'
            self.save()
        else:
            raise ValidationError("Insufficient leave balance.")
