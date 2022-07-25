from django.contrib import admin
from .models import Problem, TestCase, SignalName
from file.models import File
from django.urls import path
from django.template.response import TemplateResponse
import sys, io
from django.db import transaction
import django.core.files
from django.http import HttpResponse
import yaml

class TestCaseInline(admin.StackedInline):
    model = TestCase
    extra = 0

class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'create_time', 'deadline_time', 'total_grade', 'related_testcases_id')
    inlines = [
        TestCaseInline,
    ]
    change_list_template = ['admin/custom_change_list.html']
    # actions = ['export_yaml', 'export_binary_yaml']

    def total_grade(self, obj):
        return obj.get_total_grade()

    def related_testcases_id(self, obj):
        return ",".join([str(p.id) for p in obj.get_testcases()])

    def import_yaml(self, yaml_data):
        print("[DEBUG] 导入YAML文件开始")
        log = ""
        success = False

        problems = yaml.load(yaml_data, Loader=yaml.SafeLoader)
        log += "找到了 {} 个题目\n".format(len(problems))
        log += "开始存储题目...\n"
        try:
            print("[DEBUG] 导入YAML文件开始 try块开始")
            for problem in problems:
                log += "正在存储问题{}({})...\n".format(problem['id'], problem['name'])
                problem_to_save = Problem.objects.create(
                    logic_id=problem['id'],
                    name=problem['name'],
                    description=problem['description'],
                    description_input=problem['description_input'],
                    description_output=problem['description_output'],
                    top_module=problem['top_module'],
                )
                for signal in problem['signals']:
                    new_signal = SignalName.objects.create(name=signal)
                    problem_to_save.signal_names.add(new_signal)

                code_template = File.objects.create(
                    name='template.v',
                    file=django.core.files.File(io.StringIO(initial_value=problem['code_template']), name='template.v')
                )
                problem_to_save.template_code_file = code_template
                
                code_reference = File.objects.create(
                    name='code_ref.v',
                    file=django.core.files.File(io.StringIO(initial_value=problem['code_reference']), name='code_ref.v')
                )
                problem_to_save.code_reference_file = code_reference

                for testbench in problem['code_testbenches']:
                    new_testbench_file = File.objects.create(
                        name='testbench.v',
                        file=django.core.files.File(io.StringIO(initial_value=testbench), name='testbench.v')
                    )
                    TestCase.objects.create(
                        problem=problem_to_save,
                        testbench_file=new_testbench_file
                    ).save()

                problem_to_save.save()
                
                print("[DEBUG] 添加成功")
        except Exception as e:
            print("[DEBUG] 出问题")
            print(e)
            log += str(e) + "\n"
            success = False
            log += "添加题目出错\n"
            return log, success

        success = True
        return log, success
        

    def import_yaml_view(self, request):
        # TODO: avoid duplicate import
        stat_msg = ""
        if request.method == 'POST':
            if 'yaml_context' not in request.POST:
                stat_msg += "Error: yaml_context should be available in POST request"
            else:
                stat_msg += "开始导入...\n"
                log, success = self.import_yaml(request.POST['yaml_context'])
                stat_msg += log
                if not success:
                    stat_msg += "导入失败...\n"
                else:
                    stat_msg += "成功导入！\n"
        
        context = dict(
            self.admin_site.each_context(request),
            title="使用YAML文件导入题目",
            # Additional context
            status_message=stat_msg if stat_msg != "" else "暂无"
        )
        return TemplateResponse(request, "admin/import_yaml.html", context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import_yaml/', self.admin_site.admin_view(self.import_yaml_view)),
        ]
        return my_urls + urls

class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'related_problem', 'grade')

    def related_problem(self, obj):
        return obj.problem

admin.site.register(Problem, ProblemAdmin)
admin.site.register(TestCase, TestCaseAdmin)
