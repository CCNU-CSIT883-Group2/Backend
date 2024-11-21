import json

from django.db.models import Max, QuerySet
from django.http import JsonResponse
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
from ascal import gai, generator
from Questions.models import (QuestionsModel,
                              HistoryModel, BlankQuestionModel, ChoiceQuestionModel,
                              HistorySerializer, QuestionSerializer)
from User.models import UserModel


# Create your views here.

def get_question(hid: str) -> QuerySet:
    questions = QuestionsModel.objects.filter(history_id=hid)
    return questions


class ChoiceQuestionDetail:
    def __init__(self, q: QuestionsModel):
        cq = ChoiceQuestionModel.objects.get(QID=q.QID)
        self.qid = q.QID
        self.content = q.content
        self.explanation = q.explanation
        self.difficulty = q.difficulty
        self.time_require = q.time_require
        self.note = q.note
        self.type = q.type
        # history_id is an object.
        self.history_id = q.history_id_id
        self.option1 = cq.option1
        self.option2 = cq.option2
        self.option3 = cq.option3
        self.option4 = cq.option4
        self.correct_answers = cq.correct_answers

    def to_dict(self):
        return {
            'qid': self.qid,
            'content': self.content,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'time_require': self.time_require,
            'note': self.note,
            'type': self.type,
            'history_id': self.history_id,
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3,
            'option4': self.option4,
            'correct_answers': self.correct_answers,
        }


class BlankQuestionDetail:
    def __init__(self, q: QuestionsModel):
        bq = BlankQuestionModel.objects.get(QID=q.QID)
        self.qid = q.QID
        self.content = q.content
        self.explanation = q.explanation
        self.difficulty = q.difficulty
        self.time_require = q.time_require
        self.note = q.note
        self.type = q.type
        # history_id is an object.
        self.history_id = q.history_id_id
        self.correct_answer = bq.correct_answer

    def to_dict(self):
        return {
            'qid': self.qid,
            'content': self.content,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'time_require': self.time_require,
            'note': self.note,
            'type': self.type,
            'history_id': self.history_id,
            'correct_answer': self.correct_answer,
        }


def questions_create(request):
    # 前端需要在body中提供 subject和 tag
    if request.method == 'POST':
        data = json.loads(request.body)
        uid = data.get('UID')
        subject = data.get('subject')
        tag = data.get('tag')
        q_type = data.get('type')

        ''' history '''

        user_instance = UserModel.objects.get(UID=uid)
        new_history = HistoryModel(
            subject=subject,
            tag=tag,
            UID=user_instance,
        )
        new_history.save()

        ''' questions '''

        questions = []

        if q_type == 'choice':
            config = gai.TestConfig(gai.test_client.TestQuestionType.Choice)
            client = gai.Client(config)
            g = generator.ChoiceQuestionGenerator(
                subject, tag, generator.ChoiceType.Multi, client
            )
            questions.extend(g.generate(3))
        else:
            config = gai.TestConfig(gai.test_client.TestQuestionType.Blank)
            client = gai.Client(config)
            g = generator.BlankQuestionGenerator(
                subject, tag, client
            )
            questions.extend(g.generate(3))

        history_id_instance = HistoryModel.objects.get(history_id=new_history.history_id)

        for question in questions:
            print(question.model_dump_json(indent=2))

            new_question = QuestionsModel(
                content=question.question,
                explanation=question.explanation,
                difficulty=question.difficulty,
                time_require=question.time_require,
                type=q_type,
                history_id=history_id_instance,
            )
            new_question.save()

            qid_instance = QuestionsModel.objects.get(QID=new_question.QID)

            if q_type == 'choice':
                new_choice = ChoiceQuestionModel(
                    option1=question.options[0],
                    option2=question.options[1],
                    option3=question.options[2],
                    option4=question.options[3],
                    correct_answers=question.answer,
                    QID=qid_instance,
                )
                new_choice.save()
            else:
                new_choice = BlankQuestionModel(
                    correct_answer=question.answer,
                    QID=qid_instance,
                )
                new_choice.save()

        # question_list = QuestionsModel.objects.all()

        max_hid = HistoryModel.objects.aggregate(Max('history_id'))['history_id__max']
        history = HistoryModel.objects.filter(history_id=max_hid)
        questions = QuestionsModel.objects.filter(history_id=max_hid)

        question_set = []

        if q_type == 'choice':
            for question in questions:
                question_set.append(ChoiceQuestionDetail(question))
        else:
            for question in questions:
                question_set.append(BlankQuestionDetail(question))

        for q in question_set:
            print(q.to_dict())

        # question_json_list = [q.model_dump_json() for q in questions]
        # questions_json = f"[{','.join(question_json_list)}]"
        # questions = json.loads(questions_json)

        # questions_json = serializers.serialize('json', questions)
        # questions_data = json.loads(questions_json)

        # return JsonResponse(
        #     {'code': 200, 'subject': subject, 'tag': tag, 'type': q_type,
        #      'data': QuestionSerializer(questions, many=True).data},
        #     status=200)

        return JsonResponse(
            {'code': 200, 'subject': subject, 'tag': tag, 'type': q_type,
             # 'questions': QuestionSerializer(questions, many=True).data,
             'questions': [q.to_dict() for q in question_set],
             'history': HistorySerializer(history, many=True).data}, status=200)

    else:
        return JsonResponse({'code': 400, 'msg': 'method is not POST'}, status=400)


def questions_search(request):
    data = json.loads(request.body)
    hid = data.get("history_id")
    questions = QuestionsModel.objects.filter(history_id=hid)

    questions_set = []
    for q in questions:
        if q.type == 'choice':
            questions_set.append(ChoiceQuestionDetail(q))
        else:
            questions_set.append(BlankQuestionDetail(q))

    for question in questions_set:
        print(question.to_dict())

    return JsonResponse({'code': 200, 'info': 'ok',
                         'data': [q.to_dict() for q in questions_set]}, status=200)


# def questions_get(request):
#     if request.method == 'GET':
#         config = gai.TestConfig()
#         client = gai.Client(config)
#
#         g = generator.ChoiceQuestionGenerator(
#             "English", "noun", generator.ChoiceType.Multi, client
#         )
#         questions = list(g.generate(10))
#         ls = list(map(lambda x: x.dict(), questions))
#         for question in questions:
#             print(question.model_dump_json(indent=2))
#             new_question = QuestionsModel(
#
#             )
#         return JsonResponse({'code': 200, 'info': ls})
#     else:
#         return JsonResponse({'code': 400, 'info': 'false'})


def questions_answer(request):
    # 前端需要提供 QID
    if request.method == 'GET':
        data = json.loads(request.body)
        qid = data.get('QID')
        question = QuestionsModel.objects.get(pk=qid)
        # answer = QuestionSerializer(question).data.get('a_options')
        # explanation = QuestionSerializer(question).data.get('explanation')
        if question.type == 'choice':
            content = question.content
            explanation = question.explanation
            difficulty = question.difficulty
            time_require = question.time_require
            cq = ChoiceQuestionModel.objects.get(QID=qid)
            option1 = cq.option1
            option2 = cq.option2
            option3 = cq.option3
            option4 = cq.option4
            answer = cq.correct_answers
            return JsonResponse(
                {'code': 200, 'info': 'ok', 'content': content, 'option1': option1, 'option2': option2,
                 'option3': option3, 'option4': option4, 'answer': answer, 'explanation': explanation,
                 'difficulty': difficulty, 'time_require': time_require}, status=200)
        else:
            content = question.content
            explanation = question.explanation
            difficulty = question.difficulty
            time_require = question.time_require
            bq = BlankQuestionModel.objects.get(QID=qid)
            answer = bq.correct_answers
            return JsonResponse(
                {'code': 200, 'info': 'ok', 'content': content, 'answer': answer, 'explanation': explanation,
                 'difficulty': difficulty, 'time_require': time_require}, status=200)
    else:
        return JsonResponse({'code': 400, 'info': 'method is not GET'}, status=400)


def history_delete(request):
    data = json.loads(request.body)
    name = data.get('usersname')
    hid = data.get('history_id')
    user = UserModel.objects.get(name=name)
    uid = user.UID
    history_obj = HistoryModel.objects.filter(history_id=hid, UID=uid)
    if history_obj.exists():
        history_obj.delete()
        return JsonResponse({'code': 200, 'info': 'history delete successfully!'}, status=200)
    else:
        return JsonResponse({'code': 400, 'info': 'history delete fail, because history not exist!'}, status=400)


def history_get(request):
    data = json.loads(request.body)
    name = data.get('username')
    hid = data.get('history_id')
    user = UserModel.objects.get(name=name)
    uid = user.UID
    if hid is None:
        history_list = HistoryModel.objects.filter(UID=uid).all()
        return JsonResponse({'code': 200, 'info': 'get all history successfully!',
                             'data': HistorySerializer(history_list, many=True).data}, status=200)
    else:
        history_list = HistoryModel.objects.filter(UID=uid, history_id=hid).all()
        return JsonResponse({'code': 200, 'info': 'get history successfully!',
                             'data': HistorySerializer(history_list, many=True).data}, status=200)
# @method_decorator(csrf_exempt, name='dispatch')
# class QuestionsView(View):

# @staticmethod
# def create(request):
#
#     return JsonResponse({'message': 'Question created'}, status=201)
#
# @staticmethod
# def post(request):
#     print(request.path.split('/')[-1])
#     action = request.path.split('/')[-1]
#
#     if action == 'create':
#         return QuestionsView.create(request)
#     else:
#         return JsonResponse({'code': 200, 'info': 'This is in post method'})

# @staticmethod
# def get(request):
#     config = gai.TestConfig()
#     client = gai.Client(config)
#
#     g = generator.ChoiceQuestionGenerator(
#         "English", "noun", generator.ChoiceType.Multi, client
#     )
#     questions = list(g.generate(10))
#     ls = list(map(lambda x: x.dict(), questions))
#     for question in questions:
#         print(question.model_dump_json(indent=2))
#         new_question = QuestionsModel(
#
#         )
#     return JsonResponse({'code': 200, 'info': ls})
