# TODO

The get_isolated() method is assuming all of those in the discovered
compartment are discovered in generation. Alternatively, it could assume
that none of them are but that would mess up how we use the simulator with
positive arrival tests that are discovered. We need a way to delineate this.

I am a little fuzzy on how generation time should be set. If it should be the
function of some other parameters, it should be computed explicitly and not be
a user-defined parameter.

I think there is some inconsistency and things that could be made more clear
with regards to units. Specifically, if something is per day or per generation
time and if something is infections or contact units. I think contacts are
being interpreted as if they are in generation time right now but we
probably want that to be per day. Outside rate is also in generation time.

In the current view, antigen and pcr both can detect a hidden recovered which
does not reflect reality. This is probably a complication we should warn about
but not implement.

As a general note, as of [7-10-22], we have just completed a large refactor and
it would be good to have more eyes go through the code/documentation and add
more test cases especially for the groups and trajectory modules.
