# How to execute the unit tests

> ./setup.py test -q

or

> pytest

# How to generate the documentation

> cd docs; make clean html

# How to send patches

Pull requests with unit tests please.

Please note that this project practices Semantic Versioning and [Dependable API Evolution](https://github.com/dwt/Dependable_API_Evolution)

# Release checklist
- Tests run at least in python 3.7
- Increment version
- Update Changelog
- build with $ ./setup.py sdist bdist_wheel
- upload to testpypi as required $ twine upload --repository testpypi dist/fluentpy-*
- Test install and check the new version from pypi
- Tag release
- Push git tags
- upload to pypi as required $ twine upload dist/fluentpy-*

