import sys
from cx_Freeze import setup, Executable
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin

include_files = []

base = None

if sys.platform == "win32":
    base = "Win32GUI"

executables = {
    Executable("wsgi.py", base=base)
}

buildOptions = dict(
        packages = [],
        includes = ["flask","flask_login","flask_sqlalchemy","flask_migrate","flask_admin"],
        include_files = [],
        excludes = []
)


setup(name = "script",
        version = "0.1",
        description = "this is a script",
        options = dict(build_exe = buildOptions),
        executables = executables
)
