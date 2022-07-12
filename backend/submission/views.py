from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from rest_framework.compat import coreapi, coreschema
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.pagination import LimitOffsetPagination
from judge.tasks import do_judge_task

from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins

from .models import Submission, SubmissionResult
from .serializers import SubmissionSerializer, SubmissionResultSerializer
from .serializers import SubmissionPublicSerializer, SubmissionResultPublicSerializer
from .serializers import SubmissionPublicListSerializer
from user.permissions import GetOnlyPermission
from judge.judger_auth import IsJudger
from problem.models import Problem

import django.utils

import django.conf

class SubmissionViewSet(ReadOnlyModelViewSet):
    """
    获取提交信息
    """
    queryset = Submission.objects.all().order_by('-id')
    #serializer_class = SubmissionSerializer
    # TODO: 提交信息的查看权限问题
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (GetOnlyPermission,)
    filter_fields = ('id', 'user', "problem", "submit_time")

    def get_serializer_class(self):
        """
        Override parent code from rest_framework.generics.GenericAPIView
        to dynamically adjust the item to be used
        """
        if not hasattr(self.request, 'user'): # 生成文档用
            return SubmissionSerializer
        elif self.request.auth == "Judger" or self.request.user.is_superuser:
            if self.request.method == 'GET' and (not 'pk' in self.kwargs):
                # Check if we're querying a specific one
                # In list mode, the log and app_data is always hidden
                return SubmissionPublicListSerializer
            else:
                return SubmissionSerializer
        elif self.request.method == 'GET' and (not 'pk' in self.kwargs):
            # Check if we're querying a specific one
            # In list mode, the log and app_data is always hidden
            return SubmissionPublicListSerializer
        elif self.request.method == 'GET' and 'pk' in self.kwargs:
            # In retrieve mode
            user_id = self.request.user.id
            if user_id is None:
                return SubmissionPublicSerializer
            else:
                subm = Submission.objects.filter(id=self.kwargs['pk'])[0]
                if str(subm.user.id) != str(user_id):
                    return SubmissionPublicSerializer
                else:
                    return SubmissionSerializer
        else:
            assert(django.conf.settings.DEBUG == True)
            return SubmissionSerializer

# Read-only for users, allow to create for other users
class SubmissionResultViewSet(mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.ListModelMixin,
                              GenericViewSet):
    """
    Get submission result information
    """
    queryset = SubmissionResult.objects.all()
    #serializer_class = SubmissionResultSerializer
    # TODO: 提交信息的查看权限问题
    permission_classes = (GetOnlyPermission | IsJudger,)

    def get_serializer_class(self):
        """
        Override parent code from rest_framework.generics.GenericAPIView
        to dynamically adjust the item to be used
        """
        if not hasattr(self.request, 'user'): # 生成文档用
            return SubmissionResultSerializer
        elif self.request.auth == "Judger" or self.request.user.is_superuser:
            return SubmissionResultSerializer
        elif self.request.method == 'GET' and (not 'pk' in self.kwargs):
            # Check if we're querying a specific one
            # In list mode, the log and app_data is always hidden
            return SubmissionResultPublicSerializer
        elif self.request.method == 'GET' and 'pk' in self.kwargs:
            # In retrive mode
            user_id = self.request.user.id
            if user_id is None:
                return SubmissionResultPublicSerializer
            else:
                # Query to get the related submission, and user that it belongs to
                subm = SubmissionResult.objects.filter(id=self.kwargs['pk'])[0].submission
                if str(subm.user.id) != str(user_id):
                    return SubmissionResultPublicSerializer
                else:
                    return SubmissionResultSerializer
        else:
            assert(django.conf.settings.DEBUG == True)
            return SubmissionResultSerializer

class SubmitView(APIView):
    """
    提交
    """
    permission_classes = (IsAuthenticated,)
    schema = AutoSchema(manual_fields=[
        coreapi.Field(name='problem',
                      required=True,
                      location='form',
                      schema=coreschema.Integer(title='problem',
                                                description='要提交的题目ID')),
        coreapi.Field(name='submit_files',
                      required=True,
                      location='form',
                      schema=coreschema.Array(title='submit_files',
                                              items=coreschema.Integer,
                                              description='要提交的文件（代码等）')),
    ])

    def post(self, request, *args):
        # Fix bug: must check permission first
        self.check_permissions(request)

        # put the user segment in, ref: BaseSerializer docstring
        # Fix bug: AttributeError: This QueryDict instance is immutable
        # ref: https://stackoverflow.com/questions/44717442/this-querydict-instance-is-immutable
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = SubmissionSerializer(data=data)

        # print(request.data)
        # print(serializer.initial_data)
        try:
            serializer.is_valid(True)

            # (Optional) Checking for deadline time
            ddl = Problem.objects.filter(id=data['problem'])[0].deadline_time
            if ddl is not None and ddl < django.utils.timezone.now():
                # Whoops, you dare submitting it over ddl!
                return Response("You've submitted it after deadline! {}".format(str(ddl)),
                status.HTTP_400_BAD_REQUEST)

            subm = serializer.save()

            # Instantiate judge task for all testcases
            # Get all test cases related to this problem
            prob_id = serializer.data['problem']
            subm_id = subm.id
            # print("{} {}".format(prob_id, subm_id))
            prob = Problem.objects.filter(id=prob_id).first()
            if prob == None:
                return Response('No such problem', status.HTTP_404_NOT_FOUND)

            for case in prob.get_testcases():
                # Create a new SubmissionResult structure
                subm_res = SubmissionResult.objects.create(
                    status='PENDING',
                    submission=subm,
                    testcase=case,
                    grade=0,
                    log="",
                    app_data="",
                    possible_failure='NA'
                )

                do_judge_task.delay(
                    self.build_judge_detail(prob, case, subm, subm_res),
                    django.conf.settings.JUDGER_CONFIG
                )

            return Response(serializer._data, status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def build_judge_detail(self, prob, case, subm, subr):
        return {
            'id': subm.id,
            'problem': {
                'id': prob.id,
                'judge_files': [
                    i.id for i in prob.judge_files.all()
                ]
            },
            'submit_files': [
                i.id for i in subm.submit_files.all()
            ],
            'testcase': {
                'id': case.id,
                'testcase_files': [
                    i.id for i in case.testcase_files.all()
                ],
                'mem_limit': case.mem_limit,
                'time_limit': case.time_limit
            },
            'submission_result': {
                'id': subr.id
            }
        }
