# myproject/setup.py

from setuptools import setup, find_packages

setup(
    name="endee-langchain",
    version="0.1.1",
    packages=find_packages(include=['endee_langchain', 'endee_langchain.*']),
    install_requires=[
        # List your dependencies here
        "langchain>=0.3.25",
        "langchain-core>=0.3.59",
        "endee>=0.1.4",
        "numpy",
    ],
    author="Endee Labs",
    author_email="support@endee.io",
    description="High Speed Vector Database for Faster and Efficient  ANN Searches with LangChain",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://endee.io",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)