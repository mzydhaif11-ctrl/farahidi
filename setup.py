from setuptools import setup, find_packages

setup(
    name="farahidi-engine",
    version="0.2.0",
    description="محرك المعجم العربي الحتمي مع دعم الذكاء الاصطناعي كطبقة احتياطية",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.4.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Arabic",
    ],
    python_requires=">=3.7",
)
