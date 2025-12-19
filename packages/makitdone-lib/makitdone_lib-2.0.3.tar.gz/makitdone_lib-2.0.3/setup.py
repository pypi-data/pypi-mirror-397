from setuptools import setup

setup(
    name='makitdone-lib',
    version='2.0.3',
    packages=[
        'makit.lib',
        'makit.lib.inspect',
        'makit.lib.json',
        'makit.lib.samples'
    ],
    namespace_package=['makit', 'makit.lib'],
    install_requires=[
        'docstring_parser~=0.17.0',
        'psutil~=7.1.1',
        'setuptools~=80.9.0'
    ],
    python_requires='>=3.3',
    url='https://gitee.com/makitdone/makitdone-lib',
    license='MIT',
    author='liangchao',
    author_email='liang20201101@163.com',
    description='python基础库扩展'
)
