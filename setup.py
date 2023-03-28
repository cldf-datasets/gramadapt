from setuptools import setup


setup(
    name='cldfbench_gramadapt',
    py_modules=['cldfbench_gramadapt'],
    include_package_data=True,
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
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
