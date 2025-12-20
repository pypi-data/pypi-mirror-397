import setuptools
import os
from distutils.command.register import register as register_orig
from distutils.command.upload import upload as upload_orig

from setuptools import setup


class register(register_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')

class upload(upload_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qufit",
    version="1.1.70",
    author="赵寿宽(sk zhao)",
    author_email="2396776980@qq.com",
    description="本模块包括了超导量子计算实验中常用模型的拟合函数于数据处理方法。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    cmdclass={
        'register': register,
        'upload': upload,
    },
    # install_requires=[
    #     'qufit',
    #     'numpy',
    #     'pandas',
    #     'scikit-learn',
    #     'scipy',
    #     'sympy',
    #     'matplotlib',
    #     'imp',
    #     'math',
    #     'bayesian-optimization',
    #     'nest_asyncio',
    #     'scikit-optimizer',
    #     'pickle',
    #     'plotly',
        
    # ],
)
