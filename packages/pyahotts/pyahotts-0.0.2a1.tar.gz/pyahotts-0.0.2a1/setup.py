from setuptools import setup, find_packages
import os

BASE = os.path.dirname(__file__)

def get_version():
    """ Find the version of ovos-core"""
    version = None
    version_file = os.path.join(BASE, 'pyahotts', 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if int(alpha):
        version += f"a{alpha}"
    return version

def get_package_data():
    """Function to collect all necessary package data files."""
    data_files = []

    # Include all data files in 'data_tts' directory (e.g., voices, dicts)
    for root, dirs, files in os.walk(f'{BASE}/pyahotts'):
        for file in files:
            data_files.append(os.path.relpath(os.path.join(root, file), 'pyahotts'))

    return data_files


setup(
    name='pyahotts',
    version=get_version(),
    description='AhoTTS - python Text-to-Speech package',
    author='JarbasAI',
    author_email='jarbasai@mailfence.com',
    url='https://github.com/TigreGotico/pyAhoTTS',
    packages=find_packages(include=['pyahotts', 'pyahotts.*']),
    package_data={
        'pyahotts': get_package_data(),
    },
    install_requires=[
        'numpy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)
