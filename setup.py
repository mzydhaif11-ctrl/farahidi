from setuptools import setup, find_packages

setup(
    name="farahidi-engine",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
    ],
    description="محرك لغوي عربي هجين يعتمد على التخزين المحلي والذكاء الاصطناعي",
    author="Mzydhai11-ctrl",
    author_email="mzydhaif11@gmail.com",
    url="https://github.com/mzydhai11-ctrl/farahidi",
)
