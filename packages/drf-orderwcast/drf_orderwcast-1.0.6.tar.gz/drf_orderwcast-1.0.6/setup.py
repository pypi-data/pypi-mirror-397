from setuptools import setup


with open('README.md') as f:
    README = f.read()

VERSION = '1.0.6'
URL = 'https://github.com/keter2002/drf-orderwcast'
DESCRIPTION = 'A Django REST Framework OrderingFilter like class that handles sort with casting'

setup(
    name='drf-orderwcast',
    version=VERSION,
    url=URL,
    license='MIT',
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    author='João Manica',
    author_email='joaoedisonmanica@gmail.com',
    packages=['drf_orderwcast'],
    include_package_data=True,
    install_requires=[
        'djangorestframework',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
