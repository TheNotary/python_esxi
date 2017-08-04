from setuptools import setup

setup(name='python_esxi',
      version='0.1',
      description='An internal tool helping me work with ESXi as infra-code',
      url='https://github.com/thenotary/python_esxi',
      author='TheNotary',
      author_email='TheNotary@example.com',
      license='MIT',
      packages=['python_esxi'],
      install_requires=[
          'pyVmomi',
          'paramiko==2.2.1',
          'pyOpenSSL==16.2.0',
      ],
      scripts=['bin/python_esxi'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
