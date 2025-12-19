# coding:utf-8

from makit.lib.command import AppCommand

c = AppCommand('test')


@c.command(default=True)
def serve(env: str = 'prod', host: str = '127.0.0.1', port: int = 8080):
    """
    运行服务
    :param env: 环境，默认值: prod
    :param host: host地址，默认 127.0.0.1
    :param port: 端口默认8080
    :return:
    """
    print('Serving on %s:%d, env: %s' % (host, port, env))


c.run()
