from importlib.metadata import entry_points
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.readlines()

setuptools.setup(
    name="set_pass",
    version="1.0.0",
    author="Kol",
    author_email="skolchin@gmail.ru",
    description="PASS package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skolchin/pass",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': ['pass=set_pass.set_pass:main'],
    }
)
