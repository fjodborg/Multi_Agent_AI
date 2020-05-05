"""Setup installation file."""
from setuptools import setup, find_packages

setup(
    name="multi_sokoban",
    version="0.2.0",
    description="Multi-Agent AI Sokoban solver",
    author="some students at DTU",
    author_email="",
    keywords="AI multi-agent-ai python PDDL",
    packages=find_packages(),
    install_requires=["numpy"],
)
