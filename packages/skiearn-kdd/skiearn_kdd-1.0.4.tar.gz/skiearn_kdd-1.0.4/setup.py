from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='skiearn-kdd',
    version='1.0.4',
    author='KDD Study Team',
    description='Interactive Knowledge Discovery & Data Mining (KDD) study guide',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/skiearn',
    packages=find_packages(),
    package_data={
        'skiearn': ['docs/*.txt'],
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='kdd data-mining machine-learning statistics study-guide education data-science',
    python_requires='>=3.7',
    project_urls={
        'Bug Tracker': 'https://github.com/yourusername/skiearn/issues',
        'Documentation': 'https://github.com/yourusername/skiearn',
        'Source Code': 'https://github.com/yourusername/skiearn',
    },
)
