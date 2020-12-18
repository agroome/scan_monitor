import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='scan_monitor',
    version='0.',
    author='Andy Groome',
    author_email='groome.andy@gmail.com',
    description='Monitor Tenable.sc scans and notify when status changes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/agroome/scan_monitor',
    packages=['scan_monitor'],
    install_requires=[
        'Click',
        'Jinja2',
        'pytenable',
        'python-systemd',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'scan_monitor=scan_monitor.app:start_monitor',
            'configure=scan_monitor.cli:configure'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Ubuntu',
    ],
    python_requires='>=3.6',
)
