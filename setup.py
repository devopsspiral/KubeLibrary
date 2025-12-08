from pkg_resources import parse_requirements
from pathlib import Path
from setuptools import setup

exec(open("src/KubeLibrary/version.py").read())

with open("README.md", "r") as fh:
    long_description = fh.read()

with Path("requirements.txt").open() as requirements:
    install_requires = [
        str(requirement)
        for requirement in parse_requirements(requirements)
    ]

setup(
    name="robotframework-kubelibrary",
    version=version,
    author="Michał Wcisło",
    author_email="mwcislo999@gmail.com",
    description="Kubernetes library for Robot Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devopsspiral/KubeLibrary",
    license="MIT",
    packages=["KubeLibrary"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
    ],
    keywords="robotframework testing test automation kubernetes",
    python_requires='>=3.6',
    package_dir={'': 'src'},
    install_requires=install_requires,
)
