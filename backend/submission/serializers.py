from dataclasses import field
from rest_framework import serializers
from .models import Submission, SubmissionResult, LibraryMapping, GoogleLibraryMapping
from problem.serializers import ProblemSerializer, ProblemListSerializer
from user.serializers import UserSerializer, UserPublicSerializer, UserPublicListSerializer

class LibraryMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryMapping
        fields = '__all__'

class GoogleLibraryMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleLibraryMapping
        fields = '__all__'

class SubmissionResultSerializer(serializers.ModelSerializer):
    result = serializers.CharField(source='get_result', read_only=True)

    library_mapping_yosys_cmos = LibraryMappingSerializer(source='yosys_cmos_result', read_only=True)
    library_mapping_google_130nm = LibraryMappingSerializer(source='google_130nm_result', read_only=True)
    library_mapping_xilinx_fpga = LibraryMappingSerializer(source='xilinx_fpga_result', read_only=True)
    google_alldata = GoogleLibraryMappingSerializer(source='google_data',read_only=True)
    
    class Meta:
        model = SubmissionResult
        fields = '__all__'
        #exclude = ['id', 'submission']

class SubmissionResultPublicSerializer(serializers.ModelSerializer):
    result = serializers.CharField(source='get_result', read_only=True)

    class Meta:
        model = SubmissionResult
        #fields = '__all__'
        exclude = ['wave_json', 'log', 'logic_circuit_data','circuit_diagram_data'] # 需要用户验证才能看到的数据

class SubmissionSerializer(serializers.ModelSerializer):
    problem_belong = ProblemSerializer(source='problem', read_only=True)
    user_belong = UserSerializer(source='user', read_only=True)
    
    results = SubmissionResultSerializer(source='get_results', read_only=True, many=True)
    total_grade = serializers.IntegerField(source='get_total_grade', read_only=True)
    # judged = serializers.BooleanField(source='have_judged', read_only=True)
    # ac = serializers.BooleanField(source='is_ac', read_only=True)
    result = serializers.CharField(source='get_result', read_only=True)
    
    class Meta:
        model = Submission
        fields = '__all__'

class SubmissionPublicListSerializer(serializers.ModelSerializer):
    total_grade = serializers.IntegerField(source='get_total_grade', read_only=True)
    result = serializers.CharField(source='get_result', read_only=True)

    problem_belong = ProblemListSerializer(source='problem', read_only=True)
    user_belong = UserPublicListSerializer(source='user', read_only=True)
    class Meta:
        model = Submission
        # fields = '__all__'
        exclude = ['submit_file']

class SubmissionPublicSerializer(serializers.ModelSerializer):
    problem_belong = ProblemSerializer(source='problem', read_only=True)
    user_belong = UserPublicSerializer(source='user', read_only=True)
    
    results = SubmissionResultPublicSerializer(source='get_results', read_only=True, many=True)
    total_grade = serializers.IntegerField(source='get_total_grade', read_only=True)
    result = serializers.CharField(source='get_result', read_only=True)
    
    class Meta:
        model = Submission
        # fields = '__all__'
        exclude = ['submit_file']
