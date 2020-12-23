Epipeptide metalloprotease yydH
===============================

Based on [Butcher et al., 2007](https://dx.doi.org/10.1128/JB.01181-07).
The profile was built from `yydH_family.fa`, which in turn was built using the
published sequence for yydH of _Bacillus subtilis_ subsp. subtilis str. 168 (`yydH.fa`)
as the seed for a BLAST search against NR, picking the 64 hits with 50+ % identity and
80+ % coverage as of 2018-12-23.

GA and TC values were set to 400, based on picking up the majority of `yydH_family.fa`.
NC was set as the lowest score in `yydH_family.fa`, and confirmed to be above all scores
in `noise.fa` which were taken from lower-scoring BLAST hits of the same query.
