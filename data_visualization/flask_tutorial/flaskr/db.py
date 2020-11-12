import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():#返回一个数据库连接，用于执行文件中的命令
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
            )
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:#打开一个文件，该文件名是相对于flaskr 包的
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')#定义一个名为init-db 命令行，它调用init_db 函数，并为用户显示一个成功的消息。
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)#告诉Flask 在返回响应后进行清理的时候调用此函数。
    app.cli.add_command(init_db_command)#添加一个新的可以与flask 一起工作的命令