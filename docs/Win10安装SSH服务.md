# Win10安装SSH服务

基于PowerShell的OpenSSH: <https://github.com/PowerShell/Win32-OpenSSH/releases>

详细说明可以参考Github的Wiki: <https://github.com/PowerShell/Win32-OpenSSH/wiki>，安装步骤：

## 安装步骤

1. 从上面地址下载OpenSSH-Win64.zip，解压（解压的目录就是安装目录，可以移动到想要安装的目录）。

2. 开打cmd，进入解压后的目录，执行命令:
```
powershell.exe -ExecutionPolicy Bypass -File install-sshd.ps1
```

3. 服务启停操作
```
# 设置服务自启动
sc config sshd start=auto
# 使服务变为手动启动
sc config sshd start=demand
# 启动sshd服务
net start sshd
# 停止sshd服务
net stop sshd
# 删除sshd服务
sc delete sshd
```
