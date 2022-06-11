.. _population_model:

Population Model
================

A population of people is comprised of "meta-groups." Within a meta-group,
all parameters such as hospitalization rate remain constant with the exception
of contact level. For example, in modeling a university, possible meta-groups
could be undergraduates, graduates, professional students, and faculty/staff.
A meta-group contact matrix encodes how often these meta-groups come into
contact with one another. Within each meta-group, there are multiple groups
that represent varying contact levels.

The :py:mod:`simpar.groups.MetaGroup` class allows one to specify a vector
of number of contacts across meta-groups as well as a vector indicating what
fraction of the meta-group population is in each of these groups.
Alternatively, this can be specified with a truncated `Pareto`_ distribution.
Given a shape parameter :math:`\alpha` and truncation point :math:`ub`, the
fraction of the meta-group population with :math:`i` contacts is
:math:`f(i;\alpha,ub)` where :math:`f` is the probability density function of
the Pareto distribution. Note these values are normalized to sum to 1.

The interactions among individuals within the same meta-group is assumed to be
well-mixed in that the amount of interaction group :math:`i` has with group
:math:`j` is proportional to both groups contact levels and the fraction of the
population of group :math:`j`. Hence, it is `not` assumed that more social
people tend to interact with more social people and vice versa. Similarly,
while the meta-group contact matrix encodes how much contact takes place
between two meta-groups, the interaction between them is assumed to be
well-mixed with respect to the groups that comprise them. See
:py:mod:`simpar.groups.MetaGroup` and :py:mod:`simpar.groups.Population` for
more details.

.. _Pareto: https://en.wikipedia.org/wiki/Pareto_distribution
