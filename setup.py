import os
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

requirements = open("requirements/base_requirements.txt", "r").read().split("\n")

setup(
    name='django-heaven',
    version='0.0.3',
    packages=['responses', 'services'],
    include_package_data=True,
    install_requires=requirements,
    license='MIT License',
    description='django-heaven brings structure and order to your django projects',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/knucklesuganda/django-heaven/',
    author='Andrey Ivanov',
    author_email='python.on.papyrus@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
