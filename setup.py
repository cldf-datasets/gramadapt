from setuptools import setup, find_packages


setup(
    name='cldfbench_gramadapt',
    py_modules=['cldfbench_gramadapt'],
    include_package_data=True,
    packages=find_packages(where='.'),
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'gramadapt=cldfbench_gramadapt:Dataset',
        ],
        'cldfbench.commands': [
            'gramadapt=gramadaptcommands',
        ]
    },
    install_requires=[
        'cldfbench',
        'matplotlib',
        'seaborn',
        'plot_likert',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
