#!/usr/bin/env python
from distutils.core import setup

setup(
    name='PILasOPENCV',
    version='1.0',
    author='Andreas Bunkahle',
    author_email='abunkahle@t-online.de',
    description='Wrapper for Image functions which are used and called in the manner of the famous PIL/Pillow module but work internally with OpenCV.',
    license='MIT',
    py_modules=['PILasOPENCV'],
    python_requires='>=2.7',
    url='https://github.com/bunkahle/particlescv2',
    long_description=open('README.md').read(),
    platforms = ['any'],
    install_requires=['numpy', 'opencv-python', 'freetype-py']
)
