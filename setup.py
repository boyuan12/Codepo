from setuptools import setup

setup(
    author="Boyuan Liu",
    author_email="boyuanliu6@yahoo.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development"
    ],
    license="MIT",
    description="This is Git Clone for GitHub Clone (https://github-clone-dj.herokuapp.com)",
    install_requires=["requests", "boto3"],
    keywords="git",
    name="git-clone-dj",
    packages=["git-clone-dj"],
    entry_points={
        "console_scripts": ["gitt=gitt.main:main"]
    },
    py_requires="3.6",
    url="https://github.com/boyuan12/git-clone-dj",
    version="0.0.3"
)