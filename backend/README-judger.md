# 判题流程


前端submit:
post("/files/", "code.v")
post("/submit", problem, submit_files)

后端:
backend/submission/view.py:
def post():
    调用do_judge_task

tasks.py:
def do_judge_task(detail, judger_config):
    根据judger_config['use_docker']选择local.py/docker.py
    然后调用executor.run()

judge/executor/local.py:
    def run():
        创建一个temp文件夹:
            TESTCASE_DIR, PROBLEM_DIR, SUBMIT_DIR = self.place_tree(tmpdirname)

            def place_tree():
                从/files/里下载file所需项目

        执行subprocess: main.sh

        读取 score,log,appdata

        patch_result


judge/executor/docker.py:
    def run():
       os.mkdir(base_dir)
       self.place_tree(base_dir)#把文件放在这里
       os.chdir(base_dir)

       在此处创建docker 
        def create_docker(
            self,
            docker_image_name,
            id,
            bind_mount_hostside, 
            bind_mount_containerside,
            container_cmd
        )
        把本地bind_mount_hostside挂载到bind_mount_containerside
        调用时
        docker_image_name = self.judger_config['docker_image']
        id = self.detail['submission_result']['id']
        container_cmd = "main.sh"

        调用完container_cmd后，直接从本地读文件，流程和local.py完全相同

        