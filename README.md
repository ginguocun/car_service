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

数据迁移
```bash
python3 manage.py dumpdata --all --format=json > mysite_all_data.json
python3 manage.py loaddata mysite_all_data.json
```

```python
from app.models import *

irs = InsuranceRecord.objects.filter(profits__isnull=True)
for ir in irs:
    if ir.total_price:
        if ir.payback_amount:
            payback_amount = ir.payback_amount
        else:
            payback_amount = 0
        if ir.ic_payback_amount:
            ic_payback_amount = ir.ic_payback_amount
        else:
            ic_payback_amount = 0
        ir.profits = round(float(ir.total_price) - float(payback_amount) - float(ic_payback_amount), 2)
        ir.save()
        print(ir.total_price, ir.profits)
```