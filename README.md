# deterministic-sim

This repo was factored out from the cornell-modeling repo and served as the
deterministic simulation used to make decisions for the Cornell Spring 2022
semester. It is currently in the process of being converted to a Python
package with private data removed.

Note: The previous `scenario.py` script was factored out into its own repo
`amps` which is now a dependency. The amps Python package has yet to be
published to [PyPI](https://pypi.org) which allows for `pip install`. In any
case, the preferred setup will be to clone the `amps` repo. From there, you
can navigate to that directory and run

```pip install -e .```

to use it as you would any other Python package where the `-e` flag indicates
that any changes to the source code will automatically be reflected in the
installation. Contact Henry Robbins (hwr26) with any questions.
