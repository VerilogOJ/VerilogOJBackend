# Verilog OJ 后端

> 以`Ubuntu server 20.04`为例

## 开发

### 安装全局依赖

```sh
sudo apt update && sudo apt upgrade # once
sudo apt install build-essential python3-virtualenv yosys iverilog rabbitmq-server # once
# 其中yosys和iverilog为Verilog综合仿真软件 rabbitmq负责在后端和判题模块中传递消息
```

### 下载源代码

```sh
git clone git@git.tsinghua.edu.cn:eeverilogoj/verilogojbackend.git # once
cd verilogojbackend
cd backend
```

### 创建Python虚拟环境

```sh
# 激活创建并Python虚拟环境
virtualenv venv
. venv/bin/activate

# 安装必要依赖
python -m pip install -r requirements.txt # once
```

### 运行Django

```sh
# 如果不用Docker判题环境 需要将`backend/backend/settings/dev.py`中的 `use_docker`修改为False（开发默认False 生产默认True） 否则会报错说缺少一些Docker相关的环境变量

# 创建数据库
VERILOG_OJ_DEV=TRUE python manage.py migrate
# 创建Django的超级用户的用户名和密码 在后台管理界面会用到 请妥善保管
VERILOG_OJ_DEV=TRUE python manage.py createsuperuser # once
# 启后端Django
VERILOG_OJ_DEV=TRUE python manage.py runserver
```

- 打开<http://127.0.0.1:8000/oj/docs>可以查看后端所有接口
- 打开<http://127.0.0.1:8000/oj/admin-django/>可以进行admin管理

### 运行判题服务

```sh
# 激活Python虚拟环境
virtualenv venv
. venv/bin/activate
```

```sh
# 启动rabbitmq
sudo systemctl start rabbitmq-server

VERILOG_OJ_DEV=TRUE celery -A judge worker -l INFO
```

### 题目导入

以上步骤进行完毕后 可以导入题目 进行开发环境的部署测试。打开Django管理页面<http://127.0.0.1:8000/oj/admin-django/problem/problem/import_yaml> 逐个复制粘贴仓库目录下`test-problems`内的资源文件内容提交 即可在前端看到题目

## 生产

### 部署

- 第一次部署
    - 安装`Docker`和`Docker Compose` `sudo apt install docker.io docker-compose`
    - 启动Docker守护进程 `sudo systemctl start docker`
    - 在`.env`中修改生产部署的环境变量值 **请务必修改其中的账户密码**
    - `sudo docker-compose up --detach`
        - `--detach` Detached mode: Run containers in the background, print new container names.
    - 初始化Django数据库和创建超级用户
        - 进入backend容器
            - `sudo docker ps | grep _backend`
            - `sudo docker exec -it <container_id> /bin/sh`
        - `python manage.py migrate`
        - `python manage.py createsuperuser`
- 非第一次部署（更新）
    - 如果修改了数据库的结构
        - 注意用`python manage.py makemigrations`更新实际数据库的表格
        - 进入backend容器执行
        - `python manage.py migrate`
    - `git pull && sudo docker-compose up --detach --build`
        - `--build` Build images before starting containers. 重新构建依赖的images
        - `--detach` Detached mode: Run containers in the background, print new container names.

### 成功部署

`sudo docker ps`可以看到有image为`verilogojbackend_backend-nginx` `verilogojbackend_backend` `verilogojbackend_judgeworker`  `rabbitmq:3.8-management` `mysql:5.7`的容器在跑

- API <http://166.111.223.67:40000/oj/api/>
- 查看接口文档 <http://166.111.223.67:40000/oj/api/docs/>
- Django管理 <http://166.111.223.67:40000/oj/admin-django/>
    - 在<http://166.111.223.67:40000/oj/admin-django/problem/problem/import_yaml>中逐个复制粘贴仓库目录下`test-problems`内的资源文件内容，提交，即可在前端看到题目

## Open Source Projects

- [YAVGroup/Verilog-OJ](https://github.com/YAVGroup/Verilog-OJ) [AGPL-3.0 license](https://github.com/YAVGroup/Verilog-OJ/blob/master/LICENSE)
- [libreliu/pyDigitalWaveTools](https://github.com/libreliu/pyDigitalWaveTools) [MIT license](https://github.com/libreliu/pyDigitalWaveTools/blob/master/LICENSE)
