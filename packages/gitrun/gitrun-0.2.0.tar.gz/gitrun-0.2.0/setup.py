from setuptools import setup, find_packages
setup(
    name="gitrun",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["requests>=2.25.0"],
    entry_points={"console_scripts": ["gitrun=gitrun.cli:main"]},
)
