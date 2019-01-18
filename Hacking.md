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
- Increment version and tag
- upload new build with $ ./setup.py sdist upload
