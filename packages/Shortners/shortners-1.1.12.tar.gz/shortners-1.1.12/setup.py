from setuptools import setup, find_packages
from Shortners import DATA01, DATA02, DATA03
from Shortners import licence, version
from Shortners import pythons, appname
from Shortners import install, clinton
from Shortners import mention, profile

with open("README.md", "r") as mess:
    description = mess.read()

setup(name=appname,
      url=profile,
      author=clinton,
      version=version,
      license=licence,
      keywords=mention,
      description=DATA03,
      classifiers=DATA02,
      author_email=DATA01,
      python_requires=pythons,
      packages=find_packages(),
      install_requires=install,
      long_description=description,
      long_description_content_type="text/markdown")
