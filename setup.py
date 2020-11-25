import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scan-monitor",
    version="0.0.1",
    author="Andy Groome",
    author_email="agroome@tenable.com",
    description="Monitor and scan status",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agroome/scan_monitor",
    packages=setuptools.find_packages(),
    install_requires=['python-dotenv', 'pytenable'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
