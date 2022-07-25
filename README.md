# Verilog OJ 后端

> 以`Ubuntu server 20.04`为例

## 开发

### 下载源代码

```sh
git clone git@git.tsinghua.edu.cn:eeverilogoj/verilogojbackend.git
cd verilogojbackend
cd backend
```

### 创建虚拟环境并安装依赖

```sh
# 使用`sudo apt update && sudo apt install python3-virtualenv`等命令安装Python虚拟环境
# 激活创建并Python虚拟环境（或使用conda）
virtualenv venv && . venv/bin/activate
# 安装必要依赖
python -m pip install -r requirements.txt
```

### 运行Django

```sh
# 迁移数据库结构
VERILOG_OJ_DEV=TRUE python manage.py makemigrations user file problem submission news discussion
# 创建数据库
VERILOG_OJ_DEV=TRUE python manage.py migrate
# 创建Django的超级用户的用户名和密码 在后台管理界面会用到 请妥善保管
VERILOG_OJ_DEV=TRUE python manage.py createsuperuser # once
# 启后端Django
VERILOG_OJ_DEV=TRUE python manage.py runserver
```

- 打开<http://127.0.0.1:8000/oj/docs>可以查看后端所有接口
- 打开<http://127.0.0.1:8000/oj/admin-django/>可以进行admin管理

### 重新运行

- 本地开发时，数据存在`backend/db.sqlite3`。
    - 数据库相关的结构大改时，若产生冲突，可以删除该数据库文件。
    - 如果在`makemigrations`或`migrate`阶段产生冲突，可以删除Django中所有app的`migrations/`重新建表。

## 生产

### 部署

- 第一次部署
    - 安装`Docker`和`Docker Compose` `sudo apt install docker.io docker-compose`
    - 启动Docker守护进程 `sudo systemctl start docker`
    - 在`.env`中修改生产部署的环境变量值 **请务必修改其中的账户密码**
    - `git clone git@git.tsinghua.edu.cn:eeverilogoj/verilogojbackend.git`
    - `cd verilogojbackend`
    - `sudo docker compose up --detach`
        - `--detach` Detached mode: Run containers in the background, print new container names.
    - 初始化Django数据库和创建超级用户
        - 进入backend容器
            - `sudo docker ps | grep _backend`
            - `sudo docker exec -it <container_id> /bin/sh`
        - `python manage.py makemigrations user file problem submission news discussion`
            - `makemigrations`后面要带上app的名字，否则默认会给`django_admin`建表，导致admin的用户模型会取代我们自己写的用户模型
        - `python manage.py migrate`
        - `python manage.py createsuperuser` 创建超级用户 注意保留帐密
- 非第一次部署（更新）
    - `git pull && sudo docker compose up --detach --build`
        - `--detach` Detached mode: Run containers in the background, print new container names.
        - `--build` Build images before starting containers. 重新构建依赖的images
    - 如果修改了数据库的结构
        - 进入backend容器执行应用数据库的修改
            - `sudo docker ps | grep _backend`
            - `sudo docker exec -it <container_id> /bin/sh`
        - `python manage.py makemigrations user file problem submission news discussion`
        - `python manage.py migrate`

### 部署成功

`sudo docker ps`可以看到有image为`verilogojbackend_backend-nginx` `verilogojbackend_backend` `mysql:5.7`的容器在跑

- API <http://166.111.223.67:40000/oj/api/>
- 查看接口文档 <http://166.111.223.67:40000/oj/api/docs/>

### 部署失败

用下列命令查看并删除后端相关数据、容器、镜像，重新执行第一次部署

- `sudo docker volume ls` `sudo docker volume rm -f ...`（注意备份）
- `sudo docker ps` `sudo docker rm -f ...`
- `sudo docker images` `sudo docker rmi -f...`

## 题目导入

以上步骤进行完毕后 可以导入题目 进行开发环境的部署测试。打开Django管理页面 逐个复制粘贴仓库目录下`test-problems`内的资源文件内容提交 即可在前端看到题目

按照`problem-bank/docs/add-problem.md`中的说明，先在`problem-bank/problems/`中编写题目。编写完成之后使用`problem-bank/gather_all_problem.py`的脚本将所有题目合成到一个文件内。

然后打开Django管理页面（<http://127.0.0.1:8000/oj/admin-django/problem/problem/import_yaml>或<http://166.111.223.67:40000/oj/admin-django/problem/problem/import_yaml>），点击`Problem`，右上角选择`从YAML文件导入`，复制`problem-bank/all_problems.yaml`点击提交即可导入。

## Open Source Projects

- [YAVGroup/Verilog-OJ](https://github.com/YAVGroup/Verilog-OJ) [AGPL-3.0 license](https://github.com/YAVGroup/Verilog-OJ/blob/master/LICENSE)
- [libreliu/pyDigitalWaveTools](https://github.com/libreliu/pyDigitalWaveTools) [MIT license](https://github.com/libreliu/pyDigitalWaveTools/blob/master/LICENSE)
