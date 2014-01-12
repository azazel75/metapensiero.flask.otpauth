from setuptools import setup, find_packages
import os

version = '0.1'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='metapensiero.flask.otpauth',
      version=version,
      description="A flask application that is able to authenticate on a LinOTP service",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Alberto Berti',
      author_email='alberto@metapensiero.it',
      url='',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['metapensiero', 'metapensiero.flask'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'flask',
          'pastedeploy',
          'pastescript'
      ],
      entry_points="""
      [paste.app_factory]
      main = metapensiero.flask.otpauth.app:app_factory
      """,
      )
