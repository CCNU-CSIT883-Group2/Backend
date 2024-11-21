from django.db import models
from rest_framework import serializers


# Create your models here.

class HistoryModel(models.Model):
    history_id = models.AutoField(primary_key=True)
    #
    UID = models.ForeignKey('User.UserModel', on_delete=models.CASCADE, db_column='UID')
    #
    create_time = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=32)
    tag = models.CharField(max_length=32)
    # When user saves or submits the quizes, update this field
    progress = models.FloatField(default=0)

    class Meta:
        db_table = 'History'


# class HistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = HistoryModel
#         fields = '__all__'

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoryModel
        fields = ['history_id', 'UID', 'create_time', 'subject', 'tag', 'progress']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # 将 create_time 转换为整数时间戳
        representation['create_time'] = int(instance.create_time.timestamp())
        return representation


# # Questions Model is used to manage all the questions.
# class QuestionsModel(models.Model):
#     # QID is used to uniquely identify each question.
#     QID = models.AutoField(primary_key=True, unique=True, editable=False)
#     # SID is used to record different questions set.
#     SID = models.PositiveIntegerField(default=0)
#     # subject is used to mark which subject each question belongs to.
#     subject = models.CharField(max_length=30)
#     # tag is used to record the section of the subject that each question belongs to.
#     tag = models.CharField(max_length=120)
#     # question is used to record the content of a question.
#     question = models.CharField(max_length=500)
#     # q_options are used to record the options of a question.
#     q_options = models.CharField(max_length=500)
#     # explanation is used to record the answer explanation information.
#     explanation = models.CharField(max_length=500)
#     # q_options are used to record the options of the answers.
#     a_options = models.CharField(max_length=500, null=True, blank=True)
#     # difficulty is used to show the correct rate of a question.
#     difficulty = models.FloatField(default=0.0)
#     # time is used to mark the time of issue generation.
#     time = models.DateTimeField(auto_now_add=True, null=True)
#
#     class Meta:
#         db_table = 'Questions'

class QuestionsModel(models.Model):
    QID = models.AutoField(primary_key=True)
    history_id = models.ForeignKey('Questions.HistoryModel', on_delete=models.CASCADE, db_column='history_id')
    content = models.TextField()
    explanation = models.TextField()
    difficulty = models.IntegerField()
    time_require = models.IntegerField()
    note = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=10, null=False, default='')

    class Meta:
        db_table = 'Questions'
        constraints = [
            models.CheckConstraint(
                check=models.Q(type__in=['choice', 'blank']),
                name='Questions_type_check'
            )
        ]


class ChoiceQuestionModel(models.Model):
    QID = models.OneToOneField(
        'Questions.QuestionsModel', on_delete=models.CASCADE, primary_key=True, db_column='QID'
    )
    option1 = models.TextField()
    option2 = models.TextField()
    option3 = models.TextField()
    option4 = models.TextField()
    correct_answers = models.JSONField()

    class Meta:
        db_table = 'ChoiceQuestion'


class BlankQuestionModel(models.Model):
    QID = models.OneToOneField(
        'Questions.QuestionsModel', on_delete=models.CASCADE, primary_key=True, db_column='QID'
    )
    correct_answer = models.TextField()

    class Meta:
        db_table = 'BlankQuestion'


class AttemptModel(models.Model):
    attempt_id = models.AutoField(primary_key=True)
    QID = models.ForeignKey('Questions.QuestionsModel', on_delete=models.CASCADE, db_column='QID')
    history_id = models.ForeignKey('Questions.HistoryModel', on_delete=models.CASCADE, db_column='history_id')
    UID = models.ForeignKey('User.UserModel', on_delete=models.CASCADE, db_column='UID')
    attempt_time = models.DateTimeField(auto_now_add=True)
    user_answers = models.JSONField(null=True, blank=True)  # For ChoiceQuestion
    user_answer = models.TextField(null=True, blank=True)  # For BlankQuestion
    is_correct = models.BooleanField()

    class Meta:
        db_table = 'Attempt'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionsModel
        fields = '__all__'

# # Question History Model can store questions that have been generated in the past.
# class QuestionsHistoryModel(models.Model):
#     from User.models import UserModel
#     # UID is used to uniquely identify each user.
#     UID = models.ForeignKey('User.UserModel', on_delete=models.CASCADE, db_column='UID')
#     # QID is used to uniquely identify each question.
#     QID = models.ForeignKey('Questions.QuestionsModel', on_delete=models.PROTECT, db_column='QID')
#
#     class Meta:
#         # UID and SID can uniquely mark a table item.
#         unique_together = ('UID', 'SID')
#         db_table = 'QuestionsHistory'
