from setuptools import setup, find_packages

setup(
    name="pysi-kdd",
    version="1.0.0",
    author="User",
    description="A comprehensive KDD and Data Mining code snippet reference package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pysi",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "scipy",
        "matplotlib",
        "seaborn",
        "imbalanced-learn",
        "statsmodels",
        "xgboost",
        "shap"
    ],
)
