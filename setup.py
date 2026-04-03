from setuptools import setup, find_packages

setup(
    name='ai-trader',
    version='0.1.0',
    author='zhangyan8216',
    author_email='your_email@example.com',
    description='A trading algorithm powered by AI',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'scikit-learn',
        'tensorflow',  # or 'pytorch'
        'keras'
    ],
    entry_points={
        'console_scripts': [
            'ai-trader=main:run',
        ],
    },
)