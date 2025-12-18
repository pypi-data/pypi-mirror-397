from setuptools import setup, find_packages

setup(
    name='trex_admin',
    version="1.0.3",
    description="TRex admin package",
    author="Jack Lok",
    packages=find_packages(include=["*.py","trexadmin", "trexadmin.*"]),
    include_package_data=False,   # don’t include non-Python files
    zip_safe=False,
    install_requires=[
      'flask',
      'Jinja2',
      'MarkupSafe',
      'phonenumbers',
      'requests',
      'testfixtures',
      'flask-babel',
      'Flask-CORS',
      'trex-lib',
      'trex-model',
      'trex-mail',
    ],
    entry_points={
        "console_scripts": [
            "trexadmin=trexadmin.__main__:main",   # optional
        ]
    },
)



