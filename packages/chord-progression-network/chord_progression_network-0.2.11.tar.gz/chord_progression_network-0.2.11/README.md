# Chord Progression Network
Network transition chord progression generator

## DESCRIPTION

This class generates network transition chord progressions. The transitions are given by a `net` of scale positions, and the chord "flavors" are defined by a `chord_map` of types. The chords that are returned are either named chords or lists of three or more named notes with octaves.

The chord types are as follows:
```
'' (i.e. an empty string) means a major chord.
'm' signifies a minor chord.
'7' is a seventh chord
'M7' is a major 7th chord and 'm7' is a minor 7th.
'dim' is a diminished chord and 'aug' is augmented.
'9', '11', and '13' are extended 7th chords.
'M9', 'M11', and 'M13' are extended major-7th chords.
'm9', 'm11', and 'm13' are extended minor-7th chords.
```

The scale must be specified with one of the known scales listed on the [musical-scales](https://pypi.org/project/musical-scales/) page. A custom `scale` of named notes (with appropriate `net` and `chord_map` attributes) may also be given. Traditional modes (Ionian, Dorian, etc) have known `chord_map`s. For all other scales, a `chord_map` should be given in the constructor.

For the traditional modes, the `chord_map`s are as follows: The "Ionian" mode (`major` scale) is `['', 'm', 'm', '', '', 'm', 'dim']`. "Dorian" is `['m', 'm', '', '', 'm', 'dim', '']`, etc. A "chromatic" scale is all minors.

The `tonic` attribute means that if the first chord of the progression is being generated, then for `0` choose a random successor of the first chord, as defined by the `net` attribute. For `1`, return the first chord in the scale. For any other value, choose a random value of the entire scale.

The `resolve` attribute means that if the last progression chord is being generated, then for `0` choose a random successor. For `1`, return the first chord in the scale, and for any other value, choose a random value of the entire scale. In all other cases (i.e. the middle chords of the progression), choose a random successor.

By default, all chords and notes with accidentals are returned as sharps. If you want flats, set the `flat` attribute to `True` in the constructor.

If the `substitute` attribute is set to `True`, then the progression chords are subject to extended, "jazz" chord, including tritone substitution. This module performs chord substitution depending on the `sub_cond` lambda that acts 30% of the time. For now, for this work-in-progress advanced option, please see the `substitution()` method in the source...

Please see the `Tests.py` program, in this distribution for usage hints. :)

## SYNOPSIS
```python
from chord_progression_network import Generator

neighbors = [ i for i in range(1, 8) ] # 1 through 7
transitions = [ 1 for _ in neighbors ] # equal probability

g = Generator( # defaults
    max=8,
    scale_note='C',
    scale_name='major',
    octave=4,
    net={
        1: neighbors,
        2: neighbors,
        3: neighbors,
        4: neighbors,
        5: neighbors,
        6: neighbors,
        7: neighbors,
    },
    weights={
        1: transitions,
        2: transitions,
        3: transitions,
        4: transitions,
        5: transitions,
        6: transitions,
        7: transitions,
    },
    chord_map=[ '', 'm', 'm', '', '', 'm', 'dim' ],
    tonic=1,
    resolve=1,
    flat=False,
    chord_phrase=False,
    substitute=False,
    verbose=False,
)
phrase = g.generate()

# Use a different set of chords with equal transition probability:
g = Generator()
scale_map = { 'G': 'm', 'Bb': '', 'D': 'm' }
g.chord_map, g.net, g.weights = g.map_net_weights(scale_map=scale_map)
phrase = g.generate()
```

## MUSICAL EXAMPLES
```python
from music21 import chord, stream
from chord_progression_network import Generator

g = Generator(verbose=True)
phrase = g.generate()

s = stream.Score()
p = stream.Part()

for notes in phrase:
    p.append(chord.Chord(notes, type='whole'))

s.append(p)
s.show()
```

```python
from music21 import chord, duration, stream
from chord_progression_network import Generator
from random_rhythms import Rhythm

r = Rhythm(durations=[1, 3/2, 2])
motifs = [ r.motif() for _ in range(4) ]

s = stream.Score()
p = stream.Part()

# simplistic example: all ones = equal probability
weights = [ 1 for _ in range(1,6) ]

g = Generator(
    scale_name='whole-tone scale',
    net={
        1: [2,3,4,5,6],
        2: [1,3,4,5,6],
        3: [1,2,4,5,6],
        4: [1,2,3,5,6],
        5: [1,2,3,4,6],
        6: [1,2,3,4,5],
    },
    weights={ i: weights for i in range(1,7) },
    chord_map=['m'] * 6,
    substitute=True,
)

for m in motifs:
    g.max = len(m)
    phrase = g.generate()
    for i, d in enumerate(m):
        c = chord.Chord(phrase[i])
        c.duration = duration.Duration(d)
        p.append(c)

s.append(p)
s.show()
```