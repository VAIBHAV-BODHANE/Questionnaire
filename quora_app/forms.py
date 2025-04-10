from django import forms
from quora_app.models import QuestionsAsked, QuestionsAnswered


class AddQuestion(forms.ModelForm):
    
    class Meta:
        model=QuestionsAsked
        fields=['question', 'tag', 'question_attachment']


class AddAnswer(forms.ModelForm):

    class Meta:
        model=QuestionsAnswered
        fields=['answer', 'question', 'answer_attachment']