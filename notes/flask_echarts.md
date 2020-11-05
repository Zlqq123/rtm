
启动服务器
>>set FLASK_APP=hello.py
>>flask run

进入调试模式
>>set FLASK_ENV=development


外部可见的服务器
>>flask run --host=0.0.0.0



/home/user/Projects/flask-tutorial
├── flaskr/
│ ├── __init__.py
│ ├── db.py
│ ├── schema.sql
│ ├── auth.py
│ ├── blog.py
│ ├── templates/
│ │ ├── base.html
│ │ ├── auth/
│ │ │ ├── login.html
│ │ │ └── register.html
│ │ └── blog/
│ │ ├── create.html
│ │ ├── index.html
│ │ └── update.html
│ └── static/
│ └── style.css
├── tests/
│ ├── conftest.py
│ ├── data.sql
│ ├── test_factory.py
│ ├── test_db.py
│ ├── test_auth.py
│ └── test_blog.py
├── venv/
├── setup.py
└── MANIFEST.in