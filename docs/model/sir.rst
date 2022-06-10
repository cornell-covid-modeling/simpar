.. _sir_model:

SIR Compartmental Model
=======================

The SIR model is a compartmental model which is comprised of three main
compartments: susceptible (S), infected (I), and recovered (R). Additionally,
discovered (D) and hidden (H) compartments keep track of the number of
infected or recovered that have been discovered. The population is divided
into "groups" which interact with one another. Every time period in the
simulation, some people move from susceptible to infected based on internal
group interactions and an external outside rate of infection. The time period
corresponding to an iteration of the simulation is a generation time. Hence, a
person infected in one iteration will be recovered by the next. Furthermore,
people move from hidden to discovered based on an infection discovery and
recovered discovery fraction.

Mathematically, let :math:`k` be the number of groups and :math:`T` be the
number time periods to simulate. Let :math:`S`, :math:`I`, :math:`R`,
:math:`D`, and :math:`H` be :math:`T` by :math:`k` matrices such that
:math:`S[i,j]` is the number of people in group :math:`j` susceptible during
time period :math:`i`. Let :math:`A` be a :math:`k` by :math:`k` matrix
encoding the interactions between groups such that :math:`A[i,j]` is the number
of infections in group :math:`j` caused by a single infection in group
:math:`i`. Let :math:`o` be the vector representing the outside rate of
infection. Lastly, let :math:`a` and :math:`r` be the vectors representing the
infection and recovered discovery fractions respectively.

Given a state at time period :math:`t`, the following state at time period
:math:`t+1` is given as follows.

.. tabularcolumns:: ll

+------------------+-----------------------------------------------------------------+
| :math:`S[t+1] =` | :math:`S[t] - I[t+1]`                                           |
+------------------+-----------------------------------------------------------------+
| :math:`I[t+1] =` | :math:`\min((I[t]A + o) * (S[t] / (S[t] + I[t] + R[t])), S[t])` |
+------------------+-----------------------------------------------------------------+
| :math:`R[t+1] =` | :math:`R[t] + I[t]`                                             |
+------------------+-----------------------------------------------------------------+
| :math:`D[t+1] =` | :math:`D[t] + aI[t+1] + rH[t]`                                  |
+------------------+-----------------------------------------------------------------+
| :math:`H[t+1] =` | :math:`(1-a)I[t+1] + (1-r)H[t]`                                 |
+------------------+-----------------------------------------------------------------+

The :py:mod:`simpar.sim` module implements this exact SIR model.
