# Garden test

41 phone photos of panicle hydrangeas, late October, 9 groups of photos taken in a row.
Stage is scored on the 23 photos that clearly show flowers.

## Health (every photo is normal autumn)

| method | right (autumn, or healthy for the old labels) | false alarm (says disease, wilting or yellowing) |
|---|---|---|
| zero-shot, old labels | 0% | 100% |
| zero-shot, with autumn label | 46% | 54% |
| trained on internet photos | 24% | 76% |
| trained + garden photos (unseen groups) | 100% | 0% |

Answers the old zero-shot gave: leaf_spot 9, wilting 13, yellowing 19

## Stage (blooming vs fading_blooms)

| method | accuracy |
|---|---|
| always guess the most common stage | 74% |
| zero-shot | 52% |
| trained on internet photos | 70% |
| trained + garden photos (unseen groups) | 74% |

## Read this before trusting the numbers

- Health in the garden photos has only ONE true answer (autumn). A model that always says 'autumn' scores 100% here. In the trained + garden row, 'autumn' also comes only from phone photos, so the model may be learning 'phone photo of a garden' instead of 'autumn'. A fair test needs healthy summer photos and some diseased leaves from the same garden.
- Groups are photos taken one after another, not confirmed separate bushes, so leakage between train and test is possible.
- Stage has 23 photos and one season. Treat differences of a few photos as noise.
