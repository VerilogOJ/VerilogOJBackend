from django.db import models
from user.models import User
from file.models import File
from django.db.models import F

DEFAULT_USER_ID = 1

class SignalName(models.Model):
    """
    信号名称 一个Problem可以有多个信号名称
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20,help_text='信号名称')

class Problem(models.Model):
    # [题目属性-自动生成]
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(auto_now_add=True, help_text='题目的创建时间')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='题目创建者',
        default=DEFAULT_USER_ID # 默认管理员添加
    )
    
    # [题目描述]
    logic_id = models.IntegerField(null=True, help_text='学生看到的题目ID')
    name = models.CharField(max_length=20, help_text='题目名称')
    description = models.TextField(help_text='题目描述（文字）')
    description_input = models.TextField(help_text='输入描述（文字）')
    description_output = models.TextField(help_text='输出描述（文字）')

    # [题目属性-手动添加]
    # 必有
    top_module = models.CharField(max_length=20, help_text='顶层模块名字') # 必有 否则无法判题
    signal_names = models.ManyToManyField(SignalName, help_text='题目中需要的信号') # 必有 否则无法判题 一般题目都是至少有一个信号的
    # 可选
    deadline_time = models.DateTimeField(null=True, blank=True, help_text='题目的截止时间')
    level = models.IntegerField(default=1, help_text="难度等级")
    tags = models.CharField(max_length=100, help_text="题目标签", blank=True)
    
    # [题目关联的文件]
    template_code_file = models.ForeignKey(
        File, on_delete=models.SET_NULL, null=True, blank=True,
        help_text='模板代码文件 供学生在其基础上编写代码', related_name="template_code"
    )
    code_reference_file = models.ForeignKey(
        File, on_delete=models.SET_NULL, null=True, blank=True,
        help_text='模板代码文件', related_name="reference_code"
    )


    def get_testcases(self):
        "获得该题目所有测试点"
        return TestCase.objects.filter(problem=self)
    
    def get_total_grade(self):
        "获得该题目测试点分值之和"
        return sum([testcase.grade for testcase in self.get_testcases()])
    
    def get_submitted_users(self):
        "获得提交了该题目的用户（仅id）"
        from submission.models import Submission
        user_ids = Submission.objects.filter(problem=self).values('user').distinct().values('user_id')

        return user_ids
    
    def get_ac_users(self):
        "获得AC了该题目的用户（仅id）"
        from submission.models import Submission, SubmissionResult
        success_id = SubmissionResult.objects.filter(possible_failure="NONE", status="DONE").values('submission').values('submission_id')
        user_ids = Submission.objects.filter(problem=self, id__in=success_id).values('user').distinct().values('user_id')
        
        return user_ids
    
    def get_submissions(self):
        "获得所有提交"
        from submission.models import Submission
        return Submission.objects.filter(problem=self).values('id')
    
    def __str__(self):
        return self.name


class TestCase(models.Model):
    id = models.AutoField(primary_key=True, help_text='TestCase ID')
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        help_text='测试点所属的题目'
    )
    testbench_file = models.ForeignKey(
        File, on_delete=models.SET_NULL, null=True, blank=True,
        help_text='测试点的testbench文件', related_name="testbench"
    )
    grade = models.IntegerField(default=1, help_text='测试点的分值')

    def __str__(self):
        return "TestCase #{} (Problem #{}, {})".format(
            self.id, self.problem.id, self.problem.name
            )
