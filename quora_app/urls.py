from django.urls import path
from quora_app import views


app_name = 'questions'

urlpatterns = [
    path('questions/', views.questions, name='home'),
    path('ask_question/', views.ask_question, name='add_question'),
    path('question_answer_details/<int:question_id>', views.question_answer_details, name='answerdetails'),
    path('add_answer/<int:question_id>', views.add_answer, name='add_answer'),
    path('answer_vote/<int:answer_id>', views.answer_vote, name='answer_vote'),
]