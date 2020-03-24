## 服务升级

快速执行
```sh
cd /opt/car_service  && source venv/bin/activate && git pull 
python3 manage.py migrate
ps auxw | grep car_uwsgi
uwsgi --reload /opt/car_service/uwsgi/uwsgi.pid
ps auxw | grep car_uwsgi
```

进入指定的路径

```sh
cd /opt/car_service
```

启动虚拟环境
```sh
source venv/bin/activate
```

拉取最新的代码
```sh
git pull
pip install -r requirements.txt
python3 manage.py migrate
```

重启服务

```sh
ps auxw | grep car_uwsgi
uwsgi --reload /opt/car_service/uwsgi/uwsgi.pid


uwsgi --ini /opt/car_service/car_uwsgi.ini
```


## 服务安装
进入指定的路径

```sh
cd /opt/car_service
```

启动虚拟环境
```sh
python3 -m venv venv
source venv/bin/activate
```

更新 setuptools pip

```sh
pip3 install --upgrade setuptools pip
```

安装依赖

```
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

查看服务

```sh
ps auxw | grep uwsgi
uwsgi --ini /opt/car_service/car_uwsgi.ini
uwsgi --reload /opt/car_service/uwsgi/uwsgi.pid
```
