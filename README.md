# 缠论量化交易系统

## 安装和启动api服务

### 安装

Window环境安装项目依赖

```cmd
prepare.bat
```

处于开发阶段，代码经常会变，所以可以以开发模式安装。

```cmd
python setup.py develop
```

### 启动

如果以开发模式安装后，可以这样启动。

```cmd
pychanlun run-api-server
```

如果没有安装，可以这样启动。

```cmd
python pychanlun\cli.py run-api-server
```

还可以以模块方式启动api服务。

```cmd
python -m pychanlun
```

## 启动背驰监控程序

```cmd
pychanlun monitoring
```

或者

```cmd
python pychanlun\cli.py monitoring
```

## 其它

- ricequant rqdata 安装脚本 用于后期vnpy回测
  - make.bat
    >windows
  - make.sh
    >mac os
- front vue前端代码(停更)
- web 原生前端代码
- back 后端代码
  - monitor 监控代码
- vnpy-2.0.5 量化交易框架

使用阿里源安装程序包

```cmd
pip install -U tqsdk -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com
```
