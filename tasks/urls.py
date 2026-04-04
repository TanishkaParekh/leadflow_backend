from django.urls import path
from .views import TaskViewSet

task_list = TaskViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

task_detail = TaskViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

task_complete = TaskViewSet.as_view({
    'patch': 'mark_complete'
})

urlpatterns = [
    path('', task_list, name='task-list'),
    path('<int:pk>/', task_detail, name='task-detail'),
    path('<int:pk>/complete/', task_complete, name='task-complete'),
]