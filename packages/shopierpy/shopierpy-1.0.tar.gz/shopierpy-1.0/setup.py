from setuptools import setup

LONG_DESCRIPTION = """
# Shopier Python SDK (TR)

Unofficial Shopier SDK with CLI, donation mode and webhook verification.

## Features
- shopier pay
- shopier donate
- Webhook verification
- Automatic HTML payment form
- Secure HMAC signature

## Install
pip install shopierpy

## Commands
shopier init
shopier pay
shopier donate
shopier talimat
"""

setup(
    name="shopierpy",
    version="1.0",
    author="Muhammed Yusuf Özkaya",
    description="Shopier Python SDK + CLI + Donate + Webhook",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    py_modules=["shopier"],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "shopier=shopier:main"
        ]
    },
    license="MIT",
)