from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
from datetime import datetime
import json, uuid, math, traceback, hashlib, os, hmac

BASE = Path(__file__).resolve().parent
# Hosted deployments can mount durable storage and point CS2_DATA_DIR at it.
MATCH_DIR = Path(os.environ.get('CS2_DATA_DIR', str(BASE / 'matches')))
MATCH_DIR.mkdir(exist_ok=True)
HISTORY_FILE = MATCH_DIR / 'history.json'
MAX_UPLOAD = 2 * 1024 * 1024 * 1024
app = Flask(__name__, static_folder=None)
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD


@app.before_request
def protect_hosted_site():
    # Render deployment sets CS2_PASSWORD; local LAN mode can remain password-free.
    password = os.environ.get('CS2_PASSWORD', '')
    if not password:
        return None
    auth = request.authorization
    expected_user = os.environ.get('CS2_USER', 'lanadmin')
    if (not auth or auth.username != expected_user or
            not hmac.compare_digest(auth.password or '', password)):
        return ('Login required', 401, {'WWW-Authenticate': 'Basic realm="CS2 LAN Statistics"'})
    return None


def safe_num(v):
    try:
        if v is None: return 0.0
        n = float(v)
        return 0.0 if math.isnan(n) or math.isinf(n) else n
    except Exception:
        return 0.0


def records(df):
    if df is None: return []
    try:
        return df.to_dict(orient='records')
    except Exception:
        try: return list(df)
        except Exception: return []


def find_value(row, candidates, default=None):
    lower = {str(k).lower(): k for k in row.keys()}
    for c in candidates:
        if c.lower() in lower:
            return row.get(lower[c.lower()])
    # allow prefixed player-property names, e.g. user_player_name
    for c in candidates:
        matches = [k for k in row.keys() if str(k).lower().endswith('_' + c.lower())]
        if matches:
            return row.get(matches[0])
    return default


def parse_demo(path, filename):
    try:
        from demoparser2 import DemoParser
    except Exception as e:
        raise RuntimeError('demoparser2 суусангүй. START_SERVER.bat-ийг дахин ажиллуулаад package суулгана уу.') from e

    parser = DemoParser(str(path))
    header = {}
    try:
        h = parser.parse_header()
        if isinstance(h, dict): header = h
        elif hasattr(h, 'to_dict'): header = h.to_dict()
    except Exception:
        pass

    try:
        deaths = records(parser.parse_event('player_death'))
    except Exception as e:
        raise RuntimeError('player_death event уншиж чадсангүй. Энэ demo CS2-ийн тохирох GOTV/competitive demo мөн эсэхийг шалгана уу. ' + str(e))

    try: hurts = records(parser.parse_event('player_hurt'))
    except Exception: hurts = []
    try: round_ends = records(parser.parse_event('round_end'))
    except Exception: round_ends = []
    try: round_starts = records(parser.parse_event('round_start'))
    except Exception: round_starts = []

    stats = {}
    def get_player(name):
        if name is None: return None
        name = str(name).strip()
        if not name or name.lower() in ('world', 'worldspawn', 'unknown', 'none', 'nan'):
            return None
        if name not in stats:
            stats[name] = {'name': name, 'k': 0, 'd': 0, 'a': 0, 'hs': 0, 'damage': 0.0}
        return stats[name]

    for row in deaths:
        victim_name = find_value(row, ['user_name', 'victim_name', 'player_name', 'name'])
        attacker_name = find_value(row, ['attacker_name', 'killer_name'])
        assister_name = find_value(row, ['assister_name', 'assistant_name'])
        victim = get_player(victim_name)
        attacker = get_player(attacker_name)
        assister = get_player(assister_name)
        if victim: victim['d'] += 1
        if attacker and (not victim or attacker['name'] != victim['name']):
            attacker['k'] += 1
            hs = find_value(row, ['headshot', 'is_headshot'], False)
            if str(hs).lower() in ('true', '1', 'yes') or hs == 1: attacker['hs'] += 1
        if assister and (not victim or assister['name'] != victim['name']) and (not attacker or assister['name'] != attacker['name']):
            assister['a'] += 1

    total_damage = 0.0
    for row in hurts:
        attacker_name = find_value(row, ['attacker_name', 'attacker_player_name'])
        dmg = safe_num(find_value(row, ['dmg_health', 'dmg_health_real', 'health_damage', 'damage'], 0))
        attacker = get_player(attacker_name)
        if attacker and dmg > 0:
            attacker['damage'] += dmg
            total_damage += dmg

    rounds = len(round_ends) or max(0, len(round_starts) - 1)
    if not rounds:
        for row in deaths:
            r = find_value(row, ['total_rounds_played', 'round'])
            if r is not None: rounds = max(rounds, int(safe_num(r)))

    players = []
    for p in stats.values():
        kd = (p['k'] / p['d']) if p['d'] else float(p['k'])
        hs_pct = (p['hs'] / p['k'] * 100) if p['k'] else 0
        adr = p['damage'] / rounds if rounds else 0
        players.append({
            'name': p['name'], 'k': p['k'], 'd': p['d'], 'a': p['a'], 'hs': p['hs'],
            'kd': round(kd, 2), 'hs_pct': round(hs_pct, 1), 'adr': round(adr, 1),
            'damage': round(p['damage'], 1)
        })
    players.sort(key=lambda p: (p['k'], p['a'], -p['d']), reverse=True)
    map_name = header.get('map_name') or header.get('map') or header.get('mapname') or 'Unknown map'
    result = {
        'id': path.stem, 'filename': filename, 'map': str(map_name), 'rounds': rounds,
        'players': players, 'total_kills': sum(p['k'] for p in players),
        'total_damage': round(total_damage, 1), 'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'size_mb': round(path.stat().st_size / 1048576, 1)
    }
    if not players:
        result['warning'] = 'Demo уншигдсан боловч player_death event-ээс тоглогчийн нэр илэрсэнгүй.'
    return result


@app.get('/')
def home():
    return send_from_directory(BASE, 'index.html')

@app.get('/api/health')
def health():
    return jsonify({'ok': True})

@app.post('/api/analyze')
def analyze():
    f = request.files.get('demo')
    if not f or not f.filename:
        return jsonify({'error': 'Demo файл сонгогдоогүй байна.'}), 400
    original = Path(f.filename).name
    if not original.lower().endswith('.dem'):
        return jsonify({'error': 'Зөвхөн .dem файл оруулна уу.'}), 400
    safe_id = uuid.uuid4().hex
    saved_path = MATCH_DIR / f'{safe_id}.dem'
    try:
        f.save(saved_path)
        if saved_path.stat().st_size < 16:
            saved_path.unlink(missing_ok=True)
            return jsonify({'error': 'Файл хоосон эсвэл буруу байна.'}), 400
        file_hash = hashlib.sha256(saved_path.read_bytes()).hexdigest()
        history = []
        if HISTORY_FILE.exists():
            try: history = json.loads(HISTORY_FILE.read_text(encoding='utf-8'))
            except Exception: history = []
        duplicate = next((m for m in history if m.get('file_hash') == file_hash), None)
        if duplicate:
            saved_path.unlink(missing_ok=True)
            duplicate = dict(duplicate)
            duplicate['duplicate'] = True
            return jsonify(duplicate)
        result = parse_demo(saved_path, original)
        result['file_hash'] = file_hash
        history.insert(0, result)
        HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding='utf-8')
        # Keep aggregate history, not the original large demo upload.
        saved_path.unlink(missing_ok=True)
        return jsonify(result)
    except Exception as e:
        saved_path.unlink(missing_ok=True)
        return jsonify({'error': str(e)}), 500

@app.get('/api/matches')
def matches():
    if not HISTORY_FILE.exists(): return jsonify({'matches': []})
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding='utf-8'))
        return jsonify({'matches': [{k:m.get(k) for k in ('id','filename','map','rounds','total_kills','date','size_mb')} for m in data]})
    except Exception:
        return jsonify({'matches': []})


@app.get('/api/leaderboard')
def leaderboard():
    if not HISTORY_FILE.exists():
        return jsonify({'players': [], 'matches': 0})
    try:
        history = json.loads(HISTORY_FILE.read_text(encoding='utf-8'))
    except Exception:
        history = []
    aggregate = {}
    for match in history:
        rounds = max(0, int(safe_num(match.get('rounds'))))
        for player in match.get('players', []):
            name = str(player.get('name') or '').strip()
            if not name: continue
            p = aggregate.setdefault(name, {'name': name, 'matches': 0, 'rounds': 0, 'k': 0, 'd': 0, 'a': 0, 'hs': 0, 'damage': 0.0})
            p['matches'] += 1
            p['rounds'] += rounds
            p['k'] += int(safe_num(player.get('k')))
            p['d'] += int(safe_num(player.get('d')))
            p['a'] += int(safe_num(player.get('a')))
            # Older saved records may not have the raw headshot count.
            p['hs'] += int(safe_num(player.get('hs', round(safe_num(player.get('hs_pct')) * safe_num(player.get('k')) / 100))))
            p['damage'] += safe_num(player.get('damage', safe_num(player.get('adr')) * rounds))
    players = []
    for p in aggregate.values():
        kd = p['k'] / p['d'] if p['d'] else float(p['k'])
        hs_pct = p['hs'] / p['k'] * 100 if p['k'] else 0
        adr = p['damage'] / p['rounds'] if p['rounds'] else 0
        # A transparent community score, not Valve's official rating.
        rating = (p['k'] * 1.0 + p['a'] * 0.35 - p['d'] * 0.55 + p['damage'] / 100) / max(1, p['matches'])
        players.append({**p, 'kd': round(kd, 2), 'hs_pct': round(hs_pct, 1), 'adr': round(adr, 1), 'rating': round(rating, 2)})
    players.sort(key=lambda x: (x['rating'], x['k'], x['kd']), reverse=True)
    return jsonify({'players': players, 'matches': len(history)})

@app.errorhandler(413)
def too_large(_):
    return jsonify({'error': 'Файл 2 GB-аас том байна.'}), 413

if __name__ == '__main__':
    print('\nCS2 Captain Draft Pro+ is running: http://127.0.0.1:8000')
    print('Local: http://127.0.0.1:8000')
    print('LAN: бусад PC-ээс энэ компьютерийн IPv4 хаяг + :8000 ашиглана.')
    print('Энэ цонхыг хаахгүй байгаарай.\n')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '8000')), debug=False)
