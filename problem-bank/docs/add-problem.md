# 出题指南

https://yaml-multiline.info/

## YAML文件结构

在`problem-bank/problems/`中新建一个yaml文件并编辑内容，即可创建一个题目。


- 题目信息
    - `id` 题目id（正整数）
        - 请确保每道题目的id唯一
        - 试手题目 0-99
        - 每个专题 100-199 200-299 ...
    - `name` 题目名称（字符串）
    - `description` 题目描述（多行字符串）
        - 支持Markdown
    - `description_input` 输入描述（多行字符串）
        - 支持Markdown
    - `description_output` 输出描述（多行字符串）
        - 支持Markdown
- 题目属性
    - `top_module` 顶层模块名称（字符串）
        - 需要确保`code_template`,`code_reference`的模块名称为`top_module`指定的名称
    - `signals` 波形图需要显示的信号名称（字符串列表）
        - 需要确保`code_template`,`code_reference`,`code_testbenches`模块中的信号为`signals`中的信号名称
- 题目代码
    - `code_template` 代码模版（多行字符串）
        - 在其中添加提示`// 在这里输入你的代码 请不要修改模块和信号名称`
    - `code_reference` 参考答案（多行字符串）
    - `code_testbenches` 测试矢量（多行字符串列表）
        - 一个测试矢量表示一个测试点
        - 测试矢量的模块名称必须为`testbench`
        - 需要在其中添加下面的代码确保后台分析工具成功生成波形文件
            ```verilog
            initial begin
                $dumpfile(`DUMP_FILE_NAME);
                $dumpvars;
            end
            ```

## 检查YAML

修改`problem-bank/parse_yaml.py`中的`yaml_path`为某个yaml文件，并执行该Python脚本。如果没有出错，则说明yaml格式正确。

## 汇总全部题目

执行`problem-bank/gather_all_problem.py`得到yaml文件`all_problems.yaml`。

## 添加新题目

将某道题或者全部题目的yaml文件复制到Django后端即可完成题目的添加。
