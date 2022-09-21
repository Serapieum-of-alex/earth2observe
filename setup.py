from setuptools import find_packages, setup

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

# requirements = [line.strip() for line in open("requirements.txt").readlines()]
# requirements = requirements[1:]

test_requirements = [
    "pytest>=3",
]

setup(
    name="earth2observe",
    version="0.1.1",
    description="remote sensing package",
    author="Mostafa Farrag",
    author_email="moah.farag@gmail.come",
    url="https://github.com/MAfarrag/earthobserve",
    keywords=["remote sensing", "ecmwf"],
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    license="GNU General Public License v3",
    zip_safe=False,
    packages=find_packages(include=["earth2observe", "earth2observe.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    # install_requires=requirements,
    # entry_points={
    #     'console_scripts': [
    #         'earth2observe=earth2observe.cli:main',
    #     ],
    # },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: GIS",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
    ],
)
