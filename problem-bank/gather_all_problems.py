# https://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python
import glob

yaml_files = glob.glob("./problems/*.yml")
yaml_files += glob.glob("./problems/*.yaml")

all_problems = ""

for yaml_file in yaml_files:
    with open(yaml_file, "r") as f:
        all_problems += f.read() + "\n"

all_problems_file = "./all_problems.yaml"
with open(all_problems_file, "w") as f:
    f.write(all_problems)
