from setuptools import setup, find_packages

setup(
    entry_points={
        "console_scripts": ["pychanlun = pychanlun.cli:run"]
    },
    name="pychanlun",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "flask",
        "pandas",
        "scipy",
        "requests",
        "pydash",
        "apscheduler",
        "pymongo",
        "pytest",
        "pytest-html",
        "ratelimit",
        "waitress",
        "click",
        "pytdx",
        "et_stopwatch",
        "func_timeout",
        "loguru",
        "quantaxis",
        "pyecharts",
        "matplotlib",
        "prettytable",
        "tushare",
        "pytz",
        "colorama",
        "matplotlib"
    ]
)
