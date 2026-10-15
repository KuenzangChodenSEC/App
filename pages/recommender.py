"""
recommender.py - the LamGo recommendation algorithm (no tkinter, easy to test).

HOW A PLACE IS SCORED
---------------------
Every place gets five sub-scores, each between 0 and 1:

    text      how well the place matches the words the user just typed
              (name, dzongkhag, category, description, synonyms, small typos)
    interest  how much the user likes this kind of place, learned from what they
              open, save, review and search (older actions slowly count less)
    recent    how well the place matches the user's recent searches
              (the newest search counts most)
    near      how close the place is to the user's live / chosen location
    quality   star rating, adjusted for how many people rated it

and the final score is a weighted sum:

    when searching :  0.50 text + 0.15 interest + 0.10 recent + 0.15 near + 0.10 quality
    no search text :  0.35 interest + 0.20 recent + 0.25 near + 0.20 quality
    "near me" typed:  the `near` weight is raised so close places come first

With a brand-new user (no activity) and no location, the order simply falls back to
"best rated first", so the app never shows an empty or random list.

Each recommendation also carries short human-readable `reasons`
("Near you - ~35 km", "You like Cultural Sites", ...) so the user can see WHY.
"""
import difflib
import json
import math
import os
import re
from functools import lru_cache

from .dzongkhag_data import DZONGKHAGS, dzongkhag_by_name, dzongkhag_of_place
from .geo import haversine_km
from .database import get_places
PLACES = get_places()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACTIVITY_FILE = os.path.join(BASE_DIR, 'user_activity.json')

MIN_TEXT = 0.20                 # a place must match the typed words at least this much
MAX_RECENT = 10                 # how many recent searches are remembered
RECENT_DECAY = 0.7              # each older search counts 70% of the one after it
ACTIVITY_DECAY = 0.97           # every new action slightly reduces the weight of older ones

WEIGHTS_SEARCH = {'text': .50, 'interest': .15, 'recent': .10, 'near': .15, 'quality': .10}
WEIGHTS_BROWSE = {'text': 0, 'interest': .35, 'recent': .20, 'near': .25, 'quality': .20}
WEIGHTS_NEAR_ME = {'text': .40, 'interest': .10, 'recent': .05, 'near': .35, 'quality': .10}

STOPWORDS = {
    'a', 'an', 'the', 'in', 'at', 'of', 'to', 'for', 'and', 'or', 'with', 'from', 'on', 'i', 'my',
    'want', 'visit', 'visiting', 'go', 'going', 'place', 'places', 'best', 'top', 'trip', 'travel',
    'around', 'bhutan', 'good', 'some', 'show', 'find', 'where', 'what', 'is', 'are', 'can', 'see',
}
NEAR_ME_WORDS = {'near', 'nearby', 'me', 'closest', 'nearest', 'close'}

# word -> related words (so "hike" also finds places in the "Nature & Hiking" category, etc.)
EXPANSIONS = {
    'hike': ['hiking', 'trek', 'walk', 'nature', 'trail'], 'hiking': ['hike', 'trek', 'walk', 'nature'],
    'trek': ['hiking', 'hike', 'trail', 'nature'], 'trekking': ['hiking', 'trek', 'trail'],
    'walk': ['hiking', 'easy', 'nature'], 'trail': ['hiking', 'trek'],
    'temple': ['monastery', 'lhakhang', 'goenpa', 'cultural', 'chorten'],
    'monastery': ['temple', 'lhakhang', 'goenpa', 'dzong', 'cultural'],
    'lhakhang': ['temple', 'monastery'], 'goenpa': ['monastery', 'temple'],
    'dzong': ['fortress', 'cultural', 'monastery'], 'fortress': ['dzong', 'cultural'],
    'stupa': ['chorten', 'cultural'], 'chorten': ['stupa', 'cultural'],
    'culture': ['cultural', 'history', 'temple'], 'history': ['historic', 'cultural', 'dzong'],
    'historic': ['history', 'cultural', 'dzong'], 'religious': ['temple', 'monastery', 'cultural'],
    'spiritual': ['temple', 'monastery', 'cultural'], 'festival': ['cultural', 'dzong'],
    'mountain': ['mountains', 'pass', 'view', 'himalaya'], 'mountains': ['mountain', 'pass', 'view'],
    'view': ['viewpoint', 'mountains', 'scenic', 'panoramic'], 'views': ['view', 'mountains', 'scenic'],
    'scenic': ['view', 'mountains', 'nature'], 'pass': ['mountains', 'view'],
    'himalaya': ['mountains', 'pass'], 'snow': ['mountains', 'pass'],
    'city': ['cities', 'town'], 'cities': ['city', 'town'], 'town': ['city', 'cities'],
    'market': ['city', 'town'], 'shopping': ['city', 'town'],
    'wildlife': ['park', 'sanctuary', 'animal', 'nature'], 'animal': ['wildlife', 'park', 'nature'],
    'animals': ['wildlife', 'park'], 'park': ['wildlife', 'nature', 'sanctuary'],
    'bird': ['crane', 'wildlife', 'nature'], 'birds': ['crane', 'wildlife', 'nature'],
    'birdwatching': ['crane', 'wildlife', 'nature'], 'crane': ['bird', 'wildlife'],
    'cranes': ['bird', 'wildlife'], 'nature': ['hiking', 'park', 'valley', 'forest'],
    'forest': ['nature', 'park', 'wildlife'], 'valley': ['nature', 'scenic'],
    'textile': ['weaving', 'cultural'], 'weaving': ['textile', 'cultural'],
    'family': ['easy'], 'relax': ['easy', 'valley', 'nature'], 'relaxing': ['easy', 'valley', 'nature'],
    'photography': ['view', 'scenic', 'mountains'],
}
DIFFICULTY_WORDS = {'easy', 'moderate', 'hard'}


# ---------------------------------------------------------------------------
# Words and text matching
# ---------------------------------------------------------------------------
def stem(word):
    """Very small stemmer so 'hike', 'hiking', 'hikes' and 'temples', 'temple' compare equal."""
    w = word.lower()
    if w.endswith('ies') and len(w) > 4:
        w = w[:-3] + 'y'
    elif w.endswith('ing') and len(w) > 5:
        w = w[:-3]
    elif w.endswith('s') and not w.endswith('ss') and len(w) > 3:
        w = w[:-1]
    if w.endswith('e') and len(w) > 3:
        w = w[:-1]
    if len(w) > 3 and w[-1] == w[-2] and w[-1] not in 'sl':
        w = w[:-1]                                   # trekk -> trek
    return w


def words(text):
    return [w for w in re.findall(r'[a-z0-9]+', (text or '').lower()) if len(w) > 1]


def stems(text):
    return {stem(w) for w in words(text)}


def _index_place(place):
    dz = dzongkhag_of_place(place)
    return {
        'name': stems(place['name']),
        'loc': stems(place['location']) | (stems(dz['region']) if dz else set()),
        'type': stems(place['type']),
        'diff': stems(place['difficulty']),
        'desc': stems(place['description']),
    }


_INDEX = {p['name']: _index_place(p) for p in PLACES}
_VOCAB = sorted(set().union(*[set().union(*i.values()) for i in _INDEX.values()])
                | {s for d in DZONGKHAGS for s in stems(d['name'])}
                | {stem(k) for k in EXPANSIONS})


def _index(place):
    if place['name'] not in _INDEX:                  # a place added while the app is running
        _INDEX[place['name']] = _index_place(place)
    return _INDEX[place['name']]


def _field_score(idx, s):
    """How strongly one word (stem) matches a place: name > location > category > level > description."""
    if s in idx['name']:
        return 1.0
    if s in idx['loc']:
        return .9
    if s in idx['type']:
        return .8
    if s in idx['diff']:
        return .6
    if s in idx['desc']:
        return .4
    return 0.0


@lru_cache(maxsize=256)
def parse_query(text):
    """
    Turn the typed text into a Query:  tokens = [(stem, [related stems], fuzzy_stem_or_None), ...]
    near_me is True when the user wrote things like "near me" or "nearby".
    """
    raw_words = words(text)
    near_me = any(w in NEAR_ME_WORDS for w in raw_words)
    tokens = []
    for w in raw_words:
        if w in STOPWORDS or w in NEAR_ME_WORDS:
            continue
        s = stem(w)
        related = [stem(e) for e in EXPANSIONS.get(w, [])]
        fuzzy = None
        if s not in _VOCAB and len(s) >= 4:          # unknown word -> maybe a typo ("thimpu")
            close = difflib.get_close_matches(s, _VOCAB, n=1, cutoff=.78)
            fuzzy = close[0] if close else None
        tokens.append((s, related, fuzzy))
    return {'tokens': tokens, 'near_me': near_me, 'text': (text or '').strip()}


def text_relevance(place, query):
    """0..1 - the average over the typed words of how well each word matches the place."""
    tokens = query['tokens']
    if not tokens:
        return 0.0
    idx = _index(place)
    total = 0.0
    for s, related, fuzzy in tokens:
        score = _field_score(idx, s)
        if related:
            score = max(score, .45 * max(_field_score(idx, r) for r in related))
        if fuzzy:
            score = max(score, .7 * _field_score(idx, fuzzy))
        total += score
    return total / len(tokens)


def matching_dzongkhags(text, limit=2):
    """Dzongkhags whose name the user typed (typos allowed) - used for 'Open Thimphu' shortcuts."""
    query = parse_query(text)
    found = []
    for d in DZONGKHAGS:
        name_stems = stems(d['name'])
        for s, _related, fuzzy in query['tokens']:
            if s in name_stems or (fuzzy and fuzzy in name_stems):
                found.append(d)
                break
    return found[:limit]


def types_for_query(text):
    """Which place categories does this search point at? (used to learn the user's interests)"""
    query = parse_query(text)
    found = set()
    for place_type in {p['type'] for p in PLACES}:
        type_stems = stems(place_type)
        for s, related, _fuzzy in query['tokens']:
            if s in type_stems or any(r in type_stems for r in related):
                found.add(place_type)
    return found


# ---------------------------------------------------------------------------
# What the user does (interests + recent searches), saved per account
# ---------------------------------------------------------------------------
class Activity:
    """Remembers what a user searches, opens, saves and reviews. Saved to user_activity.json."""

    def __init__(self, email=''):
        self.email = (email or '').lower()
        self.searches = []            # newest first
        self.types = {}               # category -> interest weight
        self.difficulty = {}          # Easy / Moderate / Hard -> interest weight
        self._load()

    # ----- recording -----
    def record_search(self, text):
        text = (text or '').strip()
        if not text or len(text) > 80:
            return
        self.searches = [s for s in self.searches if s.lower() != text.lower()]
        self.searches.insert(0, text)
        del self.searches[MAX_RECENT:]
        for place_type in types_for_query(text):
            self._bump(self.types, place_type, 1.5)
        for w in words(text):
            if w in DIFFICULTY_WORDS:
                self._bump(self.difficulty, w.capitalize(), 1.0)
        self.save()

    def record_view(self, place):
        self._learn(place, 1.0, .5)

    def record_save(self, place):
        self._learn(place, 3.0, 1.0)

    def record_review(self, place):
        self._learn(place, 2.0, .7)

    def clear_history(self):
        self.searches, self.types, self.difficulty = [], {}, {}
        self.save()

    def _learn(self, place, type_points, difficulty_points):
        self._bump(self.types, place['type'], type_points)
        self._bump(self.difficulty, place['difficulty'], difficulty_points)
        self.save()

    @staticmethod
    def _bump_all_decay(table):
        for key in table:
            table[key] *= ACTIVITY_DECAY

    def _bump(self, table, key, points):
        self._bump_all_decay(table)
        table[key] = table.get(key, 0.0) + points

    # ----- reading -----
    def interest(self, place):
        """0..1 - how much this user likes this kind of place (0 for a new user)."""
        score = 0.0
        if self.types:
            score += .8 * self.types.get(place['type'], 0) / max(self.types.values())
        if self.difficulty:
            score += .2 * self.difficulty.get(place['difficulty'], 0) / max(self.difficulty.values())
        return min(score, 1.0)

    def top_interest(self):
        return max(self.types, key=self.types.get) if self.types else None

    # ----- saving -----
    def _load(self):
        if not self.email or not os.path.exists(ACTIVITY_FILE):
            return
        try:
            with open(ACTIVITY_FILE, encoding='utf-8') as file:
                data = json.load(file).get(self.email, {})
            self.searches = [str(s) for s in data.get('searches', [])][:MAX_RECENT]
            self.types = {str(k): float(v) for k, v in data.get('types', {}).items()}
            self.difficulty = {str(k): float(v) for k, v in data.get('difficulty', {}).items()}
        except Exception:
            pass                                      # a damaged file just means "start fresh"

    def save(self):
        if not self.email:
            return                                    # not logged in -> keep in memory only
        try:
            everyone = {}
            if os.path.exists(ACTIVITY_FILE):
                with open(ACTIVITY_FILE, encoding='utf-8') as file:
                    everyone = json.load(file)
            everyone[self.email] = {'searches': self.searches,
                                    'types': {k: round(v, 3) for k, v in self.types.items()},
                                    'difficulty': {k: round(v, 3) for k, v in self.difficulty.items()}}
            with open(ACTIVITY_FILE, 'w', encoding='utf-8') as file:
                json.dump(everyone, file, indent=2)
        except Exception:
            pass                                      # never crash the app because of history


# ---------------------------------------------------------------------------
# Location and quality
# ---------------------------------------------------------------------------
def distance_to_place(place, location):
    """Approximate km from the user to the place's dzongkhag town (None if unknown)."""
    if not location or not location.get('in_bhutan', True):
        return None
    dz = dzongkhag_of_place(place)
    if not dz:
        return None
    return haversine_km(location['lat'], location['lon'], dz['lat'], dz['lon'])


def near_score(place, location):
    km = distance_to_place(place, location)
    if km is None:
        return 0.0
    score = math.exp(-km / 100.0)                     # 0 km -> 1.0, 70 km -> 0.5, 230 km -> 0.1
    if location.get('dzongkhag') and place['location'] == location['dzongkhag']:
        score = max(score, .95)
    return score


def quality_score(place):
    """Rating pulled towards the average when there are few reviews, scaled to 0..1."""
    m, avg = 200, 4.5
    v = place['reviews']
    bayes = (v / (v + m)) * place['rating'] + (m / (v + m)) * avg
    return max(0.0, min(1.0, (bayes - 4.0) / 1.0))


# ---------------------------------------------------------------------------
# The recommender
# ---------------------------------------------------------------------------
def recommend(text='', activity=None, location=None, limit=None, only_matches=True, exclude=()):
    """
    Rank places for this user.

    text          what the user typed ('' = just recommend)
    activity      Activity object (interests + recent searches) or None
    location      location dict from geo.py or None
    only_matches  with text: drop places that do not match the words (False = rank everything)
    exclude       place names to leave out

    Returns a list of dicts: {'place', 'score', 'parts', 'reasons'}  (best first).
    """
    activity = activity or Activity('')
    query = parse_query(text)
    has_text = bool(query['tokens'])
    if query['near_me']:
        weights = WEIGHTS_NEAR_ME if has_text else {**WEIGHTS_BROWSE, 'near': .55, 'interest': .20,
                                                    'recent': .05, 'quality': .20}
    else:
        weights = WEIGHTS_SEARCH if has_text else WEIGHTS_BROWSE

    current = (text or '').strip().lower()
    recent_queries = [(parse_query(s), s) for s in activity.searches if s.lower() != current]

    results = []
    for place in PLACES:
        if place['name'] in exclude:
            continue
        relevance = text_relevance(place, query) if has_text else 0.0
        if has_text and only_matches and relevance < MIN_TEXT:
            continue

        # recent searches: newest first, each older one counts RECENT_DECAY times less
        recent, recent_from = 0.0, ''
        for age, (past_query, past_text) in enumerate(recent_queries):
            value = (RECENT_DECAY ** age) * text_relevance(place, past_query)
            if value > recent:
                recent, recent_from = value, past_text

        parts = {'text': relevance, 'interest': activity.interest(place), 'recent': recent,
                 'near': near_score(place, location), 'quality': quality_score(place)}
        score = sum(weights[k] * parts[k] for k in weights)
        results.append({'place': place, 'score': score, 'parts': parts,
                        'reasons': _reasons(place, parts, weights, location, recent_from)})

    results.sort(key=lambda r: (r['score'], r['place']['reviews']), reverse=True)
    return results[:limit] if limit else results


def _reasons(place, parts, weights, location, recent_from):
    """Up to two short explanations, strongest first."""
    candidates = []
    if parts['near'] >= .5:
        if location and place['location'] == location.get('dzongkhag'):
            label = f"Near you - in {place['location']}"
        else:
            km = distance_to_place(place, location)
            label = f'Near you - about {km:.0f} km' if km is not None else 'Near you'
        candidates.append((weights['near'] * parts['near'], label))
    if parts['interest'] >= .5:
        candidates.append((weights['interest'] * parts['interest'], f"You like {place['type']}"))
    if parts['recent'] >= .35 and recent_from:
        candidates.append((weights['recent'] * parts['recent'], f'Like your search "{recent_from}"'))
    if parts['quality'] >= .85:
        candidates.append((weights['quality'] * parts['quality'], 'Top rated'))
    candidates.sort(reverse=True)
    return [label for _score, label in candidates[:2]]


def notes_for(recommendations):
    """{place name: 'reason 1 | reason 2'} - the small line shown on a place card."""
    return {r['place']['name']: '  |  '.join(r['reasons']) for r in recommendations if r['reasons']}


def similar_places(place, activity=None, location=None, limit=12):
    """'More places' - same category / dzongkhag / level first, nudged by the user's taste."""
    base = {r['place']['name']: r['score']
            for r in recommend('', activity, location, exclude=(place['name'],))}
    own_words = _index(place)['desc']
    ranked = []
    for other in PLACES:
        if other['name'] == place['name']:
            continue
        other_words = _index(other)['desc']
        overlap = len(own_words & other_words) / max(1, len(own_words | other_words))
        similarity = (.45 * (other['type'] == place['type']) + .30 * (other['location'] == place['location'])
                      + .10 * (other['difficulty'] == place['difficulty']) + .15 * min(1, overlap * 4))
        ranked.append((.7 * similarity + .3 * base.get(other['name'], 0), other))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    return [p for _s, p in ranked[:limit]]


# ---------------------------------------------------------------------------
# Suggestions while typing
# ---------------------------------------------------------------------------
def suggest(text, activity=None, location=None, limit=6):
    """
    Drop-down suggestions for the search box. Returns a list of
    (kind, label, value) where kind is 'dzongkhag', 'place' or 'query'.
    """
    activity = activity or Activity('')
    text = (text or '').strip()
    low = text.lower()
    if not low:
        return [('query', f'Recent: {s}', s) for s in activity.searches[:5]]

    def starts(name):
        if any(w.startswith(low) for w in [name.lower()] + name.lower().split()):
            return True
        return len(low) >= 3 and low in name.lower()

    items, seen = [], set()
    for d in DZONGKHAGS:                                         # 1. dzongkhags (typed or misspelt)
        if starts(d['name']) or d in matching_dzongkhags(text):
            items.append(('dzongkhag', f"{d['name']}  -  dzongkhag", d))
            seen.add(('d', d['name']))
        if len([i for i in items if i[0] == 'dzongkhag']) >= 2:
            break

    ranked = recommend(text, activity, location, only_matches=True)          # 2. places, best first
    prefix_hits = [r for r in recommend('', activity, location) if starts(r['place']['name'])]
    for r in prefix_hits + ranked:
        place = r['place']
        if ('p', place['name']) in seen:
            continue
        seen.add(('p', place['name']))
        items.append(('place', f"{place['name']}  -  {place['location']}", place))
        if len([i for i in items if i[0] == 'place']) >= max(2, limit - 2):
            break

    for s in activity.searches:                                  # 3. matching past searches
        if s.lower().startswith(low) and s.lower() != low:
            items.append(('query', f'Recent: {s}', s))
            break
    return items[:limit]
