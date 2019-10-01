# Damage state transitions

This output collects the number of buildings that go from one
damage state to another one according to the event for which we
get the intensity file and the fragility functions.

You can think of it as a table:

| Building class | From damage state | To damage state | Number of affected buildings |
|----------------|-------------------|-----------------|------------------------------|
| RC1            |                 0 |               1 |                          100 |
| RC1            |                 0 |               2 |                           50 |
| RC1            |                 0 |               3 |                           25 |
| RC1            |                 0 |               4 |                           10 |
| ...            |               ... |             ... |                          ... |
| RC1            |                 1 |               2 |                            3 |
| RC1            |                 1 |               3 |                            2 |
| ...            |               ... |             ... |                          ... |
| RC2            |                 0 |               1 |                           20 |
| ...            |               ... |             ... |                          ... |


This kind of table fill be filled for every geo cell in the exposure model, so that we
can compute the overall loss for each of the cells later.
