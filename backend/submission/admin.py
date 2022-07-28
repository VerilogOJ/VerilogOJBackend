from django.contrib import admin
from django.core import serializers
from django.http import HttpResponse
from .models import Submission, SubmissionResult
from file.models import File
import json

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'user', 'submit_time', 'is_ac', 'grade_got', 'problem_score_total')
    list_filter = ('problem__name', 'user', 'submit_time')
    
    def have_judged(self, obj):
        return obj.have_judged()
    # make a pretty boolean icon
    # ref: https://stackoverflow.com/questions/8227023/list-display-boolean-icons-for-methods
    have_judged.boolean = True

    def is_ac(self, obj):
        return obj.is_ac()
    is_ac.boolean = True

    def grade_got(self, obj):
        return obj.get_total_grade()

    def problem_score_total(self, obj):
        return obj.problem.get_total_grade()

    def save_json(self, request, queryset):
        # response = HttpResponse(content_type="application/json")

        submissions_json_array = []
        for submission in queryset:
            submission_dict = {} # 一次提交对应的json文件 注意其中设置的域方便老师/助教查看 而非所有
            
            submission_dict["题目logicID"] = str(submission.problem.logic_id)
            submission_dict["题目名称"] = str(submission.problem.name)

            submission_dict["提交ID"] = str(submission.id)
            submission_dict["提交用户"] = str(submission.user.username)
            submission_dict["提交时间"] = str(submission.submit_time)
            submission_dict["提交时间"] = str(submission.submit_time)
            submit_file_path = submission.submit_file.file.path
            with open(submit_file_path, "r") as f:
                submission_dict["提交代码"] = f.read()

            submission_dict["提交总分数"] = str(submission.get_total_grade())
            submission_dict["提交结果"] = str(submission.get_result())
            submission_dict["提交正误"] = str(submission.is_ac())

            submission_results = submission.get_results() # submission_results: QuerySet(SubmissionResult)
            for submission_result in submission_results:
                pass # TODO 但感觉也没必要加入result里面的东西
            
            submissions_json_array.append(submission_dict)
        
        return HttpResponse(
            content=json.dumps(submissions_json_array, ensure_ascii=False),
            content_type="application/json"
        )
    save_json.short_description = "导出json"
    actions = ["save_json"]

class SubmissionResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'submit_time', 'submission', 'testcase', 'grade')
    list_filter = ('status', 'grade', 'submit_time', 'testcase')

admin.site.register(Submission, SubmissionAdmin)
admin.site.register(SubmissionResult, SubmissionResultAdmin)
