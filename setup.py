
from setuptools import setup, find_packages

setup(
  name='mongo_ftdc_draw',
  version='0.1.1',
  author='Vilius Okockis',
  packages=['mongo_ftdc_draw'],
  include_package_data=True,
  license='LICENSE.txt',
  description='visualize mongo diagnostics data',
  long_description=open('README.txt').read(),
  install_requires=[
    "matplotlib",
    "numpy"
  ],
  entry_points={
  	'console_scripts': ['mongo_ftdc_draw = mongo_ftdc_draw:ftdc_main']
  }
)

