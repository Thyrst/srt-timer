from setuptools import setup

VERSION = '0.2'
URL = 'https://github.com/Thyrst/srt-timer'

description = open('README.rst').read()
changelog = open('CHANGELOG.rst').read()

setup(
    name='srt-timer',
    version=VERSION,

    description='Simple script for saving difference of two subtitle timings. ' \
                'You can than easily convert subtitle from one timing to another.',
    long_description=description + changelog,
    url=URL,
    download_url='%s/archive/%s.tar.gz' % (URL, VERSION),

    author='Thyrst',
    author_email='thyrst@seznam.cz',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Text Processing',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='srt subtitles timing',

    install_requires=[
        'srt',
    ],

    entry_points={
        'console_scripts': ['srt_timer=srt_timer:main'],
    },
    scripts=['srt_timer.py'],
    py_modules=['sdiff'],
)
