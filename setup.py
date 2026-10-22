from setuptools import setup, find_packages

setup(
    name="farahidi-engine",
    version="0.4.0",
    packages=find_packages(),
    install_requires=[
        "transformers>=4.35",
        "torch>=2.0",
        "accelerate>=0.25",
        "sentencepiece>=0.1.99",
    ],
    description="محرك لغوي عربي محلي بالكامل — بدون أي API خارجي 🔒🇸🇦",
    author="Mzydhai11-ctrl",
    author_email="mzydhaif11@gmail.com",
    url="https://github.com/mzydhai11-ctrl/farahidi",
)
