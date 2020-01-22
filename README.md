# 缠论量化交易系统

## 安装和启动api服务

### 安装

处于开发阶段，代码经常会变，所以可以以开发模式安装。

```cmd
python setup.py develop
```

### 启动

如果以开发模式安装后，可以这样启动。

```cmd
pychanlun server run
```

或者

```cmd
pychanlun server
```

如果没有安装，可以这样启动。

```cmd
python pychanlun\cli server run
```

或者

```cmd
python pychanlun\cli server
```

还可以以模式方式启动api服务。

```cmd
python -m pychanlun
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
