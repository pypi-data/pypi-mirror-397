import io

from setuptools import find_packages, setup

long_description = io.open("README.md", encoding="utf-8").read()
print(find_packages())
setup(
    name='opencv_gst_rtmp',
    version='0.1.1',    
    description='Push opencv frame to rtmp server using gstreamer',
    url='https://github.com/nguyencobap/opencv_gst_rtmp',
    author='Nguyen Hai Nguyen',
    author_email='nguyenhainguyen97@gmail.com',
    license='MIT License',
    python_requires=">=3.5",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['gstreamer', 'gst', 'opencv', 'rtmp'],
    install_requires=['opencv-python>=4.6.0.66',
                        'pycairo>=1.20.1',
                        'PyGObject>=3.42.2'
                        ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Video',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3.8',
    ],
)
