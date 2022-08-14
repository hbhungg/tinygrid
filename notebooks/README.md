# Some thoughts and findings.

## Problems
1. Normalization seem to be making the MASE score worst for some dataset.
2. How should we clean the data. There are bunch of 0s lying around. Which I would assume is noise.
3. Should we use standardize to hide away outliers? Normalization seem to only be good in deep learning only.
4. Denormalize does not affect the performance. Kinda obv when I think about it.
5. Day and year sin cos value seem to not be contributing anything to the prediction.

## Potential Solution
1. TDB.
2. Manually clean out the 0s leading or ending in a dataset. These are the easiest. Appear in Solar0 for example from 0:2460.
3. Try both.
4. Duhh.
5. Try with and without. If it truly is the case, then less work for us I guess. Maybe find a better way to represent day and year.