from setuptools import find_packages, setup

setup(name='lhs_connections',
      version='0.0.1',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      py_modules=['lhs_connections'],
      install_requires = [
          'flask',
          'pdfminer',
          'PyPDF2',
          'tabula',
          'pandas']
      )
