import uuid

from django.db import models
from rest_framework import serializers


# Create your models here.

# User Model is used to manage all the users.
class UserModel(models.Model):
    # UID is used to uniquely identify each user.
    UID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # name records the user's custom name.
    name = models.CharField(max_length=32, unique=True, default='')
    # user's login password.
    password = models.CharField(max_length=32)
    # user's contact email.
    email = models.EmailField(unique=True)
    # user's identity (only student or teacher)
    role = models.CharField(max_length=10, null=False, default='')

    class Meta:
        db_table = 'Users'
        constraints = [
            models.CheckConstraint(
                check=models.Q(role__in=['teacher', 'student']),
                name='Users_role_check'
            )
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'

# # UserBank is used to record the questions that the user has bookmarked.
# class UserBankModel(models.Model):
#     from Questions.models import QuestionsModel
#     # UID is used to uniquely identify each user.
#     UID = models.OneToOneField('User.UserModel', on_delete=models.CASCADE, db_column='UID', primary_key=True)
#     # QID is used to uniquely identify each question.
#     QID = models.ForeignKey('Questions.QuestionsModel', on_delete=models.CASCADE, db_column='QID')
#     # is_deleted is used to conduct logical deletion.
#     is_deleted = models.BooleanField(default=False)
#
#     class Meta:
#         # UID and QID can uniquely mark a table item.
#         unique_together = ('UID', 'QID')
#         db_table = 'UserBank'


# UserView Model is used to record some statistical information about the user.
# class UserViewModel(models.Model):
#     from Questions.models import QuestionsModel
#     # UID is used to uniquely identify each user.
#     UID = models.OneToOneField('User.UserModel', on_delete=models.CASCADE, db_column='UID', primary_key=True)
#     # QID is used to uniquely identify each question.
#     QID = models.ForeignKey('Questions.QuestionsModel', on_delete=models.CASCADE, db_column='QID')
#     # is_answerd is used to record whether the question has been attempted and whether it was answered correctly or not.
#     is_answered = models.BooleanField(null=True, blank=True, default=None)
#
#     class Meta:
#         unique_together = ('UID', 'QID')
#         db_table = 'UserView'
