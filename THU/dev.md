# 开发环境部署指南

## Ubuntu 20.04

### 安装全局依赖

```sh
sudo apt update && sudo apt upgrade # once

sudo apt install build-essential rabbitmq-server yosys nodejs npm python3-virtualenv # once
sudo systemctl start rabbitmq-server # once
```

### 下载代码库

```sh
git clone https://github.com/lluckydog/Verilog-OJ # once

cd Verilog-OJ
```

### 前端

```sh
cd frontend
```


```sh
npm install . # once
```

```sh
npm run serve
```

会弹出 Webpack 的分析界面（端口 8888），这并不是我们的前端界面

前端界面通过 `http://localhost:8080/` 访问

### 运行后端

```sh
cd backend
```

```sh
virtualenv ../venv
. ../venv/bin/activate

python -m pip install -r requirements.txt # once
```

```sh
# 设置一些必须的环境变量
# 如果不用 Docker 判题环境，就需要将 backend/backend/settings/dev.py 中的 `use_docker` 修改为False
# 否则会报缺少一些 Docker 相关的环境变量
VERILOG_OJ_DEV=TRUE python manage.py migrate

# 此处创建您测试环境的超级用户的用户名和密码
# 在后台管理界面也会用到，请妥善保管
VERILOG_OJ_DEV=TRUE python manage.py createsuperuser # once

# 启后端
VERILOG_OJ_DEV=TRUE python manage.py runserver
```

- 打开<http://127.0.0.1:8000/oj/docs>可以查看后端所有接口
- 打开<http://127.0.0.1:8000/oj/admin-django/>可以进行admin管理

### 题目导入

以上步骤进行完毕后，可以导入题目，进行开发环境的部署测试、

在后端运行的前提下，打开 <http://127.0.0.1:8000/oj/admin-django/problem/problem/import_yaml>

逐个复制粘贴仓库目录下 assets 内的资源文件内容，提交，即可在前端看到题目

### 运行判题服务器

```sh
cd backend
```

```sh
virtualenv ../venv
. ../venv/bin/activate

# Make sure your rabbitmq have started.
# If not, use systemctl start rabbitmq-server
# (use systemctl enable to start on system boot)
VERILOG_OJ_DEV=TRUE celery -A judge worker -l INFO
```
