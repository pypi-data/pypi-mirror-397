from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="newonder_sentry_log",
    version="1.0.1",
    author="wangsw",
    author_email="wangshiwei@xinhuadu.com.cn",
    description="A logging package that integrates with Sentry for Newonder projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/newonder/sentry-log",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            # If there are command-line tools that can be defined here
        ],
    },
)