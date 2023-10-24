from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="loki-logger-handler",
    version="0.0.1",
    author="Xente",
    description="Handler designed for transmitting logs to Grafana Loki in JSON format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xente/loki-logger-handler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="loki, loguru, logger, handler",
    install_requires=[],
    test_suite="tests",
    license="MIT",
    python_requires=">=3.6",
)
