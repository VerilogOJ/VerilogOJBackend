import yaml

yaml_path = "./problems/100-2to1mux.yaml"
with open(yaml_path, "r") as f:
    yaml_content = yaml.safe_load(f)

print(yaml_content)

# [题目信息]
print(yaml_content[0]["id"])
print(yaml_content[0]["name"])
print(yaml_content[0]["description"])
print(yaml_content[0]["description_input"])
print(yaml_content[0]["description_output"])

# [题目属性]
print(yaml_content[0]["top_module"])
print(yaml_content[0]["signals"][0])

# [题目代码]
print(yaml_content[0]["code_template"])
print(yaml_content[0]["code_reference"])
print(yaml_content[0]["code_testbenches"][0])
