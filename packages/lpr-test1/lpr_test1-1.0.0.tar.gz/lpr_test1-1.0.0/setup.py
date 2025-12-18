import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="lpr-test1",
  version="1.0.0",
  author="lpr",
  author_email="948392651@qq.com",
  description="test package",
  long_description=long_description,
  long_description_content_type="text/markdown",
  packages=setuptools.find_packages()
)