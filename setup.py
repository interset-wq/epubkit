from setuptools import setup, find_packages

setup(
    name="epubkit",
    version="0.1.0",
    description="A library to convert Markdown or HTML to EPUB eBooks",
    long_description="""epubkit is a Python library that allows you to convert Markdown or HTML files into EPUB eBooks. It uses the latest EPUB specification and standard library for zip compression.""",
    author="interset-wq",
    author_email="intersetwq@gmail.com",
    url="https://github.com/interset-wq/epubkit",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "markdown",
        "pillow"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)