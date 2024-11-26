from Home.views import (
    home,
    LoginView, RegisterView, user_logout, ProfileView
)
from Questions.views import (questions_create, questions_answer, questions_search, HistoryView, AttemptView,
                             StatisticsView)
from django.urls import path

urlpatterns = [
    path('', home, name='home'),

    # User URL
    path('login', LoginView.as_view(), name='login'),

    path('logout', user_logout, name='logout'),

    path('register', RegisterView.as_view(), name='register'),

    path('profile', ProfileView.as_view(), name='profile'),

    # Question URL
    path('questions/create', questions_create, name='questions_create'),

    path('questions/answer', questions_answer, name='questions_answer'),

    path('questions', questions_search, name='questions_search'),

    path('history', HistoryView.as_view(), name='history'),

    path('attempt', AttemptView.as_view(), name='attemp'),

    path('statistics', StatisticsView.as_view(), name='statistics'),

]
