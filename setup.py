import os
from setuptools import find_packages, setup


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-heaven',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='django-heaven brings structure and order to your django projects',
    long_description=README,
    url='https://www.example.com/',
    author='Andrey Ivanov',
    author_email='python.on.papyrus@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.1.6',
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
