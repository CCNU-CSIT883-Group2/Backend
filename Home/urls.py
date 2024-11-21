from Home.views import (
    home,
    LoginView, RegisterView, user_logout, ProfileView
)
from Questions.views import questions_create, questions_answer, history_delete, history_get, questions_search
from django.urls import path

urlpatterns = [
    path('', home, name='home'),

    path('login', LoginView.as_view(), name='login'),

    path('logout', user_logout, name='logout'),

    path('register', RegisterView.as_view(), name='register'),

    path('profile', ProfileView.as_view(), name='profile'),

    path('questions/create', questions_create, name='questions_create'),

    path('questions/answer', questions_answer, name='questions_answer'),

    path('history_delete', history_delete, name='history_delete'),

    path('history_get', history_get, name='history_get'),

    path('questions', questions_search, name='questions_search'),
]
