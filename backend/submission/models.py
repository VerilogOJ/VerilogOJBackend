from dbm.ndbm import library
from django.db import models

from problem.models import Problem, TestCase
from file.models import File
from user.models import User

class LibraryMapping(models.Model):
    id = models.AutoField(primary_key=True)
    circuit_svg = models.TextField(help_text="元件库生成电路图",blank=True)
    resources_report = models.TextField(help_text="元件库资源占用报告",blank=True)
    log = models.TextField(help_text="元件库log",blank=True)
    mapping_error = models.TextField(help_text="元件库错误",blank=True)

class GoogleLibraryMapping(models.Model):
    id = models.AutoField(primary_key=True)
    google_log = models.TextField(help_text="google130nm元件库log",blank=True)
    google_yosys_svg = models.TextField(help_text="yosys元件库生成电路图",blank=True)
    google_resources_report = models.TextField(help_text="google130nm元件库资源占用报告",blank=True)
    google_130nm_svg = models.TextField(help_text="google130nm元件库生成电路图",blank=True)
    google_default_svg = models.TextField(help_text="netlistsvg默认库生成电路图",blank=)
    google_sta_report = models.TextField(help_text="google130nm元件库生成时序报告",blank=True)
    google_error = models.TextField(help_text="google130nm元件库错误",blank=True)

class Submission(models.Model):
    id = models.AutoField(primary_key=True, help_text='提交ID')
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE, null=True,
        help_text='提交的题目',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='提交的用户'
    )
    submit_time = models.DateTimeField(auto_now_add=True, help_text='提交时间')
    submit_file = models.ForeignKey(
        File, on_delete=models.SET_NULL, null=True, blank=True,
        help_text='学生提交的代码', related_name="code_student"
    )
    
    def get_results(self):
        "获得该次提交对应的所有测试点结果"
        return SubmissionResult.objects.filter(submission=self)
    
    def get_total_grade(self):
        "获得该次提交的总分数"
        return sum([result.grade for result in self.get_results()])
    
    # def have_judged(self):
    #     "判断是否已经评测完毕"
    #     if self.problem is None:
    #         return False
    #     else:
    #         return len(self.get_results()) == len(self.problem.get_testcases())
    
    def is_ac(self):
        "判断该次提交是否AC"
        for result in self.get_results():
            if not result.is_ac():
                return False
        return True
    
    def get_result(self):
        "获得该评测的结果类型"
        results = SubmissionResult.objects.filter(submission=self).order_by('testcase')
        for (i, result) in enumerate(results):
            if result.get_result() != 'Accepted':
                return result.get_result() + ' at testcase #%d' % i
        return 'Accepted'
    
    def check_integrity(self):
        """Check if it's sane; NEED TO MAKE SURE NO ONE'S SUBMITTING to get accurate result"""
        result_count = SubmissionResult.objects.filter(submission=self).count()
        testcase_count = self.problem.get_testcases().count()
        return (result_count == testcase_count, result_count, testcase_count)

class SubmissionResult(models.Model):
    id = models.AutoField(primary_key=True, help_text='提交结果ID')

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('JUDGING', 'Judging'),
        ('DONE', 'Done'),
        ('ERROR', 'Error')
    ]

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        help_text='The current status of this submission result'
    )

    POSSIBLE_FAILURE_CHOICES = [
        ('CE', 'Compile Error'),
        ('RLE', 'Resource Limitation Exceeded'),
        ('TLE', 'Time Limitation Exceeded'),
        ('WA', 'Wrong Answer'),
        ('NONE', 'No Error'),
        # When it's in PENDING or JUDGING we use this
        ('NA', 'Not available'),
        ('SERVER_ERROR', 'Error occurred in server')
    ]

    possible_failure = models.CharField(
        max_length=64, choices=POSSIBLE_FAILURE_CHOICES,
        help_text='Possible failure of this submission result'
    )

    submit_time = models.DateTimeField(auto_now_add=True, help_text='结果提交时间')
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        help_text='某个测试点结果所属的提交'
    )
    testcase = models.ForeignKey(
        TestCase,
        on_delete=models.CASCADE,
        help_text='某个测试点结果所属的测试点'
    )
    grade = models.IntegerField(help_text='本测试点所得的分数')
    log = models.TextField(help_text='判题过程中输出的log', blank=True)
    # 如果文件系统中存了一份那其实就没必要再在数据库中存了
    wave_json = models.TextField(help_text='仿真获得的WaveJSON（由用户上传的verilog代码生成）', blank=True)
    logic_circuit_data = models.TextField(help_text='逻辑级电路图（由用户上传的verilog代码生成）', blank=True) # svg也是文字哦
    logic_circuit_possible_error = models.TextField(help_text='逻辑电路图生成过程中错误', blank=True)
    yosys_cmos_result = models.ForeignKey(LibraryMapping,on_delete=models.SET_NULL,null=True,blank=True,help_text='yosys_cmos元件库生成电路图和资源报告',related_name="yosys_cmos_result")
    google_130nm_result = models.ForeignKey(LibraryMapping,on_delete=models.SET_NULL,null=True,blank=True,help_text='google_130nm元件库生成电路图和资源报告',related_name="google_130nm_result")
    xilinx_fpga_result = models.ForeignKey(LibraryMapping,on_delete=models.SET_NULL,null=True,blank=True,help_text='xilinx_fpga元件库生成电路图和资源报告',related_name="xilinx_fpga_result")
    google_data = models.ForeignKey(GoogleLibraryMapping,on_delete=models.SET_NULL,null=True,blank=True,help_text='google_130nm元件库生成电路图,资源报告和时序分析',related_name="google_data")
    
    class Meta:
        unique_together = (('submission', 'testcase'),)
    
    def is_ac(self):
        "判断该测试点是否AC"
        return self.possible_failure == 'NONE'
    
    def get_result(self):
        "获得该评测的结果类型"
        if self.status == 'DONE':
            if self.possible_failure == 'NONE':
                return 'Accepted'
            else:
                return self.get_possible_failure_display()
        elif self.status == 'ERROR':
            return 'System Error'
        else:
            return self.status
