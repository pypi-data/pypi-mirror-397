from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="boxjenkins",
    version="0.1.0",
    author="Gerson RS",
    author_email="",
    description="Implementação completa do ciclo Box-Jenkins para modelagem ARIMA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GersonRS/boxjenkins",
    project_urls={
        "Bug Reports": "https://github.com/GersonRS/boxjenkins/issues",
        "Source": "https://github.com/GersonRS/boxjenkins",
        "Documentation": "https://github.com/GersonRS/boxjenkins#readme",
    },
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.10",
        ],
    },
)
