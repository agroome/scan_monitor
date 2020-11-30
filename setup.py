import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scan_monitor",
    version="0.0.1",
    author="Andy Groome",
    author_email="groome.andy@gmail.com",
    description="Monitor and scan status",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agroome/scan_monitor",
    packages=["scan_monitor"],
    install_requires=["python-dotenv", "pytenable"],
    entry_points={
        "console_scripts": [
            "scan_monitor = scan_monitor.scan_monitor:polling_loop"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
