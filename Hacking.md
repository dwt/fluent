# How to execute the unit tests

> ./setup.py test -q

# How to generate the documentation

> cd docs; rm -rf _build; make html

# How to send patches

With unit tests please.
Please note that this project practices Semantic Versioning and [Dependable API Evolution](https://github.com/dwt/Dependable_API_Evolution)

# Release checklist
- Tests run at least in python 3.5
- Ensure pandoc is installed (to get nicer readme output for pypi)
- Increment version and tag
- upload new build with $ ./setup.py sdist upload
