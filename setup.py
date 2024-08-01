from setuptools import setup, find_packages

setup(
    name='delta',
    version='0.0.1',
    description='DELTA: Differential Evolution Algorithm for Large-scale Tailored Atomistic Structures',
    author='Wenhao Luo',
    author_email='luowh35@mail2.sysu.edu.cn',
    url='https://github.com/luowh35/DELTA',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'ase'
    ],
    entry_points={
        'console_scripts': [
            'delta=delta.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
