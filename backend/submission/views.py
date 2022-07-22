from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from rest_framework.compat import coreapi, coreschema
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.pagination import LimitOffsetPagination

from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins

from .models import Submission, SubmissionResult, File
from .serializers import SubmissionSerializer, SubmissionResultSerializer
from .serializers import SubmissionPublicSerializer, SubmissionResultPublicSerializer
from .serializers import SubmissionPublicListSerializer
from user.permissions import GetOnlyPermission
from problem.models import Problem, SignalName



import django.utils
import django.conf
from django.conf import settings


import requests  # https://requests.readthedocs.io/en/latest/
import json
import os

from typing import List


class SubmissionViewSet(ReadOnlyModelViewSet):
    """
    获取提交信息
    """

    queryset = Submission.objects.all().order_by("-id")
    # serializer_class = SubmissionSerializer
    # TODO: 提交信息的查看权限问题
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (GetOnlyPermission,)
    filter_fields = ("id", "user", "problem", "submit_time")

    def get_serializer_class(self):
        """
        Override parent code from rest_framework.generics.GenericAPIView
        to dynamically adjust the item to be used
        """
        if not hasattr(self.request, "user"):  # 生成文档用
            return SubmissionSerializer
        elif self.request.user.is_superuser:
            if self.request.method == "GET" and (not "pk" in self.kwargs):
                # Check if we're querying a specific one
                # In list mode, the log and app_data is always hidden
                return SubmissionPublicListSerializer
            else:
                return SubmissionSerializer
        elif self.request.method == "GET" and (not "pk" in self.kwargs):
            # Check if we're querying a specific one
            # In list mode, the log and app_data is always hidden
            return SubmissionPublicListSerializer
        elif self.request.method == "GET" and "pk" in self.kwargs:
            # In retrieve mode
            user_id = self.request.user.id
            if user_id is None:
                return SubmissionPublicSerializer
            else:
                subm = Submission.objects.filter(id=self.kwargs["pk"])[0]
                if str(subm.user.id) != str(user_id):
                    return SubmissionPublicSerializer
                else:
                    return SubmissionSerializer
        else:
            assert django.conf.settings.DEBUG == True
            return SubmissionSerializer


# Read-only for users, allow to create for other users
class SubmissionResultViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    Get submission result information
    """

    queryset = SubmissionResult.objects.all()
    # serializer_class = SubmissionResultSerializer
    # TODO: 提交信息的查看权限问题
    permission_classes = (GetOnlyPermission,)

    def get_serializer_class(self):
        """
        Override parent code from rest_framework.generics.GenericAPIView
        to dynamically adjust the item to be used
        """
        if not hasattr(self.request, "user"):  # 生成文档用
            return SubmissionResultSerializer
        elif self.request.user.is_superuser:
            return SubmissionResultSerializer
        elif self.request.method == "GET" and (not "pk" in self.kwargs):
            # Check if we're querying a specific one
            # In list mode, the log and app_data is always hidden
            return SubmissionResultPublicSerializer
        elif self.request.method == "GET" and "pk" in self.kwargs:
            # In retrive mode
            user_id = self.request.user.id
            if user_id is None:
                return SubmissionResultPublicSerializer
            else:
                # Query to get the related submission, and user that it belongs to
                subm = SubmissionResult.objects.filter(id=self.kwargs["pk"])[
                    0
                ].submission
                if str(subm.user.id) != str(user_id):
                    return SubmissionResultPublicSerializer
                else:
                    return SubmissionResultSerializer
        else:
            assert django.conf.settings.DEBUG == True
            return SubmissionResultSerializer


class SubmitView(APIView):
    """
    提交
    """

    permission_classes = (IsAuthenticated,)
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(
                name="problem",
                required=True,
                location="form",
                schema=coreschema.Integer(title="problem", description="要提交的题目ID"),
            ),
            coreapi.Field(
                name="submit_file",
                required=True,
                location="form",
                schema=coreschema.Integer(
                    title="submit_file",
                    description="学生编写的Verilog文件的ID 要求前端先上传文件",
                ),
            ),
        ]
    )

    def post(self, request, *args):
        print("[DEBUG] submission.SubmitView.post 开始处理")
        # Fix bug: must check permission first
        self.check_permissions(request)

        # put the user segment in, ref: BaseSerializer docstring
        # Fix bug: AttributeError: This QueryDict instance is immutable
        # ref: https://stackoverflow.com/questions/44717442/this-querydict-instance-is-immutable
        data = request.data.copy()
        data["user"] = request.user.id # 这里增加了一个user域
        print(f"[DEBUG] data {data}")
        serializer = SubmissionSerializer(data=data)

        # print(request.data)
        # print(serializer.initial_data)
        try:
            print("[DEBUG] 进入try块")
            serializer.is_valid(True)
            print("[DEBUG] 数据验证成功")

            # (Optional) Checking for deadline time
            ddl = Problem.objects.filter(id=data["problem"])[0].deadline_time
            if ddl is not None and ddl < django.utils.timezone.now():
                # Whoops, you dare submitting it over ddl!
                return Response(
                    "You've submitted it after deadline! {}".format(str(ddl)),
                    status.HTTP_400_BAD_REQUEST,
                )
            print("[DEBUG] 183")

            subm = serializer.save() # 存入数据库 这时`subm`为已经在数据库中的对象
            print("[DEBUG] 186")
            print(f"[DEBUG] serializer.data {serializer.data}")
            # Instantiate judge task for all testcases
            # Get all test cases related to this problem
            prob_id = serializer.data["problem"]
            code_student_file_id = serializer.data["submit_file"]
            subm_id = subm.id
            print("[DEBUG] prob_id {} subm_id {}".format(prob_id, subm_id))

            prob: Problem = Problem.objects.filter(id=prob_id).first()
            code_student_file: File = File.objects.filter(id=code_student_file_id).first()
            print("[DEBUG] 取数据完成")
            if prob == None:
                return Response("No such problem", status.HTTP_404_NOT_FOUND)
            # 对于每一个测试点
            for case in prob.get_testcases():
                print("[DEBUG] 进入一个测试点")
                # [取出要判的题目相关的文件转为字符串]
                # 需要的文件
                # - 标准答案
                # - 学生的代码
                # - testbench
                
                print(f"[DEBUG] 211 code_student_file.file.path {code_student_file.file.path}")
                with open(code_student_file.file.path, "r") as f:
                    code_student: str = f.read()
                print("[DEBUG] 213")
                with open(prob.code_reference_file.file.path, "r") as f:
                    code_reference: str = f.read()
                print("[DEBUG] 217")
                with open(case.testbench_file.file.path, "r") as f:
                    testbench: str = f.read()

                # 需要的信息
                # - 顶层模块名称
                # - 信号名称
                top_module: str = prob.top_module
                print(f"[DEBUG] {SignalName.objects.filter(problem=prob)}")
                signal_names: List(str) = [signal.name for signal in SignalName.objects.filter(problem=prob)] # TODO 把这里转一下 从对应的signal_names中取出
                print(f"[DEBUG] 227 top_module {top_module} signal_names {signal_names}")

                # [生成判题服务的请求]

                request_data = {
                    "code_reference": code_reference,
                    "code_student": code_student,
                    "testbench": testbench,
                    "top_module": top_module,
                    "signal_names": signal_names,
                }
                print(f"[DEBUG] request_data {request_data}")
                url = "http://166.111.223.67:1234"

                # [调用后端判题服务上传这些文件]

                print("[request started]")
                response_origin = requests.post(url=url, data=json.dumps(request_data),headers={"Host": "verilogojservices.judger"})

                # [等待后端判题服务返回结果]

                print("[request ended]")
                print(f"[status_code] {response_origin.status_code}")
                response = json.loads(response_origin.content)

                # [将判题结果写回数据库]

                if response_origin.status_code == 200:  # 判题成功结束
                    print(f"[successed]")
                    print(f'[log] {response["log"]}')
                    if response["is_correct"]:
                        SubmissionResult.objects.create(  # TODO 这个create真的create了吗？
                            status="DONE",
                            submission=subm,  # 一个提交结果唯一对应学生的一次提交
                            testcase=case,  # 一个提交结果唯一对应题目的一个testcase
                            grade=10,  # 判题结束后 学生答对则10分 答错则0分
                            log=response["log"],
                            app_data=response["wavejson"],
                            possible_failure="NONE",
                        ).save()
                    else:
                        SubmissionResult.objects.create(  # TODO 这个create真的create了吗？
                            status="DONE",
                            submission=subm,
                            testcase=case,
                            grade=0,
                            log=response["log"],
                            app_data=response["wavejson"],
                            possible_failure="WA",
                        ).save()
                    return Response(serializer._data, status.HTTP_201_CREATED)
                elif response_origin.status_code == 400:  # 判题过程中出错
                    print(f"[failed]")
                    print(f'[error] {response["error"]}')
                    print(f'[log] {response["log"]}')
                    SubmissionResult.objects.create(  # TODO 这个create真的create了吗？
                        status="DONE",
                        submission=subm,
                        testcase=case,
                        grade=0,
                        log=response["log"] + response["error"],
                        app_data="",
                        possible_failure="CE",
                    ).save()
                elif response_origin.status_code == 422:
                    return Response(
                        "Validation Error" + response_origin.content,
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                    )
                else:
                    return Response("判题服务出错", status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
