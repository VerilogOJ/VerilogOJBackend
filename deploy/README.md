# README

- 判题服务应用`pyDigitalWaveTools`作为依赖
    - 可以通过`pip3 install git+https://github.com/libreliu/pyDigitalWaveTools`安装
    - 可以通过`pip3 install -e pyDigitalWaveTools`来安装 相应的需要在`Dockerfile.judge-env`中添加`ADD ./pyDigitalWaveTools/ /app/pyDigitalWaveTools`
        - `-e, --editable <path/url>` Install a project in editable mode (i.e. setuptools "develop mode") from a local project path or a VCS url.
