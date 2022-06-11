.. _sir_model:

SIR Compartmental Model
=======================

The SIR model is a compartmental model which is comprised of three main
compartments: susceptible (S), infected (I), and recovered (R). Additionally,
discovered (D) and hidden (H) compartments keep track of the number of
infected or recovered that have been discovered. The population is divided
into "groups" which interact with one another. Every generation in the
simulation, some people move from susceptible to infected based on internal
group interactions and an external outside rate of infection. The length
of a generation is referred to as a generation time. A person infected in one
generation will be recovered by the next. Furthermore, people move from hidden
to discovered based on an infection discovery and recovered discovery fraction.
The infection discovery fraction denotes the fraction of infected population
that is discovered in the generation in which they are infected. The recovered
discovery fraction denotes the fraction of the hidden recovered population
that become discovered in every generation. This is non-standard and arises
from a desire to model the "discovery" of infections as a result of testing.

Mathematically, let :math:`k` be the number of groups and :math:`T` be the
number generations to simulate. Let :math:`S`, :math:`I`, :math:`R`,
:math:`D`, and :math:`H` be :math:`T` by :math:`k` matrices such that
:math:`S[i,j]` is the number of people in group :math:`j` susceptible during
generation :math:`i`. State variables in SIR models are usually **fractions**
of an overall population but these are **counts**. Let :math:`A` be a :math:`k`
by :math:`k` matrix encoding the interactions between groups such that
:math:`A[i,j]` is the number of infections in group :math:`j` caused by a
single infection in group :math:`i`. Let :math:`o` be the vector representing
the outside rate of infection such that :math:`o[i]` is the count of infections
per generation time occurring in group :math:`i` as a result of outside
infection. Lastly, let :math:`a` and :math:`r` be the vectors representing the
infection and recovered discovery fractions respectively.

Given a state at generation :math:`t`, the following state at generation
:math:`t+1` is given as follows.

.. tabularcolumns:: ll

+------------------+-----------------------------------------------------------------+
| :math:`S[t+1] =` | :math:`S[t] - I[t+1]`                                           |
+------------------+-----------------------------------------------------------------+
| :math:`I[t+1] =` | :math:`\min((I[t]A + o) * (S[t] / (S[t] + I[t] + R[t])), S[t])` |
+------------------+-----------------------------------------------------------------+
| :math:`R[t+1] =` | :math:`R[t] + I[t]`                                             |
+------------------+-----------------------------------------------------------------+
| :math:`D[t+1] =` | :math:`D[t] + a \cdot I[t+1] + r \cdot H[t]`                    |
+------------------+-----------------------------------------------------------------+
| :math:`H[t+1] =` | :math:`(1-a) \cdot I[t+1] + (1-r) \cdot H[t]`                   |
+------------------+-----------------------------------------------------------------+

The :py:mod:`simpar.sim` module implements this exact SIR model.
