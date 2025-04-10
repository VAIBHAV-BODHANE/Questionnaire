from django.db import models
from django.contrib.auth.models import User


class QuestionsAsked(models.Model):
    """User's questions table"""
    question = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_attachment = models.FileField(upload_to='questions/images', null=True, blank=True)
    tag=models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """string representation of user with their question"""
        return self.user.username + '-' + self.question
    
    def get_display_name(self):
        """return user full name"""
        return self.user.username


class QuestionsAnswered(models.Model):
    """User's answer to the question table"""
    answer = models.TextField()
    question = models.ForeignKey(QuestionsAsked, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    upvotecount = models.IntegerField(default=0)
    downvotecount = models.IntegerField(default=0)
    voteuser = models.ManyToManyField(User, through='AnswerVote', blank=True, related_name='voted_answers')
    answer_attachment = models.FileField(upload_to='answers/images', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """string representation of user with their answer"""
        return self.user.username + '-' + self.answer


class AnswerVote(models.Model):
    """Individual likes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey('QuestionsAnswered', on_delete=models.CASCADE)
    is_upvote = models.BooleanField(blank=True, null=True)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')