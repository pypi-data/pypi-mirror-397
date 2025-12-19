# 快速开始

## 安装依赖

uv sync

## 作为本地包安装

uv pip install -e .

# Build package

python setup.py sdist bdist_wheel


# publish package

twine upload dist/* 