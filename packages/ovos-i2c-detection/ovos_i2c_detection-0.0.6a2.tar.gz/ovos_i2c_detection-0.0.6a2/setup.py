import os
from setuptools import setup

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def get_version():
    """ Find the version of the package"""
    version = None
    version_file = os.path.join(BASEDIR, 'ovos_i2c_detection/version.py')
    major, minor, build, alpha, post = (None, None, None, None, None)
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
            elif 'VERSION_POST' in line:
                post = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if alpha and int(alpha) > 0:
        version += f"a{alpha}"
    elif post and int(post) > 0:
        version += f"post{post}"
    return version


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
        requirements = f.read().splitlines()
        if 'MYCROFT_LOOSE_REQUIREMENTS' in os.environ:
            print('USING LOOSE REQUIREMENTS!')
            requirements = [r.replace('==', '>=').replace('~=', '>=') for r in requirements]
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


with open(f"{BASEDIR}/README.md", "r") as f:
    long_description = f.read()

setup(
    name='ovos_i2c_detection',
    version=get_version(),
    url='https://github.com/OpenVoiceOS/ovos_i2c_detection',
    license='MIT',
    author='builderjer',
    author_email='builderjer@gmail.com',
    description='i2c detection for some devices',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=required("requirements.txt"),
    packages=['ovos_i2c_detection'],
)
