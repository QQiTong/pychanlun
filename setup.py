from setuptools import setup, find_packages

setup(
    entry_points = {
        "console_scripts": ["pychanlun = pychanlun.cli:run"]
    },
    name = "pychanlun",
    version = "1.0.0",
    packages = find_packages(),
    install_requires = [
        "flask",
        "pandas",
        "requests",
        "pydash",
        "apscheduler",
        "pymongo",
        "gunicorn",
        "gevent",
        "json-logging-py",
        "rx",
        "pytest",
        "pytest-html",
        "ratelimit",
        "waitress",
        "tornado",
        "click"
    ]
)
