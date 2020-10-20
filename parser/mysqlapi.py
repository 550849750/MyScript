# encoding=utf-8
import pymysql.cursors
import configparser


class MysqlApi(object):
    # 类属性
    __instance = None

    def __new__(cls):
        """实例创建方法"""
        if cls.__instance == None:
            # 通过父类的__new__(cls)创建实例
            cls.__instance = object.__new__(cls)
            return cls.__instance
        else:
            return cls.__instance

    def __init__(self, **kwargs):
        """
        初始化数据库连接(初始化方法)

        :param kwargs:  连接配置参数
        """
        try:
            CF = configparser.ConfigParser()
            CF.read('config.ini')
            # 数据库配置信息
            self.db_config = {
                'host': CF.get('db_source', 'host'),
                'port': int(CF.get('db_source', 'port')),
                'user': CF.get('db_source', 'user'),
                'password': CF.get('db_source', 'password'),
                'db': CF.get('db_source', 'db'),
                'charset': 'utf8',
                'cursorclass': pymysql.cursors.DictCursor,
            }
            self.tables = CF.get('db_source', 'table')
        except Exception as e:
            raise e

        self.db_config.update(kwargs) if kwargs and len(kwargs) else ''
        self.__conn = pymysql.connect(**self.db_config)
        self.__cursor = self.__conn.cursor()
        # sql执行结果计数器
        self.affected = 0

    def execute(self, sql, args=None, debug=False):
        """
        执行sql语句

        :param sql:     sql语句

        :param args:    传入字典或元组,用于替换sql中的%(name)s 或 %s

        :param debug:    是否调试模式

        :return:
        """
        try:

            self.affected = self.__cursor.execute(sql, args)
            self.__conn.commit()
        except Exception as e:
            self.__conn.rollback()
            if debug:
                raise e
        return self

    def update(self, table, where, data, debug=False):
        """更新数据库"""
        data = self.__parse_dict(data, model='update')
        sql = "UPDATE {} SET {} WHERE {}".format(table, data, where)
        self.execute(sql, debug=debug)

    def get_cursor(self):
        """获取游标"""
        if self.affected > 0:
            # 重置查询结果行数
            self.affected = 0
            return self.__cursor

    def __parse_dict(self, data, model='update', and_or='and'):
        """将字典解析为sql字符串"""
        if isinstance(data, dict):
            res = ''
            space = ' '
            # where条件运算连接符
            and_or = space + and_or + space
            # 数据更新
            if model == 'update':
                for k, v in data.items():
                    v = pymysql.escape_string(str(v))
                    if not res:
                        res = str(k) + '=' + "'" + str(v) + "'"
                    else:
                        res += "," + str(k) + '=' + "'" + str(v) + "'"
            if model == 'where':
                # 数据格式:
                # {'id':['in',[1,2,3,4]],'num':'2','name':['like','%啊%'],'__condition__':'and'}
                for k, v in data.items():
                    if isinstance(v, list):
                        operator = v[0]
                        value = v[1]
                    else:
                        operator = '='
                        value = v
                    # 操作运算符
                    operator = space + operator + space
                    if not res:
                        res = str(k) + operator + "'" + str(value) + "'"
                    else:
                        res += and_or + str(k) + operator + "'" + str(value) + "'"
            return res

    def __del__(self):
        self.__cursor.close()
        self.__conn.close()
