# 部署

## 在Win上用pm2部署服务

安装pm2:

```cmd
npm i pm2 -g
```

安装pm2-windows-service:

```cmd
npm i pm2-windows-service -g
```

用pm2启动下载数据和监控服务:

```cmd
pm2 start D:\pychanlun\back\scheduler.py --interpreter python -n pychanlun-scheduler
```

保存服务记录，使服务可以随系统后自动启动

```cmd
pm2 save
```
