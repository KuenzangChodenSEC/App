"""
dzongkhag_data.py - the 20 dzongkhags (districts) of Bhutan.

Pure data + small helpers (no tkinter). Each dzongkhag has a description, climate,
best time to travel and the position of its main town (used for "near you" ranking).

A dzongkhag's rating is NOT typed in here - it is calculated from the places that
belong to it in places_data.py (a place belongs to a dzongkhag when its `location`
equals the dzongkhag name).
"""
from .places_data import slugify
from .database import get_places


def _dz(name, region, town, lat, lon, tagline, best, climate, description):
    return {
        'name': name,
        'region': region,          # Western / Central / Eastern / Southern
        'town': town,              # main town (dzongkhag headquarters)
        'lat': lat, 'lon': lon,    # approximate position of the main town
        'tagline': tagline,
        'best': best,              # best time to travel
        'climate': climate,
        'description': description,
    }


DZONGKHAGS = [
    _dz('Bumthang', 'Central', 'Jakar', 27.55, 90.75,
        'The spiritual heartland',
        'March–May and September–November',
        'Cool temperate. Mild summers, crisp clear autumns and cold winters with frost and occasional snow.',
        'Four connected valleys that hold some of the oldest temples and monasteries in the country. '
        'A relaxed region for walking, culture, local cheese, honey and buckwheat pancakes.'),
    _dz('Chhukha', 'Western', 'Phuntsholing', 26.85, 89.39,
        'The gateway to India',
        'October–April',
        'Warm and humid near the border with heavy monsoon rain from June to September; cooler in the higher north.',
        'The main entry point from India. Phuntsholing is a busy border town with temples close by, '
        'and the district climbs from warm lowlands to cool mountain areas.'),
    _dz('Dagana', 'Southern', 'Daga', 27.03, 89.88,
        'Quiet hills of the south',
        'October–April',
        'Warm to sub-tropical in the valleys and cooler in the highlands. Wet summers, pleasant dry winters.',
        'A little-visited district of forested hills and terraced villages, with a historic dzong '
        'and good walking away from the crowds.'),
    _dz('Gasa', 'Western', 'Gasa', 27.91, 89.73,
        'Hot springs and high mountains',
        'April–June and September–October',
        'Cold and alpine in the north with snow in winter; warmer around the lower valleys and hot springs.',
        'A remote district in the high Himalaya, known for the Laya trekking routes, hot springs '
        'and the Jigme Dorji National Park.'),
    _dz('Haa', 'Western', 'Haa', 27.39, 89.28,
        'A quiet valley near the border with Tibet',
        'April–June and September–November',
        'Cool temperate. Pleasant summers, cold winters and snow on the high passes.',
        'A peaceful valley with traditional villages and farms. Haa opened to visitors later than most '
        'districts, so it still feels unhurried and authentic.'),
    _dz('Lhuentse', 'Eastern', 'Lhuentse', 27.67, 91.18,
        'Remote, cultural and beautiful',
        'October–April',
        'Mild temperate climate in most valleys, warmer at lower elevations. Dry, clear winters.',
        'One of the most remote districts, home to the ancestral roots of the royal family '
        'and to the weavers of the finest Bhutanese textiles.'),
    _dz('Mongar', 'Eastern', 'Mongar', 27.27, 91.24,
        'The heart of the east',
        'October–April',
        'Warm temperate. Mild, dry winters and warm, wet summers.',
        'A relaxed eastern district with a distinctive dzong, scenic mountain roads and one of '
        'Bhutan’s best-known sacred mask dances.'),
    _dz('Paro', 'Western', 'Paro', 27.43, 89.41,
        'Home of the Tiger’s Nest',
        'March–May and September–November',
        'Cool temperate with four clear seasons. Spring and autumn are mild and sunny, summers bring rain, winters are cold and dry.',
        'A wide, fertile valley with Bhutan’s only international airport. Paro combines the famous Tiger’s Nest hike with '
        'old temples, dzongs and a lively spring festival.'),
    _dz('Pemagatshel', 'Eastern', 'Pemagatshel', 27.03, 91.34,
        'A hidden corner of the south-east',
        'November–March',
        'Warm, sub-tropical lowlands and cooler hills. Hot wet summers and pleasant dry winters.',
        'A quiet southern-eastern district of hills, farms and small temples, rarely visited by tourists.'),
    _dz('Punakha', 'Western', 'Punakha', 27.59, 89.86,
        'The old winter capital',
        'October–May',
        'Warm, sheltered valley with mild winters, hot summers and monsoon rain from June to September.',
        'A fertile valley of rice fields where two rivers meet. Punakha has one of the most beautiful dzongs in the country '
        'and many easy walks.'),
    _dz('Samdrup Jongkhar', 'Eastern', 'Samdrup Jongkhar', 26.80, 91.50,
        'The gateway to the east',
        'November–March',
        'Hot and humid with heavy summer rain; pleasant and dry from November to March.',
        'The eastern entry point from India and Bhutan’s oldest town, with a lively market and a very different feel from the high valleys.'),
    _dz('Samtse', 'Southern', 'Samtse', 26.89, 89.10,
        'Green lowlands of the south-west',
        'November–March',
        'Sub-tropical and humid. Very wet monsoon, comfortable winters.',
        'A warm southern district of green landscapes and local communities, good for birdwatching and for seeing everyday life in the lowlands.'),
    _dz('Sarpang', 'Southern', 'Sarpang', 26.86, 90.27,
        'Jungle, rivers and wildlife',
        'November–March',
        'Sub-tropical, hot and humid in summer with strong monsoon rain; pleasant in winter.',
        'The southern gateway to central Bhutan, bordering the Royal Manas National Park, with forests, rivers and wildlife.'),
    _dz('Thimphu', 'Western', 'Thimphu', 27.47, 89.64,
        'The capital city',
        'March–May and September–November',
        'Cool temperate. Mild spring and autumn, warm summers with monsoon rain, cold winters with occasional snow.',
        'The capital of Bhutan, where tradition and modern life sit side by side. Thimphu has dzongs, giant statues, '
        'markets, cafés and mountain viewpoints, all close together.'),
    _dz('Trashigang', 'Eastern', 'Trashigang', 27.33, 91.55,
        'The hub of the east',
        'October–April',
        'Warm and dry in the valleys during winter; hot and wet in summer, colder on the high eastern ridges.',
        'The largest town in the east, with a spectacular dzong. It is the starting point for visits to semi-nomadic highland communities.'),
    _dz('Trashiyangtse', 'Eastern', 'Trashiyangtse', 27.60, 91.52,
        'Crafts and cranes',
        'October–April',
        'Mild and dry in winter, warm and wet in summer.',
        'A small north-eastern district with a famous stupa, traditional wood-turning craft and a wildlife sanctuary '
        'where black-necked cranes spend the winter.'),
    _dz('Trongsa', 'Central', 'Trongsa', 27.50, 90.50,
        'The dzong on the ridge',
        'October–May',
        'Temperate. Mild, clear winters and wet summers; cool mornings and evenings.',
        'A town built along a steep ridge in the centre of the country, dominated by a huge dzong that was the seat of power of the royal family.'),
    _dz('Tsirang', 'Southern', 'Damphu', 27.02, 90.12,
        'Orange groves and hill villages',
        'November–March',
        'Warm and sub-tropical in the valleys, pleasant and dry in winter.',
        'A hilly southern district known for its oranges, farms and friendly villages.'),
    _dz('Wangdue Phodrang', 'Western', 'Wangdue Phodrang', 27.49, 89.90,
        'Valley of the black-necked cranes',
        'October–March',
        'Varies by height. Mild in the river valleys, cool and cold in Phobjikha and Gangtey in winter.',
        'A large district that includes the glacial Phobjikha valley, where black-necked cranes arrive every winter, '
        'and the scenic Gangtey area.'),
    _dz('Zhemgang', 'Central', 'Zhemgang', 27.22, 90.66,
        'Forests and biodiversity',
        'November–March',
        'Sub-tropical to warm temperate. Hot, wet summers; comfortable and dry winters.',
        'A scenic central-southern district surrounded by dense forest and some of the richest wildlife in Bhutan.'),
]

_BY_NAME = {d['name'].lower(): d for d in DZONGKHAGS}


def dzongkhag_by_name(name):
    """Find a dzongkhag from its name (case-insensitive). Returns None if unknown."""
    return _BY_NAME.get((name or '').strip().lower())


def places_in(dzongkhag):
    """All places that belong to this dzongkhag (dict or name)."""
    name = dzongkhag['name'] if isinstance(dzongkhag, dict) else dzongkhag
    return [p for p in get_places(district=name)]


def dzongkhag_rating(dzongkhag):
    """(average rating weighted by number of reviews, total reviews, number of places)."""
    places = places_in(dzongkhag)
    reviews = sum(p['reviews'] for p in places)
    if not places or not reviews:
        return 0.0, 0, len(places)
    average = sum(p['rating'] * p['reviews'] for p in places) / reviews
    return round(average, 1), reviews, len(places)


def dzongkhag_of_place(place):
    """The dzongkhag dictionary a place belongs to (or None)."""
    return dzongkhag_by_name(place.get('location'))


__all__ = ['DZONGKHAGS', 'dzongkhag_by_name', 'places_in', 'dzongkhag_rating',
           'dzongkhag_of_place', 'slugify']
