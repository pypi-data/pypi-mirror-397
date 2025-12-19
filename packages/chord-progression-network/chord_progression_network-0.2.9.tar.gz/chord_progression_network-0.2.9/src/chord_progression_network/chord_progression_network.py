import random
import re
import networkx as nx
import musical_scales
from pychord import Chord

class Generator:
    def __init__(
        self,
        max=8,
        net=None,
        weights=None,
        chord_map=None,
        scale_name='ionian',
        scale_note='C',
        octave=4,
        scale=None,
        tonic=1,
        resolve=1,
        substitute=False,
        sub_cond=None,
        flat=False,
        chord_phrase=False,
        verbose=False,
    ):
        self.max = max
        transitions = [ i for i in range(1, 8) ]
        self.net = net if net is not None else { i: transitions for i in transitions }
        transitions = [ 1 for _ in self.net.keys() ]
        self.weights = weights if weights is not None else { i: transitions for i in self.net.keys() }
        self.scale_name = scale_name
        self.scale_note = scale_note
        self.octave = octave
        self.tonic = tonic
        self.resolve = resolve
        self.substitute = substitute
        self.sub_cond = sub_cond if sub_cond is not None else lambda: random.randint(0, 3) == 0
        self.flat = flat
        self.chord_phrase = chord_phrase
        self.verbose = verbose
        self.scale = scale if scale is not None else self._build_scale()
        self.chord_map = chord_map if chord_map is not None else self._build_chord_map()
        self.graph = self._build_graph()
        self.phrase = None
        self.chords = None

    def _build_chord_map(self):
        scale_maps = {
            'chromatic':  ['m'] * 12,
            'major':      ['', 'm', 'm', '', '', 'm', 'dim'],
            'ionian':     ['', 'm', 'm', '', '', 'm', 'dim'],
            'dorian':     ['m', 'm', '', '', 'm', 'dim', ''],
            'phrygian':   ['m', '', '', 'm', 'dim', '', 'm'],
            'lydian':     ['', '', 'm', 'dim', '', 'm', 'm'],
            'mixolydian': ['', 'm', 'dim', '', 'm', 'm', ''],
            'minor':      ['m', 'dim', '', 'm', 'm', '', ''],
            'aeolian':    ['m', 'dim', '', 'm', 'm', '', ''],
            'locrian':    ['dim', '', 'm', 'm', '', '', 'm'],
        }
        if self.scale_name in scale_maps:
            return scale_maps.get(self.scale_name)
        else:
            return [''] * len(self.scale)

    def _build_scale(self):
        s = musical_scales.scale(self.scale_note, self.scale_name)
        # remove the octave number from the stringified Note:
        s2 = []
        for n in s:
            s2.append(re.sub(r"\d+", "", f"{n}"))
        if self.flat:
            s2 = [ self._equiv(note) for note in s2 ]
        if self.verbose:
            print('Scale:', s2)
        return s2

    def _equiv(self, note, is_chord=False):
        equiv = {
            'C#':  'Db',
            'D#':  'Eb',
            'E#':  'F',
            'F#':  'Gb',
            'G#':  'Ab',
            'A#':  'Bb',
            'B#':  'C',
            'Cb':  'B',
            'Dbb': 'C',
            'Ebb': 'D',
            'Fb':  'E',
            'Gbb': 'F',
            'Abb': 'G',
            'Bbb': 'A',
        }
        if is_chord:
            match = re.search(r"^([A-G][#b]+?)(.*)$", note)
            if match:
                note = match.group(1)
                flavor = match.group(2)
                return equiv.get(note) + flavor if note in equiv else note + flavor
            else:
                return note
        else:
            match = re.search(r"^([A-G][#b]+?)(\d)$", note)
            if match:
                note = match.group(1)
                octave = match.group(2)
                return equiv.get(note) + octave if note in equiv else note + octave
            else:
                return note

    def _build_graph(self):
        g = nx.DiGraph()
        for posn, neighbors in self.net.items():
            for i,neighbor in enumerate(neighbors):
                w = self.weights[posn][i]
                g.add_edge(posn, neighbor, weight=w)
        return g

    def generate(self):
        if len(self.chord_map) != len(self.net):
            raise ValueError('chord_map length must equal number of net keys')

        # build progression of successors of v
        progression = []
        v = None
        for n in range(1, self.max + 1):
            v = self._next_successor(n, v)
            progression.append(v)
        if self.verbose:
            print('Progression:', progression)

        chord_map = self.chord_map
        if self.substitute:
            for i, chord in enumerate(chord_map):
                substitute = self.substitution(chord) if self.sub_cond() else chord
                if substitute == chord and i < len(progression) and self.sub_cond():
                    progression[i] = str(progression[i]) + 't'
                chord_map[i] = substitute
            if self.verbose:
                print('Chord map:', chord_map)

        phrase = [self._tt_sub(chord_map, n) for n in progression]
        self.phrase = phrase
        if self.verbose:
            print('Phrase:', self.phrase)

        if self.chord_phrase:
            if self.flat:
                phrase = [self._equiv(chord, is_chord=True) for chord in phrase]
            return phrase
        else:
            chords = [self._chord_with_octave(chord) for chord in phrase]
            if self.flat:
                chords = [[self._equiv(note) for note in chord] for chord in chords]
            self.chords = chords
            if self.verbose:
                print('Chords:', self.chords)
            return chords

    def _next_successor(self, n, v):
        v = v if v is not None else 1
        s = None
        if n == 1:
            if self.tonic == 0:
                s = self._random_successor(1)
            elif self.tonic == 1:
                s = 1
            else:
                s = self._full_keys()
        elif n == self.max:
            if self.resolve == 0:
                s = self._random_successor(v) or self._full_keys()
            elif self.resolve == 1:
                s = 1
            else:
                s = self._full_keys()
        else:
            s = self._random_successor(v)
        return s

    def _random_successor(self, v):
        successors = list(self.graph.successors(v))
        if not successors:
            return None
        weights = self.weights[v]
        return random.choices(successors, weights=weights, k=1)[0] if successors else None

    def _full_keys(self):
        keys = [k for k, v in self.net.items() if len(v) > 0]
        return random.choice(keys)

    def _tt_sub(self, chord_map, n):
        note = None
        if isinstance(n, str) and 't' in n:
            n = int(n.replace('t', ''))
            # Tritone substitution logic for chromatic scale
            chromatic = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
            idx = chromatic.index(self.scale[n - 1]) if self.scale[n - 1] in chromatic else 0
            note = chromatic[(idx + 6) % len(chromatic)]
            if self.verbose:
                print(f'Tritone: {self.scale[n - 1]} => {note}')
        else:
            note = self.scale[int(n) - 1]
        note = f"{note}" + chord_map[int(n) - 1]
        return note

    def _chord_with_octave(self, chord):
        c = Chord(chord)
        return c.components_with_pitch(root_pitch=self.octave)

    def substitution(self, chord):
        substitute = chord
        if chord in ['', 'm']:
            roll = random.randint(0, 1)
            substitute = chord + 'M7' if roll == 0 else chord + '7'
        elif chord in ['dim', 'aug']:
            substitute = chord + '7'
        elif chord in ['-5', '-9']:
            substitute = f"7({chord})"
        elif chord == 'M7':
            roll = random.randint(0, 2)
            substitute = ['M9', 'M11', 'M13'][roll]
        elif chord == '7':
            roll = random.randint(0, 2)
            substitute = ['9', '11', '13'][roll]
        elif chord == 'm7':
            roll = random.randint(0, 2)
            substitute = ['m9', 'm11', 'm13'][roll]
        if self.verbose and substitute != chord:
            print(f'Substitute: "{chord}" => "{substitute}"')
        return substitute

    def map_net_weights(self, scale_map=None):
        if not scale_map:
            scale_map = {
                'C': '',
                'D': 'm',
                'E': 'm',
                'F': '',
                'G': '',
                'A': 'm',
                'B': 'dim',
            }
        chord_map = list(scale_map.values())
        size = len(scale_map) + 1
        transition = [ i for i in range(1, size) ] # to all nodes
        net = { i: transition for i in range(1, size) } # each node neighbor is all nodes
        weight = [ 1 for _ in range(1, size) ] # equal probability
        weights = { i: weight for i in range(1, size) } # 
        self.graph = self._build_graph()
        return chord_map, net, weights
