#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages
from pathlib import Path

# READMEを読み込む
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# バージョン情報をsrc/cloudwatchlogs_s3_stream_descriptor/__init__.pyから取得
def get_version():
    """src/cloudwatchlogs_s3_stream_descriptor/__init__.pyからバージョン情報を取得"""
    init_file = Path(__file__).parent / "src" / "cloudwatchlogs_s3_stream_descriptor" / "__init__.py"
    if not init_file.exists():
        return "0.1.0"
    
    version_match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', 
                              init_file.read_text(encoding="utf-8"), 
                              re.MULTILINE)
    if version_match:
        return version_match.group(1)
    return "0.1.0"

setup(
    name="cloudwatchlogs-s3-stream-descriptor",
    version=get_version(),
    description="AWS CloudWatch LogsとS3へのストリーム出力を行うPythonライブラリ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="n_h",
    author_email="h.10x64@gmail.com",
    url="https://github.com/h10x64/CloudWatchLogs-S3-Stream-Descriptor",
    # srcフォルダ内のパッケージを検出
    packages=find_packages(where="src"),
    # srcフォルダをパッケージのルートとして指定
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=[
        "boto3>=1.26.0",
        "python-dotenv>=0.19.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="aws cloudwatch logs s3 stream logging",
)

