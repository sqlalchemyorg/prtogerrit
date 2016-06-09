from setuptools import setup


setup(
    name='prtogerrit',
    version=1.0,
    description="Transfer pull requests to Gerrit",
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
    packages=["prtogerrit"],
    zip_safe=False,
    install_requires=['requests', 'lxml'],
    entry_points={
        'console_scripts': [
            'prtogerrit = prtogerrit.cmd:main',
        ],
    }
)
