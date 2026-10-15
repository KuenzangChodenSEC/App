"""
places_data.py - the list of Bhutan destinations shown in LamGo.

This file contains only data (no tkinter), so it can also be used by helper
scripts such as tools/make_placeholder_images.py.

To add a new destination, add one more `_place(...)` line to PLACES below and
(optionally) drop a photo called  assets/places/<slug>.jpg  - the slug is the
place name in lowercase with underscores, e.g. "Punakha Dzong" -> punakha_dzong.jpg
"""
import re


def slugify(name):
    """Turn a place name into a file-friendly name: 'Punakha Dzong' -> 'punakha_dzong'."""
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')


def _place(name, location, rating, reviews, time, kind, difficulty,
           elevation, weather, best, description):
    """Build one place dictionary (keeps the PLACES list below short and readable)."""
    return {
        'name': name,              # shown on cards and used to find the photo
        'location': location,      # district / area
        'rating': rating,          # average star rating
        'reviews': reviews,        # number of ratings
        'time': time,              # typical travel / visit time
        'type': kind,              # category used by search and filters
        'difficulty': difficulty,
        'elevation': elevation,
        'weather': weather,
        'best': best,              # best time to visit
        'description': description,
    }


PLACES = [
    _place('Paro Taktsang', 'Paro', 4.9, 2245, '3 hr 30 min', 'Nature & Hiking', 'Moderate', '3,120 m', '18°C',
           'March–May and September–November',
           'A famous cliffside monastery surrounded by mountains and forest. The hike offers beautiful views of Paro Valley.'),
    _place('Punakha Dzong', 'Punakha', 4.8, 1530, '2 hr 30 min', 'Cultural Sites', 'Easy', '1,242 m', '20°C',
           'October–May',
           'A historic fortress monastery located between the Pho Chhu and Mo Chhu rivers. It is known for its architecture and peaceful surroundings.'),
    _place('Phobjikha Valley', 'Wangdue Phodrang', 4.6, 980, '4 hr', 'Nature & Hiking', 'Easy', '2,900 m', '14°C',
           'October–March',
           'A wide glacial valley famous for its scenery, peaceful villages and black-necked cranes during the winter season.'),
    _place('Dochula Pass', 'Thimphu', 4.7, 1120, '1 hr 30 min', 'Mountains', 'Easy', '3,100 m', '12°C',
           'October–April',
           'A mountain pass with panoramic Himalayan views and the famous 108 Druk Wangyel chortens.'),
    _place('Haa Valley', 'Haa', 4.6, 650, '3 hr', 'Nature & Hiking', 'Moderate', '2,670 m', '15°C',
           'April–June and September–November',
           'A quiet valley with traditional villages, green landscapes and beautiful mountain scenery.'),
    _place('Bumthang Valley', 'Bumthang', 4.7, 742, '4 hr', 'Cultural Sites', 'Moderate', '2,800 m', '16°C',
           'October–May',
           'A culturally rich region with old temples, monasteries, farms and peaceful valleys.'),
    _place('Gangtey Valley', 'Wangdue Phodrang', 4.4, 620, '4 hr 30 min', 'Nature & Hiking', 'Moderate', '2,900 m', '13°C',
           'October–March',
           'A scenic valley around Gangtey village, known for its monastery, forests and winter crane habitat.'),
    _place('Tashichho Dzong', 'Thimphu', 4.7, 890, '20 min', 'Cultural Sites', 'Easy', '2,320 m', '19°C',
           'March–May and September–November',
           'A large fortress monastery and important government landmark in the capital city.'),
    _place('Buddha Dordenma', 'Thimphu', 4.6, 1320, '25 min', 'Cultural Sites', 'Easy', '2,680 m', '19°C',
           'March–May and September–November',
           'A huge Buddha statue overlooking Thimphu Valley with wide views of the city and surrounding mountains.'),
    _place('Memorial Chorten', 'Thimphu', 4.5, 760, '15 min', 'Cultural Sites', 'Easy', '2,320 m', '19°C',
           'All year',
           'A well-known stupa in central Thimphu visited by locals and visitors throughout the day.'),
    _place('Motithang Takin Preserve', 'Thimphu', 4.3, 540, '30 min', 'Nature & Hiking', 'Easy', '2,600 m', '18°C',
           'March–May and September–November',
           'A small nature area where visitors can see Bhutan’s national animal, the takin.'),
    _place('Chele La Pass', 'Haa', 4.6, 610, '1 hr 30 min', 'Mountains', 'Moderate', '3,988 m', '8°C',
           'April–June and October–November',
           'One of Bhutan’s highest motorable passes, offering mountain views and cool high-altitude landscapes.'),
    _place('Chimi Lhakhang', 'Punakha', 4.5, 830, '1 hr', 'Cultural Sites', 'Easy', '1,300 m', '21°C',
           'October–May',
           'A small hilltop temple reached by a pleasant walk through fields and traditional villages.'),
    _place('Khamsum Yulley Namgyal Chorten', 'Punakha', 4.8, 740, '1 hr 30 min', 'Nature & Hiking', 'Moderate', '1,500 m', '20°C',
           'October–May',
           'A beautiful chorten reached by a short hike through rice fields and forests above the Mo Chhu River.'),
    _place('Trongsa Dzong', 'Trongsa', 4.7, 690, '2 hr', 'Cultural Sites', 'Moderate', '2,200 m', '15°C',
           'October–May',
           'A dramatic fortress stretching along a mountain ridge and an important historical site in central Bhutan.'),
    _place('Kuensel Phodrang', 'Thimphu', 4.4, 430, '25 min', 'Mountains', 'Easy', '2,600 m', '18°C',
           'All year',
           'A peaceful viewpoint near the Buddha Dordenma area with views across Thimphu Valley.'),
    _place('Jigme Dorji National Park', 'Gasa', 4.7, 350, 'Varies', 'Nature & Hiking', 'Hard', 'Varies', 'Varies',
           'March–May and September–November',
           'A large protected area with forests, high mountains, wildlife and trekking opportunities.'),
    _place('Jakar Dzong', 'Bumthang', 4.5, 410, '30 min', 'Cultural Sites', 'Easy', '2,800 m', '16°C',
           'October–May',
           'A historic dzong overlooking the Bumthang valley and a useful starting point for exploring the region.'),
    _place('Laya Village', 'Gasa', 4.8, 280, 'Multi-day trek', 'Nature & Hiking', 'Hard', '3,800 m', '8°C',
           'April–June and September–October',
           'A remote highland village known for its mountain scenery, traditional culture and trekking routes.'),
    _place('Royal Manas National Park', 'Sarpang', 4.6, 320, 'Varies', 'Nature & Hiking', 'Moderate', 'Varies', '24°C',
           'November–March',
           'A rich protected area with forests, rivers and opportunities to see Bhutanese wildlife.'),
    _place('Mongar Dzong', 'Mongar', 4.4, 270, '30 min', 'Cultural Sites', 'Easy', '1,600 m', '22°C',
           'October–May',
           'A fortress monastery with views over eastern Bhutan and a distinctive traditional design.'),
    _place('Trashigang Dzong', 'Trashigang', 4.5, 300, '30 min', 'Cultural Sites', 'Easy', '1,150 m', '23°C',
           'October–May',
           'A historic dzong overlooking the Dangme Chhu river valley in eastern Bhutan.'),
    _place('Samdrup Jongkhar', 'Samdrup Jongkhar', 4.2, 180, 'Varies', 'Cities', 'Easy', '200 m', '26°C',
           'November–March',
           'A lively town in southeastern Bhutan and an important gateway between Bhutan and India.'),
    _place('Zhemgang', 'Zhemgang', 4.4, 190, 'Varies', 'Nature & Hiking', 'Moderate', '1,500 m', '23°C',
           'November–March',
           'A scenic central-southern district surrounded by forests and rich biodiversity.'),
    _place('Samtse', 'Samtse', 4.1, 150, 'Varies', 'Cities', 'Easy', '300 m', '25°C',
           'November–March',
           'A southern Bhutanese district with warm weather, green landscapes and local communities.'),

    # ---- Added so that every one of the 20 dzongkhags has at least one place. ----
    # NOTE: ratings / review counts / weather for these are placeholders - replace with real figures.
    _place('Rinpung Dzong', 'Paro', 4.7, 700, '45 min', 'Cultural Sites', 'Easy', '2,250 m', '17°C',
           'March–May and September–November',
           'A large fortress monastery above Paro town, reached by a traditional covered wooden bridge.'),
    _place('Kyichu Lhakhang', 'Paro', 4.6, 640, '40 min', 'Cultural Sites', 'Easy', '2,200 m', '17°C',
           'March–May and September–November',
           'One of the oldest and most sacred temples in Bhutan, set in a quiet courtyard with orange trees.'),
    _place('Zangto Pelri Lhakhang', 'Chhukha', 4.4, 310, '45 min', 'Cultural Sites', 'Easy', 'Varies', '26°C',
           'October–April',
           'A colourful temple in Phuntsholing representing the heavenly paradise of Guru Rinpoche, close to the Indian border.'),
    _place('Kharbandi Goenpa', 'Chhukha', 4.3, 240, '1 hr', 'Cultural Sites', 'Easy', 'Varies', '24°C',
           'October–April',
           'A peaceful monastery on a hill above Phuntsholing, surrounded by gardens and looking over the southern foothills.'),
    _place('Dagana Dzong', 'Dagana', 4.3, 160, '30 min', 'Cultural Sites', 'Easy', 'Varies', 'Varies',
           'October–April',
           'A historic dzong on a ridge in southern Bhutan with views over forested hills and terraced villages.'),
    _place('Lhuentse Dzong', 'Lhuentse', 4.4, 150, '30 min', 'Cultural Sites', 'Easy', 'Varies', 'Varies',
           'October–April',
           'A hilltop dzong in the remote north-east, in the Kurtoe region that is the ancestral homeland of the royal family.'),
    _place('Khoma Village', 'Lhuentse', 4.5, 120, '2 hr', 'Cultural Sites', 'Easy', 'Varies', 'Varies',
           'October–April',
           'A weaving village famous for kishuthara, one of Bhutan’s most prized textiles. Visitors can watch the weavers at work.'),
    _place('Drametse Lhakhang', 'Mongar', 4.5, 140, '1 hr', 'Cultural Sites', 'Moderate', 'Varies', 'Varies',
           'October–April',
           'A large monastery in eastern Bhutan, known as the home of the Drametse Ngacham mask dance.'),
    _place('Yongla Goenpa', 'Pemagatshel', 4.2, 90, '1 hr', 'Cultural Sites', 'Moderate', 'Varies', 'Varies',
           'November–March',
           'A peaceful monastery in Pemagatshel in south-eastern Bhutan, with a calm setting and views over the surrounding hills.'),
    _place('Gom Kora', 'Trashigang', 4.4, 170, '1 hr', 'Cultural Sites', 'Easy', 'Varies', 'Varies',
           'October–April',
           'A riverside temple near Trashigang, known for its sacred rock and its annual festival.'),
    _place('Chorten Kora', 'Trashiyangtse', 4.6, 260, '45 min', 'Cultural Sites', 'Easy', 'Varies', 'Varies',
           'October–April',
           'A large white stupa beside the Kulong Chhu river, modelled on Boudhanath in Nepal, and the setting of a spring festival.'),
    _place('Bumdeling Wildlife Sanctuary', 'Trashiyangtse', 4.5, 200, 'Varies', 'Nature & Hiking', 'Moderate', 'Varies', 'Varies',
           'November–March',
           'A protected area in the north-east with forests, wildlife and black-necked cranes that spend the winter in the valley.'),
    _place('Kilkhorthang Lhakhang', 'Tsirang', 4.2, 90, '30 min', 'Cultural Sites', 'Easy', 'Varies', 'Varies',
           'November–March',
           'A well-known temple in Tsirang in south-central Bhutan, visited by pilgrims and by travellers exploring the district.'),
]
