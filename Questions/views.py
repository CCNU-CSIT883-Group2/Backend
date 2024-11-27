import json
from datetime import timedelta

from django.db.models import Max, QuerySet
from django.http import JsonResponse
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
from ascal import gai, generator
from django.views import View

from Questions.models import (QuestionsModel,
                              HistoryModel, BlankQuestionModel, ChoiceQuestionModel,
                              HistorySerializer, QuestionSerializer, AttemptModel, AttemptSerializer)
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
        q_num = data.get('number')

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

        if q_type == 'multi':
            config = gai.TestConfig(gai.test_client.TestQuestionType.Choice)
            client = gai.Client(config)
            g = generator.ChoiceQuestionGenerator(
                subject, tag, generator.ChoiceType.Multi, client
            )
            questions.extend(g.generate(q_num))
        elif q_type == 'single':
            config = gai.TestConfig(gai.test_client.TestQuestionType.Choice)
            client = gai.Client(config)
            g = generator.ChoiceQuestionGenerator(
                subject, tag, generator.ChoiceType.Single, client
            )
            questions.extend(g.generate(q_num))
        else:
            config = gai.TestConfig(gai.test_client.TestQuestionType.Blank)
            client = gai.Client(config)
            g = generator.BlankQuestionGenerator(
                subject, tag, client
            )
            questions.extend(g.generate(q_num))

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

            if q_type == 'multi' or q_type == 'single':
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

        if q_type == 'multi' or q_type == 'single':
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
            {'code': 200, 'info': 'questions create successfully!',
             'data': {
                 'subject': subject,
                 'tag': tag,
                 'type': q_type,
                 'questions': [q.to_dict() for q in question_set],
                 'history': HistorySerializer(history, many=True).data,
                 'number': q_num,
             }}, status=200)

    else:
        return JsonResponse({'code': 400, 'msg': 'method is not POST'}, status=400)


def questions_search(request):
    data = json.loads(request.body)
    hid = data.get("history_id")
    questions = QuestionsModel.objects.filter(history_id=hid)

    questions_set = []
    for q in questions:
        if q.type == 'multi' or q.type == 'single':
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
                {'code': 200, 'info': 'ok',
                 'data': {
                     'content': content,
                     'option1': option1,
                     'option2': option2,
                     'option3': option3,
                     'option4': option4,
                     'answer': answer,
                     'explanation': explanation,
                     'difficulty': difficulty,
                     'time_require': time_require}
                 },
                status=200)
        else:
            content = question.content
            explanation = question.explanation
            difficulty = question.difficulty
            time_require = question.time_require
            bq = BlankQuestionModel.objects.get(QID=qid)
            answer = bq.correct_answers
            return JsonResponse(
                {'code': 200, 'info': 'ok',
                 'data': {
                     'content': content,
                     'answer': answer,
                     'explanation': explanation,
                     'difficulty': difficulty,
                     'time_require': time_require}
                 },
                status=200)
    else:
        return JsonResponse({'code': 400, 'info': 'method is not GET'}, status=400)


class HistoryView(View):

    @staticmethod
    def post(request):
        if not request.body:
            return JsonResponse({'code': 400, 'info': 'Request body is empty!'}, status=400)

        # data = json.loads(request.body)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'code': 400, 'info': 'Invalid JSON format!'}, status=400)

        print(request.body)
        print()

        # name = data.get('username')
        name = data.get('data', {}).get('username', None)
        print(f'name: {name}')
        hid = data.get('history_id')
        user = UserModel.objects.get(name=name)
        uid = user.UID
        if hid is None:
            history_list = HistoryModel.objects.filter(UID=uid).all()
            if not history_list:
                return JsonResponse({'code': 200, 'info': 'no history get!',
                                     'data': []
                                     }, status=200)
            else:
                return JsonResponse({'code': 200, 'info': 'get all history successfully!',
                                     'data': HistorySerializer(history_list, many=True).data}, status=200)
        else:
            history_list = HistoryModel.objects.filter(UID=uid, history_id=hid).all()
            if not history_list:
                return JsonResponse({'code': 200, 'info': 'no history get!',
                                     'data': []
                                     }, status=200)
            else:
                return JsonResponse({'code': 200, 'info': 'get history successfully!',
                                     'data': HistorySerializer(history_list, many=True).data}, status=200)

    @staticmethod
    def delete(request):
        data = json.loads(request.body)
        name = data.get('username')
        hid = data.get('history_id')
        user = UserModel.objects.get(name=name)
        uid = user.UID
        history_obj = HistoryModel.objects.filter(history_id=hid, UID=uid)
        if history_obj.exists():
            history_obj.delete()
            return JsonResponse({'code': 200, 'info': 'history delete successfully!'}, status=200)
        else:
            return JsonResponse({'code': 400, 'info': 'history delete fail, because history not exist!'}, status=400)


# def history_delete(request):
#     data = json.loads(request.body)
#     name = data.get('username')
#     hid = data.get('history_id')
#     user = UserModel.objects.get(name=name)
#     uid = user.UID
#     history_obj = HistoryModel.objects.filter(history_id=hid, UID=uid)
#     if history_obj.exists():
#         history_obj.delete()
#         return JsonResponse({'code': 200, 'info': 'history delete successfully!'}, status=200)
#     else:
#         return JsonResponse({'code': 400, 'info': 'history delete fail, because history not exist!'}, status=400)


# def history_get(request):
#     data = json.loads(request.body)
#     name = data.get('username')
#     hid = data.get('history_id')
#     user = UserModel.objects.get(name=name)
#     uid = user.UID
#     if hid is None:
#         history_list = HistoryModel.objects.filter(UID=uid).all()
#         return JsonResponse({'code': 200, 'info': 'get all history successfully!',
#                              'data': HistorySerializer(history_list, many=True).data}, status=200)
#     else:
#         history_list = HistoryModel.objects.filter(UID=uid, history_id=hid).all()
#         return JsonResponse({'code': 200, 'info': 'get history successfully!',
#                              'data': HistorySerializer(history_list, many=True).data}, status=200)

"""
    
"""
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

"""

"""


class AttemptView(View):

    @staticmethod
    def get(request):
        data = json.loads(request.body)
        name = data.get('username')
        hid = data.get('history_id')
        user = UserModel.objects.get(name=name)
        uid = user.UID
        if hid is not None:
            attempt = AttemptModel.objects.filter(UID=uid, history_id=hid)
            if attempt.exists():
                return JsonResponse({'code': 200, 'info': 'get attempt successfully!',
                                     'data': AttemptSerializer(attempt, many=True).data}, status=200)
            else:
                return JsonResponse({'code': 400, 'info': 'attempt not exist!'}, status=400)
        else:
            attempt = AttemptModel.objects.filter(UID=uid)
            if attempt.exists():
                return JsonResponse({'code': 200, 'info': 'get all attempt successfully!',
                                     'data': AttemptSerializer(attempt, many=True).data}, status=200)
            else:
                return JsonResponse({'code': 400, 'info': 'user not exist!'}, status=400)

    @staticmethod
    def post(request):
        # data receive
        data = json.loads(request.body)
        name = data.get('username')
        hid = data.get('history_id')
        qid = data.get('QID')
        tp = data.get('type')
        cans = data.get('choice_answers')
        bans = data.get('blank_answer')

        # data judge
        if tp == 'choice':
            cq = ChoiceQuestionModel.objects.get(QID=qid)
            refer_ans = cq.correct_answers  # get reference answers
            if set(cans) == set(refer_ans):
                is_correct = True
            else:
                is_correct = False
        else:
            bq = BlankQuestionModel.objects.get(QID=qid)
            refer_ans = bq.correct_answer  # get reference answers
            if set(bans) == set(refer_ans):
                is_correct = True
            else:
                is_correct = False
        # end data judge and get is_correct elem

        # attemp save
        user = UserModel.objects.get(name=name)
        uid = user.UID

        if AttemptModel.objects.filter(UID=uid, QID=qid, history_id=hid).exists() is False:
            # 新的attempt记录
            user_instance = UserModel.objects.get(UID=uid)
            question_instance = QuestionsModel.objects.get(QID=qid)
            history_instance = HistoryModel.objects.get(history_id=hid)
            if tp == 'choice':
                new_attempt = AttemptModel(
                    user_answers=cans,
                    is_correct=is_correct,
                    QID=question_instance,
                    UID=user_instance,
                    history_id=history_instance,
                )
                new_attempt.save()
            else:
                new_attempt = AttemptModel(
                    user_answer=bans,
                    is_correct=is_correct,
                    QID=question_instance,
                    UID=user_instance,
                    history_id=history_instance,
                )
                new_attempt.save()
            max_aid = AttemptModel.objects.aggregate(Max('attempt_id'))['attempt_id__max']
            attempt = AttemptModel.objects.get(attempt_id=max_aid)

            attempt_list = AttemptModel.objects.filter(history_id=hid)
            total = QuestionsModel.objects.filter(history_id=hid).count()
            done = attempt_list.filter(is_correct__isnull=False).count()
            progress = round(done / total, 2) if total > 0 else 0

            history = HistoryModel.objects.get(history_id=hid)
            history.progress = progress
            history.save()

            return JsonResponse({'code': 200, 'info': 'ok',
                                 'data': {
                                     'attempt': AttemptSerializer(attempt).data}
                                 },
                                status=200)
        else:
            # 更新已存在的attempt记录
            attempt = AttemptModel.objects.get(UID=uid, QID=qid, history_id=hid)
            if tp == 'choice':
                attempt.user_answers = cans
                attempt.is_corret = is_correct
                attempt.save()
            else:
                attempt.user_answer = bans
                attempt.is_corret = is_correct
                attempt.save()

            return JsonResponse({'code': 200, 'info': 'ok',
                                 'data': {
                                     'attempt': AttemptSerializer(attempt).data}
                                 },
                                status=200)
        # end attemp save


class StatisticsView(View):
    """
        指定用户，指定subject
        展示该科目某一周内正确率折线图
    """

    @staticmethod
    def get(request):
        data = json.loads(request.body)
        name = data.get('username')
        sbj = data.get('subject')
        user = UserModel.objects.get(name=name)
        uid = user.UID
        if sbj is not None:
            history_list = HistoryModel.objects.filter(UID=uid, subject=sbj)

            question_list = []  # 保存history_list中全部的question.

            # 获取符合要求的全部question实例，并把所有的实例都保存在question_list中。
            for history in history_list:
                hid = history.history_id
                questions = QuestionsModel.objects.filter(history_id=hid)
                for question in questions:
                    question_list.append(question)
            # end

            # 获取question_list中所有question的QID
            qid_list = []
            for question in question_list:
                qid_list.append(question.QID)
            # end

            # 默认获取最新做题时间的那一周的统计信息
            latest_time = AttemptModel.objects.filter(QID__in=qid_list) \
                .aggregate(latest_attempt_time=Max('attempt_time'))['latest_attempt_time']
            if latest_time:
                start_of_week = (latest_time - timedelta(days=latest_time.weekday())).date()  # 确定latest_time的所在周的开始时间
                end_of_week = (start_of_week + timedelta(days=6))  # 确定latest_time的所在周的结束时间

                attempts_in_week = AttemptModel.objects.filter(
                    # attempt_time__range=(start_of_week, end_of_week),
                    # QID__in=qid_list
                    attempt_time__date__gte=start_of_week,
                    attempt_time__date__lte=end_of_week,
                    QID__in=qid_list
                )

                # 记录每一天的统计数据
                daily_statistics = []
                questions_on_date = []  # 保存每天提交题目的QID
                for day_offset in range(7):  # 遍历这一周的每一天
                    current_date = start_of_week + timedelta(days=day_offset)
                    attempts_on_date = attempts_in_week.filter(attempt_time__date=current_date)

                    for attempt in attempts_on_date:
                        questions_on_date.append(attempt.QID_id)  # attempt中的QID实质上是个QuestionModel，这里应该用QID_id来获取真正的QID

                    total = attempts_on_date.count()
                    correct = attempts_on_date.filter(is_correct=True).count()
                    correct_rate = round(correct / total, 2) if total > 0 else 0

                    daily_statistics.append({
                        'date': current_date,
                        'total_attempts': total,
                        'correct_attempts': correct,
                        'correct_rate': correct_rate,
                        'questions_on_date': questions_on_date
                    })

                    questions_on_date = []

                return JsonResponse({'code': 200, 'info': 'get statistics successfully!',
                                     'data': {
                                         'latest_time': latest_time,
                                         'start_of_week': start_of_week,
                                         'end_of_week': end_of_week,
                                         'daily_statistics': daily_statistics}
                                     }, status=200)
            else:
                attempts_in_week = AttemptModel.objects.none()  # 没有数据时返回空查询集
                return JsonResponse({'code': 200, 'info': 'no latest attempt information',
                                     'data': {
                                         'history': HistorySerializer(history_list, many=True).data,
                                         'QIDs': qid_list,
                                         'attempts': AttemptSerializer(attempts_in_week, many=True).data}
                                     },
                                    status=200)
            # end

        else:
            history_list = HistoryModel.objects.filter(UID=uid)
            return JsonResponse({'code': 200, 'info': 'get statistics successfully!',
                                 'data': {
                                     'history': HistorySerializer(history_list, many=True).data}
                                 }, status=200)
