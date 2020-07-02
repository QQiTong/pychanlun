# Win10安装SSH服务

基于PowerShell的OpenSSH: <https://github.com/PowerShell/Win32-OpenSSH/releases>

详细说明可以参考Github的Wiki: <https://github.com/PowerShell/Win32-OpenSSH/wiki>

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
# 启动sshd服务
net start sshd
# 停止sshd服务
net stop sshd
# 删除sshd服务
sc delete sshd
```

## 修改设置

通常linux下会修改ssh_config文件来修改ssh配置，OpenSSH-Win64的配置在C:\ProgramData\ssh目录下。

以下配置分别是使用密钥登录，禁止密码登录，不允许空密码登录。

```
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
```

## 密钥生成

在客户端，生成密钥id_rsa和公钥id_rsa.pub
```
ssh-keygen -t rsa -C 电子邮箱地址
```

因为客户端一般是以adminstrator登录，所以生成后，把id_rsa.pub的内容添加到服务端的C:\ProgramData\ssh\administrators_authorized_keys文件中。参考文档: <https://github.com/PowerShell/Win32-OpenSSH/wiki/Security-protection-of-various-files-in-Win32-OpenSSH#administrators_authorized_keys>

## 文件权限设置

相关文件需要设置好权限，否则还是不能登录。参考文档: <https://github.com/PowerShell/Win32-OpenSSH/wiki/OpenSSH-utility-scripts-to-fix-file-permissions>
以管理员身份，在PowerShell中执行:
```
.\FixHostFilePermissions.ps1
```

上面提到的administrators_authorized_keys文件也要做权限设置。以管理员身份，在PowerShell中执行:
```
icacls administrators_authorized_keys /inheritance:r
icacls administrators_authorized_keys /grant SYSTEM:`(F`)
icacls administrators_authorized_keys /grant BUILTIN\Administrators:`(F`)
```

通过以上设置后就可以在客户端ssh免密登录了。
