# PYCHANLUN量化交易系统

## 在Windows本地机器部署

### 工具

#### scoop

推荐使用scoop管理windows软件, 网站：<https://scoop.sh>。

#### nssm

推荐使用nssm把程序部署成windows的服务，网站：<https://nssm.cc/>。

使用scoop安装python,nginx,nssm。我们使用python37，python38可能还会有不兼容的情况。

安装python37需要用到versions bucket。

```cmd
scoop bucket add versions
```

```cmd
scoop install python37
scoop install nginx
scoop install nssm
```

使用nssm把API服务程序安装成windows服务。生产模式服务放在在18888端口，防止和开发模式（使用5000端口）冲突。

MongoDB也要先安装成Windows服务模式，参考MongoDB文档。

（管理员命令行模式）
```cmd
nssm install pychanlun-api-service C:/Users/Administrator/scoop/apps/python37/current/scripts/pychanlun.exe
nssm set pychanlun-api-service AppDirectory D:/development/pychanlun
nssm set pychanlun-api-service AppParameters "run-api-server --port 18888"
nssm set pychanlun-api-service AppStdout E:/pychanlun.log
nssm set pychanlun-api-service AppStderr E:/pychanlun.log
nssm set pychanlun-api-service DependOnService MongoDB
net start pychanlun-api-service
```

使用nssm部署外盘数据下载程序

（管理员命令行模式）

```cmd
nssm install global-futures-downloader "pychanlun"
nssm set global-futures-downloader AppParameters "download-global-future-data"
nssm set global-futures-downloader DependOnService MongoDB
nssm start global-futures-downloader
```
使用nssm部署okex数据下载程序

（管理员命令行模式）

```cmd
nssm install global-futures-downloader "pychanlun"
nssm set global-futures-downloader AppDirectory "D:/development/pychanlun"
nssm set global-futures-downloader AppParameters "download-global-future-data"
nssm set global-futures-downloader DependOnService MongoDB
nssm start global-futures-downloader
```


使用nssm部署NGINX服务。

网页代码需要打包好，如果存放的目录不一样还要调整D:/development/pychanlun/nginx里面的配置。nginx对接口的代理指向到18888端口。

```cmd
cd D:\development\pychanlun\front
npm run build
```

```cmd
nssm install nginx "C:/Users/Administrator/scoop/shims/nginx.exe"
nssm set nginx AppParameters "-p D:/development/pychanlun/nginx"
net start nginx
```

这样的部署后只要输入<http://localhost>就可以访问系统了。

### 开发模式

在开发模式下，请使用如下方式启动程序，这样就不会和生产模式冲突了。

```cmd
cd D:\development\pychanlun
python pychanlun\server.py
```
