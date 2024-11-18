from django.urls import path
from .views import LeaveApplicationCreateView, LeaveApplicationListView, ManagerLeaveApplicationListView,UpdateLeaveStatusView,RemainingLeaveDaysView,TotalLeavesReportView


urlpatterns = [
    path('create/', LeaveApplicationCreateView.as_view(), name='leave-application-create'),
    path('list/', LeaveApplicationListView.as_view(), name='leave-application-list'),
    path('manager/leave-requests/', ManagerLeaveApplicationListView.as_view(), name='manager-leave-list'),
    path('manager/update-leave/<int:pk>/', UpdateLeaveStatusView.as_view(), name='update-leave-status'),
    path('remaining-leaves/', RemainingLeaveDaysView.as_view(), name='remaining-leaves'),
    path('total-leaves-report/', TotalLeavesReportView.as_view(), name='total-leaves-report'),

    
]
