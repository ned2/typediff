from setuptools import setup, find_packages


setup(
    name='typediff',
    version='0.1',
    py_modules=['typediff'],
    install_requires=[
        'flask',
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={'typediff': ['bin/*']},
    entry_points={'console_scripts': [
        'typediff=typediff.typediff:main',
        'grammar-utils=typediff.grammar_utils:main',
        'type-stats=typediff.type_stats:main',
        'parseit=typediff.parseit:main',
        'queryex=typediff.queryex:main',
    ]}
)
