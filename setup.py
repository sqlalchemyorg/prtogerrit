from setuptools import setup


setup(name='prtogerrit',
      version=1.0,
      description="prtogerrit",
      classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Programming Language :: Python',
      'Programming Language :: Python :: Implementation :: CPython',
      ],
      author='Mike Bayer',
      author_email='mike@zzzcomputing.com',
      url='http://bitbucket.org/zzzeek/prtogerrit',
      license='MIT',
      packages=["bbutils"],
      zip_safe=False,
      install_requires=['requests', 'lxml'],
      entry_points={
        'console_scripts': [
            'prtogerrit = prtogerrit.cmd:main',
        ],
      }
)
