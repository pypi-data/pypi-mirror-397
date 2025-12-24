from setuptools import setup, find_packages

setup(
    name='gPCE_model',
    version='0.1.3',
    author='András Urbanics, Bence Popovics, Emese Vastag, Elmar Zander, Noémi Friedman',
    author_email='popbence@hun-ren.sztaki.hu',
    description='Implementing generalized Polynomial Chaos Expansion (gPCE) for uncertainty quantification and surrogate modeling',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/TRACE-Structures/gPCE_model/',
    packages=find_packages(),
    py_modules=['uncertain_variables'],
    install_requires=[
        'numpy',
        'scikit-learn',
        'scipy',
        'uncertain_variables',
        'shap',
        'pandas'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
    ],
)
