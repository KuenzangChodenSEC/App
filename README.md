# LamGo - Bhutan Place Recommendation Desktop App

## Features
- Opens maximized; cards, images and text re-flow when the window is resized.
- Login / Sign Up page uses your own picture (`assets/auth_background.jpg`).
  The heading and caption change when you switch between LOGIN and SIGN UP.
- Logging in **or** creating an account takes you straight to the Home page.
- "Forgot password?" opens a Reset Password form (email + new password + confirm).
- Password rules are shown under the first password box; the confirm box only says whether the passwords match.
- Every page has a green "Back" button in the top bar.
- **Home shows all 20 dzongkhags.** Click one (e.g. Thimphu) to open its page: photo, rating,
  description, best time to travel, climate, 3 photos and every place to visit there.
- **Smart search** ranks places for each user using: the words typed (with synonyms and typo
  tolerance), the user's interests (what they open / save / review / search), their recent
  searches, and their location. Cards show *why* a place is recommended. A drop-down suggests
  places, dzongkhags and recent searches while typing. Try: `hike`, `temples`, `thimpu`, `near me`.
- 38 Bhutan places, each with its own picture, weather, best time, map link and reviews.
- Saved places, posts, profile photo, notifications, categories and filters.

## Install and run
```bash
pip install -r requirements.txt
python main.py
```

## Project layout
```
main.py                 app window, navigation, login/logout
pages/
    common.py           colours, fonts, image helpers, header, place cards, responsive grid
    database.py         SQLite database access and place-management helpers
    places_data.py      starter/sample place records (imported into SQLite once)
    auth.py             login / sign-up page
    home.py explore.py place_details.py reviews.py create_post.py profile.py ...
assets/
    auth_background.jpg picture on the login / sign-up page
    bhutan_place.jpg    fallback picture for any place without its own photo
    places/             one picture per place  (see below)
tools/make_placeholder_images.py   regenerates the stand-in pictures
```

## Pictures for each place
Every place looks for its photo in `assets/places/` using its name in lowercase with underscores:

| Place                     | Main photo file             |
|---------------------------|-----------------------------|
| Paro Taktsang             | `paro_taktsang.jpg`         |
| Punakha Dzong             | `punakha_dzong.jpg`         |
| Khamsum Yulley Namgyal Chorten | `khamsum_yulley_namgyal_chorten.jpg` |

- `paro_taktsang.jpg` is a real photo. The other files are **illustrated stand-ins** - replace
  any of them with a real photo by saving it under the same name (jpg, jpeg, png or webp).
- On the Place Details page, three photos are shown. Add `<name>_2.jpg` and `<name>_3.jpg`
  for different extra photos; otherwise the main photo is reused.
- To add a new place, add a `_place(...)` line in `pages/places_data.py` and drop its photo in `assets/places/`.

## How the recommendation works (pages/recommender.py)
score = weighted sum of: text match, interest, recent searches, nearness, rating quality.
Weights are at the top of the file - change them to tune the results.
Interests and recent searches are saved per account in `user_activity.json`.

## Place database (SQLite)
LamGo now stores destination records in `data/lamgo.db`. It is created automatically on first run and starts with the existing 38 sample places. The original sample list is only used to seed a new database; once a place is in SQLite, edits made in the database are not overwritten on startup.

For an Excel-like way to manage destinations, install the free **DB Browser for SQLite** from https://sqlitebrowser.org/ and open `data/lamgo.db`. Open the `places` table and use **Browse Data** to add or edit rows. Save changes before reopening LamGo.

The `places` table includes: `name`, `district`, `category`, `rating`, `reviews`, `visit_time`, `difficulty`, `elevation`, `weather`, `best_time`, `description`, `latitude`, `longitude`, `image`, and `verified_coordinates`.

Suggested categories are **Nature & Hiking**, **Cities**, **Cultural Sites**, and **Mountains & Peaks**. Use the district name consistently (for example, `Paro`, `Thimphu`, or `Bumthang`). For map directions and proximity ranking, enter a place's real decimal latitude and longitude when you have verified coordinates; leave them blank rather than guessing. Image filenames should match the place name in `assets/places/`.

To add places in Python, use `add_or_update_place(...)` from `pages.database`; the function checks required fields and coordinate ranges. The existing UI is compatible with the database fields, and filters/recommendations read the database-backed catalogue.

## Adding data
- New dzongkhag info: `pages/dzongkhag_data.py` (description, climate, best time, coordinates).
- A dzongkhag's rating is calculated from its places. A place belongs to a dzongkhag when its
  `location` in `places_data.py` equals the dzongkhag name.
- Own dzongkhag photos: `assets/dzongkhags/<name>.jpg` (also `_2`, `_3`). Without them the photos
  of the dzongkhag's best-known places are used.
- Ratings, review counts and weather of the 13 places marked "Added so that every dzongkhag..."
  in `places_data.py` are placeholders - please replace them with real figures.

## Live location
A desktop Python program usually cannot read a phone-style GPS sensor. LamGo currently uses an internet IP lookup (ipapi.co / ipwho.is), which is approximate and may identify only a town or region, plus the **Change** button to choose a dzongkhag manually. This is not continuous, precise live GPS tracking. Accurate device location would require a supported GPS/location device or a separate location-enabled mobile/web client. Place coordinates in SQLite are optional and should be verified before using them for distance-based recommendations.
Set `AUTO_DETECT_LOCATION = False` in `pages/geo.py` to disable the internet lookup.


## Community features (updated)

- LamGo now uses a warm cream and brown colour palette.
- **Follow / Friends** lists registered users, supports follow/unfollow, and opens a user's posts and ratings.
- Posts and reviews, likes, and follow relationships are saved in `social_data.json` beside `main.py` so they remain after restarting the app.
- Destination rating averages and rating counts are calculated from ratings submitted by LamGo users; the interface no longer inserts made-up sample reviews.
- **Location** can request an approximate network-based location, let the user choose a district manually, and open the coordinates in Google Maps. Desktop Tkinter does not have direct phone GPS access; network location may be less precise than device GPS.

Run from the `lamgo` folder with `python main.py`. Install requirements first with `pip install -r requirements.txt`.

## Cross-platform notes (Windows, macOS and Linux)

LamGo uses Python, Tkinter, Pillow and SQLite. Install a supported Python 3 version and ensure Tkinter is installed for your operating system. Then run `python main.py` (on some Linux systems use `python3 main.py`). Install Python dependencies with `python -m pip install -r requirements.txt`.

LamGo now stores writable account, social and place-database data in the operating system's user-data directory rather than requiring write access to the application folder:

- Windows: `%LOCALAPPDATA%\\LamGo`
- macOS: `~/Library/Application Support/LamGo`
- Linux: `~/.local/share/lamgo` (or `$XDG_DATA_HOME/lamgo`)

On first launch, existing `users.json`, `social_data.json`, and `data/lamgo.db` files are copied into the user-data directory if present.

## Social features and scope

Follow, follow-back, like, comment, and notification records are persisted per account in the local social store. This works between accounts using the same LamGo installation and data directory. **It does not synchronise separate laptops over the internet.** To make users on different devices see each other's posts and notifications, LamGo needs a hosted API and shared database, plus authentication and deployment configuration; a desktop-only Tkinter program cannot provide cross-device sync by itself.

## Location accuracy

Use **Use Precise Device Location** on the Location page to open a local permission page in the default browser. Allow location access in the browser and operating system. The browser returns the device's available location coordinates to the running LamGo app. Accuracy depends on the device and its GPS/Wi-Fi/location services. If permission is denied or the browser cannot locate the device, use approximate IP location or choose a district manually. IP location is approximate and should not be treated as GPS.

## Package as a desktop app

Run PyInstaller from the project folder on each target operating system (build on Windows for Windows, macOS for macOS, and Linux for Linux):

```bash
python -m pip install pyinstaller
python -m PyInstaller --onedir --windowed --name LamGo main.py
```

Before distributing a packaged build, test the assets and first-run database migration on a clean user account. Tkinter apps should generally be built separately on each operating system.
