from pathlib import Path
from setuptools import setup

exec(Path("src/KubeLibrary/version.py").read_text())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

install_requires = [
    line.strip()
    for line in Path("requirements.txt").read_text().splitlines()
    if line.strip() and not line.strip().startswith("#")
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
    license_expression="MIT",
    packages=["KubeLibrary"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
    ],
    keywords="robotframework testing test automation kubernetes",
    python_requires='>=3.6',
    package_dir={'': 'src'},
    install_requires=install_requires,
)
