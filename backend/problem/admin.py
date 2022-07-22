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
    actions = ['export_yaml', 'export_binary_yaml']

    def total_grade(self, obj):
        return obj.get_total_grade()

    def related_testcases_id(self, obj):
        return ",".join([str(p.id) for p in obj.get_testcases()])

    def import_yaml(self, yaml_data):
        def save_file_to_db(name, content):
            file_inst = File.objects.create(
                name=name,
                file=django.core.files.File(io.StringIO(initial_value=content), name=name)
            )
            return file_inst

        log = ""
        success = False

        problems = yaml.load(yaml_data, Loader=yaml.SafeLoader)
        log += "找到了 {} 个题目\n".format(len(problems))
        log += "开始存储题目...\n"
        try:
            for problem in problems:
                log += "已存储 问题{}({})...\n".format(problem['id'], problem['name'])
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

                code_template = save_file_to_db('template.v', problem['code_template'])
                problem_to_save.template_code_file = code_template
                
                code_reference = save_file_to_db('code_ref.v', problem['code_reference'])
                problem_to_save.judge_files.add(code_reference)

                for testbench in problem['code_testbenches']:
                    new_testbench = save_file_to_db('testbench.v', testbench) # FIXME 这里名字相同可能会冲突
                    problem_to_save.judge_files.add(new_testbench)

                problem_to_save.save()
        except:
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
                stat_msg += "Processing begin\n"
                log, success = self.import_yaml(request.POST['yaml_context'])
                stat_msg += log
                if not success:
                    stat_msg += "Operation failed.\n"
                else:
                    stat_msg += "Operation completed successfully.\n"
        
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
    list_display = ('id', 'related_problem', 'type', 'grade', 'mem_limit', 'time_limit')

    def related_problem(self, obj):
        return obj.problem

admin.site.register(Problem, ProblemAdmin)
admin.site.register(TestCase, TestCaseAdmin)
