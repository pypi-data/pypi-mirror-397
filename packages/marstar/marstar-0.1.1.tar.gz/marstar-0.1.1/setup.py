from setuptools import setup, find_packages

setup(
    name="marstar",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.7",
    description="An ultimate game platform,available for Tic-Tac-Toe game and Murphy,the best number game ever.Use marstar.guide() to view the guide of this game,required NumPy.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Marcy",
)

