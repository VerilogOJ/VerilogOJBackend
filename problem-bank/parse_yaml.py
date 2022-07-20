import yaml

with open("./problems/2to1mux.yaml", "r") as f:
    yaml_content = yaml.safe_load(f)

print(yaml_content)

print(yaml_content[0]["code_template"])
print(yaml_content[0]["code_reference"])
print(yaml_content[0]["code_testbenches"][0])