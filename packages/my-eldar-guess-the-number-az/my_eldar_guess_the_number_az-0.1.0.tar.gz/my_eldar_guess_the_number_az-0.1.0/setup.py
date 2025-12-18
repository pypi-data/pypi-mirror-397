# setup.py

from setuptools import setup, find_packages

setup(
    name='my-eldar-guess-the-number-az',
    version='0.1.0',
    packages=find_packages(),
    description='Azerbaycan dilində "Ədədi Tap" mini oyunu.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Sizin-Github-Adınız/guess-the-number-az', # GitHub linkinizi qeyd edin
    author='Sizin Adınız',
    author_email='sizin_emailiniz@example.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Games/Entertainment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='game, number, terminal, python, azerbaijan',
    python_requires='>=3.6',
)