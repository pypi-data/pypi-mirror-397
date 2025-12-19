import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="example-pkg-DeNeRATe",
  version="0.0.1",
  author="Jiayuxuan Yang",
  author_email="1229836346@qq.com",
  description="A small example package",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/DeNeRATe-cool/BUAA_Algorithm_resources",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)