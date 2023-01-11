#!/usr/bin/env python

from distutils.core import setup

setup(name='xcom_s3_backend',
      version='1.0',
      description='Custom XCom backend implementation for Airflow, with data serialization to S3.',
      author='Aleksei Solovev',
      author_email='lelkaklel@gmail.com',
      url='https://github.com/lelkaklel/airflow-xcom-s3',
      py_modules = ['xcom_s3_backend'],
     )