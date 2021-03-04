import sys
from fluentpy import wrap
assert len(sys.argv) == 2, \
    """\
Usage: python -m fluentpy 'some code that can access fluent functions without having to import them'
See documentation section 'Easy Shell Filtering with Python' for inspiration."""

# __wrapper_is_sealed = True
exec(sys.argv[1], vars(wrap))
