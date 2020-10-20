# encoding=utf-8
import threading
import configparser
import requests

API = 'index.php?s=bdts&c=bdapi&m=push'


def get_ini():
    """解析配置文件"""
    try:
        CF = configparser.ConfigParser()
        CF.read('config.ini')
    except Exception as e:
        raise e
    return CF.items()


def main():
    items = get_ini()
    for item in items:
        key, data = item
        if key == 'DEFAULT':
            continue
        data = dict(data)
        if 'host' not in data.keys():
            continue
        url = str(data.pop('host')).rstrip('/') + '/' + API.lstrip('/')
        t = threading.Thread(target=handler, kwargs={'url': url, 'param': data})
        t.start()



def handler(url, param):
    print(requests.Session().post(url, param).text)


if __name__ == '__main__':
    main()
