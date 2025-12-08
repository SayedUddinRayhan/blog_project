from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    ToggleLikeView,
    CreatePostView,
    EditPostView,
    DeletePostView,
    LoginView,
    LogoutView,
)

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/like/', ToggleLikeView.as_view(), name='toggle_like'),
    path('post/create/', CreatePostView.as_view(), name='create_post'),
    path('post/<int:pk>/edit/', EditPostView.as_view(), name='edit_post'),
    path('post/<int:pk>/delete/', DeletePostView.as_view(), name='delete_post'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
