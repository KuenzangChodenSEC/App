"""
geo.py - distances and "where is the user?" helpers (no tkinter).

A normal desktop Python program has no GPS. LamGo therefore finds the user's
approximate position in this order:

    1. IP-address lookup (needs internet; accurate to roughly town / region level)
    2. The dzongkhag the user picks by hand ("Change" button) - always works offline

Set AUTO_DETECT_LOCATION = False to switch off the internet lookup completely.
"""
import json
import math
import urllib.request

from .dzongkhag_data import DZONGKHAGS, dzongkhag_by_name

AUTO_DETECT_LOCATION = True
OUTSIDE_BHUTAN_KM = 120          # further than this from every dzongkhag town -> "outside Bhutan"

# Free HTTPS services that return the caller's approximate position. Tried in order.
_SERVICES = [
    ('https://ipapi.co/json/', lambda d: (d.get('latitude'), d.get('longitude'), d.get('city'))),
    ('https://ipwho.is/', lambda d: (d.get('latitude'), d.get('longitude'), d.get('city'))
     if d.get('success', True) else (None, None, None)),
]


def haversine_km(lat1, lon1, lat2, lon2):
    """Straight-line distance between two points on Earth, in kilometres."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def nearest_dzongkhag(lat, lon):
    """(dzongkhag, distance_km) of the closest dzongkhag town."""
    best = min(DZONGKHAGS, key=lambda d: haversine_km(lat, lon, d['lat'], d['lon']))
    return best, haversine_km(lat, lon, best['lat'], best['lon'])


def make_location(lat, lon, source, city=None):
    """Build the location dictionary that the whole app uses."""
    dzongkhag, km = nearest_dzongkhag(lat, lon)
    in_bhutan = km <= OUTSIDE_BHUTAN_KM
    return {
        'lat': lat, 'lon': lon, 'source': source,         # source: 'auto' or 'manual'
        'dzongkhag': dzongkhag['name'] if in_bhutan else None,
        'in_bhutan': in_bhutan,
        'label': (dzongkhag['name'] if in_bhutan else (city or 'outside Bhutan')),
    }


def location_from_dzongkhag(name):
    """A manual location: the main town of the chosen dzongkhag."""
    d = dzongkhag_by_name(name)
    if not d:
        return None
    return make_location(d['lat'], d['lon'], 'manual')


def detect_location_blocking(timeout=4):
    """
    Ask the internet services for our approximate position (call from a background thread!).
    Returns a location dict, or None if offline / blocked.
    """
    if not AUTO_DETECT_LOCATION:
        return None
    for url, parse in _SERVICES:
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'LamGo/1.0'})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode('utf-8'))
            lat, lon, city = parse(data)
            if lat is not None and lon is not None:
                return make_location(float(lat), float(lon), 'auto', city)
        except Exception:
            continue                      # try the next service
    return None


def request_browser_geolocation(on_success, on_error=None):
    """Open a localhost page that requests OS/browser location permission.

    Tkinter itself has no cross-platform GPS API. Browsers can use available
    GPS/Wi-Fi/location services after explicit user permission. This helper
    uses localhost (a secure context) and never substitutes random coordinates.
    """
    import threading
    import webbrowser
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_GET(self):
            html = '''<!doctype html><html><head><meta charset="utf-8"><title>LamGo location permission</title>
            <style>body{font:16px system-ui;background:#f7f1e8;color:#35291f;max-width:620px;margin:8vh auto;padding:24px}
            button{background:#8b5e3c;color:white;border:0;padding:12px 18px;border-radius:8px;cursor:pointer}</style></head>
            <body><h2>Share your device location with LamGo</h2><p>Your browser will ask for permission. Coordinates are sent only to the LamGo app running on this computer.</p>
            <button onclick="locate()">Allow and detect my location</button><p id="status">Waiting for your permission.</p>
            <script>async function locate(){const s=document.getElementById('status');if(!navigator.geolocation){s.textContent='This browser does not support geolocation.';return;}
            s.textContent='Requesting permission…';navigator.geolocation.getCurrentPosition(async p=>{try{const r=await fetch('/location',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({lat:p.coords.latitude,lon:p.coords.longitude,accuracy:p.coords.accuracy})});s.textContent=r.ok?'Location sent to LamGo. You can close this tab.':'Could not send location to LamGo.';}catch(e){s.textContent='Could not connect to LamGo. Please retry.';}},e=>{s.textContent='Location unavailable: '+e.message+'. Check browser and operating-system location permissions.';},{enableHighAccuracy:true,timeout:20000,maximumAge:0});}</script></body></html>'''
            self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers(); self.wfile.write(html.encode('utf-8'))

        def do_POST(self):
            if self.path != '/location':
                self.send_error(404); return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                payload = json.loads(self.rfile.read(length).decode('utf-8'))
                lat, lon = float(payload['lat']), float(payload['lon'])
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    raise ValueError('invalid coordinates')
                location = make_location(lat, lon, 'browser', None)
                location['accuracy_m'] = payload.get('accuracy')
                self.send_response(200); self.end_headers(); self.wfile.write(b'OK')
                on_success(location)
            except Exception:
                self.send_error(400, 'Invalid location data')

    try:
        server = HTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        webbrowser.open(f'http://127.0.0.1:{server.server_port}/')
        threading.Timer(180, server.shutdown).start()
        return True
    except Exception as exc:
        if on_error:
            on_error(str(exc))
        return False
