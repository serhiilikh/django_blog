from django.urls import path, include
from .views import post_detail, post_list, signup, create_post, wait_for_email, registration_success
from django.contrib.auth import views
from django.urls import path


urlpatterns = [
    path('', post_list, name='posts'),
    path('<int:post_id>/', post_detail, name='post_detail'),
    path('signup/', signup, name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('create_post/', create_post, name='create_post'),
    path('wait_for_email/', wait_for_email, name='wait_for_email'),
    path('registration_succesfull/', registration_success, name='registration_success'),
]
