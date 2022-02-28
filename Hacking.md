
# How to work on fluenpty

## Execute the unit tests

    ./setup.py test -q

or `pytest` or `tox` (to test all supported python versions).

## Generate the documentation

    cd docs; make clean html

or

    sphinx-autobuild doc doc/_build/html

to work on it while it live updates

## Send patches

Pull requests with unit tests please. Bonus points if you add release notes.

Please note that this project practices [Semantic Versioning](https://semver.org) and [Dependable API Evolution](https://github.com/dwt/Dependable_API_Evolution)

## Release checklist

- Tests run at least in all supported versions of python. Use `tox`
- Increment version
- Update Changelog
- build with $ ./setup.py sdist bdist_wheel
- upload to testpypi as required $ twine upload --repository testpypi dist/fluentpy-*
- Test install and check the new version from pypi
- Tag release
- Push git tags
- upload to pypi as required $ twine upload dist/fluentpy-*

