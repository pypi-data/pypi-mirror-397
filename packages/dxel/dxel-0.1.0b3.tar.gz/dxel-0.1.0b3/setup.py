from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dxel",
    version="0.1.0b3",
    author="Prashant Gavit",
    author_email="prashant.gavit115@gmail.com",
    description="An AI-powered data analysis agent for intelligent data insights and visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prashantgavit/dxel",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11,<3.13",
    keywords="data-analysis ai gemini llm agent data-science"
)
