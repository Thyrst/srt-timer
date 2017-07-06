from setuptools import setup

VERSION = '0.1'
URL = 'https://github.com/Thyrst/srt-timer'

description = open('README.rst').read()

setup(
    name='srt-timer',
    version=VERSION,

    description='Simple script for saving difference of two subtitle timings. ' \
                'You can than easily convert subtitle from one timing to another.',
    long_description=description,
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

    install_requires=[
        'srt',
    ],

    keywords='srt subtitles timing',
    scripts=['srt_timer.py'],
    py_modules=['sdiff'],
)
