#!/usr/bin/env python
from distutils.core import setup

setup(
    name='PILasOPENCV',
    version='2.4',
    author='Andreas Bunkahle',
    author_email='abunkahle@t-online.de',
    description='Wrapper for Image functions which are used and called in the manner of the famous PIL/Pillow module but work internally with OpenCV.',
    license='MIT',
    py_modules=['PILasOPENCV'],
    python_requires='>=2.7',
    url='https://github.com/bunkahle/PILasOPENCV',
    long_description=open('README.txt').read(),
    platforms = ['any'],
    install_requires=['numpy', 'opencv-python', 'freetype-py', 'mss', 'gif2numpy', 'numpy2gif'],
    keywords = 'PIL OPENCV wrapper',
    classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'],
)
