# encoding=utf-8
from mysqlapi import MysqlApi
import threading
from summary import Summary
from titleparse import Title
import re
import time
import configparser

db = MysqlApi()
lock = threading.Lock()


def get_ini(section):
    """解析配置文件"""
    try:
        CF = configparser.ConfigParser()
        CF.read('config.ini')
    except Exception as e:
        raise e
    return CF.items(section)


# 获取待处理的字段(全局)
field_tags = get_ini('field_tags')


def main():
    # 线程数量
    thread_num = 32
    rows = yield_row()
    # 多线程并发执行
    while True:
        if len(threading.enumerate()) < thread_num:
            try:
                row = next(rows)
            except StopIteration:
                break
            table = row.pop('__table__')
            # 创建子线程
            th = threading.Thread(target=handler, args=(row, table), name=row['Id'])
            th.start()
        else:
            time.sleep(0.2)
            continue


def yield_row():
    """每次生产一条记录"""
    table_names = str(db.tables).split(',')
    for table in table_names:
        if not check_db(table):
            continue
        cursor = db.execute(
            "select * from {} where have_summary=0 and ysneirong!='' and baidutitle!='';".format(table),
            debug=True).get_cursor()
        if not cursor:
            continue
        rows = list(cursor.fetchall())
        while True:
            if not rows:
                break
            row = rows.pop()
            # 表名称
            row['__table__'] = table
            yield row


def handler(row, table):
    """多线程处理器"""
    data = parse_summary(row)
    data2 = parse_title(row)
    data.update(data2)
    lock.acquire()
    # 入库
    db.update(table, 'Id={}'.format(row['Id']), data=data)
    lock.release()


def parse_summary(row):
    """摘要处理"""
    obj = Summary()
    data = {}
    for item in field_tags:
        s_field, e_field = item
        text = re.sub('\<.+?\>', '', row[s_field])
        summary = obj.summary(text, phrases_num=3, sentence_num=12)
        if len(summary) < 15:
            continue
        data[e_field] = summary

    data['have_summary'] = 1 if len(data) else -1
    return data


def parse_title(row):
    """标题处理"""
    obj = Title()
    data = obj.process(row)
    if not data:
        return
    # 添加处理标志
    data['is_worked'] = 1
    return data


def check_db(table):
    """检查表字段完整性"""
    # 为表加上`is_worked`字段
    cursor = db.execute(
        "select count(*) as c from information_schema.columns where table_name=%s and column_name='have_summary';",
        (table,)).get_cursor()
    if not cursor:
        return False
    row = cursor.fetchone()
    if row['c'] == 0:
        db.execute(
            "ALTER TABLE %s ADD `have_summary` INT(5) NOT NULL DEFAULT '0' AFTER `PageUrl`, ADD INDEX (`have_summary`);" % (
                table,))

    # 为表加上`is_worked`字段
    cursor = db.execute(
        "select count(*) as c from information_schema.columns where table_name=%s and column_name='is_worked';",
        (table,)).get_cursor()
    if not cursor:
        return False
    row = cursor.fetchone()
    if row['c'] == 0:
        db.execute(
            "ALTER TABLE  %s ADD `is_worked` INT(5) NOT NULL DEFAULT '0' AFTER `PageUrl`, ADD INDEX (`is_worked`);" % (
                table,))

    return True


if __name__ == '__main__':
    main()
