import os
import sys
import re
import ssl
import json
import time
import uuid
import hmac
import string
import base64
import random
import hashlib
import asyncio
import socket
import struct
import threading
import traceback
import math
from datetime import datetime
from urllib.parse import urlsplit

import aiohttp
import requests
import urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

import MajorloginReqBuild_pb2
import PorTs_pb2
from MajorloginResp_pb2 import MajorLoginRes as MajorLoginResponse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from protobuf_decoder.protobuf_decoder import Parser
    HAS_PARSER = True
except ImportError:
    HAS_PARSER = False
    Parser = None

REGION_LIST = ["IND", "ID", "TH", "ME", "EUROPE", "VN", "BD", "PK", "TW", "RU", "NA", "SAC", "BR", "SG", "US"]

REGION_LANG = {
    "ME": "ar", "IND": "hi", "ID": "id", "VN": "vi", "TH": "th",
    "BD": "bn", "PK": "ur", "TW": "zh", "EUROPE": "fr", "RU": "ru",
    "NA": "na", "SAC": "es", "BR": "pt", "SG": "ms", "US": "us",
}

REGION_GROUP = {
    "IND": "IND",
    "BR": "AMERICA", "US": "AMERICA", "NA": "AMERICA", "SAC": "AMERICA",
    "ID": "OTHERS", "TH": "OTHERS", "ME": "OTHERS", "EUROPE": "OTHERS",
    "VN": "OTHERS", "BD": "OTHERS", "PK": "OTHERS", "TW": "OTHERS",
    "RU": "OTHERS", "SG": "OTHERS",
}

REGION_URLS = {
    "IND": {"server": "https://loginbp.ppmainecoonghj.com/", "client": "https://client.ind.freefiremobile.com/"},
    "AMERICA": {"server": "https://loginbp.ppmainecoonghj.com/", "client": "https://client.us.freefiremobile.com/"},
    "OTHERS": {"server": "https://loginbp.ppmainecoonghj.com/", "client": "https://clientbp.ggpolarbear.com/"},
}

APP_ID = 100067
CLIENT_TYPE = 2
SOURCE = 2
SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"

GARENA_BASE = "https://100067.connect.garena.com/api/v2/oauth"
REGISTER_URL = f"{GARENA_BASE}/guest:register"
GRANT_URL = f"{GARENA_BASE}/guest/token:grant"
DATADOME_URL = "https://datadome.garena.com/js/"
VER_URL_BASE = "https://version.ggwhitehawk.com/live/ver.php"
PLAYSTORE_URL = "https://play.google.com/store/apps/details?id=com.dts.freefireth&hl=en&gl=US"

MIN_REGISTER_INTERVAL = 1.0
REGISTER_BACKOFF_START = 10.0
REGISTER_BACKOFF_MAX = 60.0
REGISTER_MAX_RETRIES = 6
DATADOME_MAX_RETRIES = 4
VER_MAX_ATTEMPTS = 3

USER_AGENT_MSDK = "GarenaMSDK/4.0.44(V2538 ;Android 16;en;US;app 1.132.1 2019121227;)"
USER_AGENT_UNITY = "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
USER_AGENT_WEB = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

_KEYSTREAM = bytes([
    0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37,
    0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30,
])

SESSION_HASH = "1ac4b80ecf0478a44203bf8fac6120f5"

ACCOUNTS_FILE = "accs.txt"
CLAN_TRACKER_FILE = "clan_tracker.json"
UDP_LOG_FILE = "udp_logs.txt"

REGION = "IND"
LANG_CODE = "hi"

SETTLE_AFTER_ALL_JOIN = 1.5
SQUAD_PLAYERS = 4
SQUAD_TIMEOUT = 600
REGION_ROTATION_LIST   = ["IND", "ID", "TH", "ME", "VN", "BD", "PK", "SG"]
REGION_ROTATE_EVERY_N  = 2
NEW_MATCH_DELAY        = 1.0
START_REPEAT_INTERVAL  = 1.5

CMD_EMOTE                    = 371
CMD_USE_ACTIVE_SKILL         = 248
CMD_SYNC_ACTIVE_SKILL_STATE  = 250
CMD_USE_ACTIVE_SKILL_FAIL    = 823
CMD_AUTOFLIGHTBOMB_CREATE    = 538
CMD_AUTOFLIGHTBOMB_PUSHSTATE = 542
CMD_PUSH_AUTOFLIGHT_ENEMY    = 543
CMD_SYNC_PRESET_INFO         = 1658
CMD_GRI_SYNC_PHASE           = 1901

PHASE_PREPARE  = 1
PHASE_FIGHT    = 2
PHASE_ROUND_END = 5

EMOTE_ID             = 909000001
EMOTE_EVERY          = 4.0
HOMER_SKILL_ID       = 102000037
ACTIVE_SKILL_ID      = 5506
KNOWN_ACTIVE_SKILLS  = (5506, 102000037)
SKILL_EVERY          = 5.0
SKILL_AFTER_FIGHT_SEC = 1.5
SKILL_MAX_DIST       = 60000.0
SKILL_NO_REPLY_SEC   = 4.0
DRONE_TARGET_MAX     = 60000.0

MSG_KEY_RELIABLE_MIN = 90
MSG_KEY_RELIABLE_MAX = 99
JWT_CACHE_FILE         = "jwt.json"
JWT_TTL                = 7 * 3600

_PLAY_VERSION = "1.132.13"
_OB_VERSION = "OB55"

HARDCODED_CONFIG = {
    "latest_release_version": "OB55",
    "remote_version": "1.132.13",
    "cdn_url": "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/",
    "abhotupdate_cdn_url": "https://core-bs.ggpolarbear.com/live/ABHotUpdates/",
    "client_ip": "103.200.36.133",
    "vercfg_sign": "1.f46ddde8bb35d74e",
    "region": REGION,
    "lang": LANG_CODE,
    "country_code": REGION,
    "server_url": "https://loginbp.ppmainecoonghj.com/",
    "client_url": "https://client.ind.freefiremobile.com/",
}

# Avatar Constants
AVATAR_BODY_HEX_1 = "F7 7E 25 1D 0B 8C 68 60 D2 B9 9B 0E 28 7D E7 FD"
AVATAR_BODY_HEX_2 = "63 54 39 64 57 89 CC 67 F6 0E 4E 72 09 B7 91 C3"

_print_lock = threading.Lock()
_file_lock = threading.Lock()
_gate_lock = threading.Lock()
_dd_lock = threading.Lock()
_count_lock = threading.Lock()

_last_register_time = 0.0
_success_count = 0
_failure_count = 0

_dd_session_cookie = None
_dd_expires_at = 0.0

_log_lock = threading.Lock()

MOVE_HZ = 5.0
MOVE_INTERVAL = 1.0 / MOVE_HZ
PUNCH_VEL = 390
PUNCH_STEP = PUNCH_VEL / MOVE_HZ  # 78.0
STICK_DIST = 150.0
CHASE_Y_LERP = 0.5
POSE_STANDING = 0
POSE_DASHING = 2
POSE_PUNCHING = 151
CMD_PLAYER_STATE_UPLOAD = 2001
CHAT_FOLLOW_TRIGGERS = (1, 2)

STUCK_TRIGGER = 2.0
SLOW_DURATION = 8.0
SLOW_HZ = 1.5
SLOW_INTERVAL = 1.0 / SLOW_HZ

BLOCKED_TICKS = 4
SIDESTEP_DIST = 180.0
SIDESTEP_HOLD = 0.8

REGROUP_RADIUS = 700.0
REGROUP_WEIGHT = 0.6

JHUND_MAX_AGE = 10.0
JHUND_DASH_DIST = 6000.0
JHUND_SLOT_MIN = 120.0
JHUND_SLOT_MAX = 260.0
LEADER_DEADZONE = 220.0

def _log(line):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    with _log_lock:
        print(f"[{ts}] {line}", flush=True)
        try:
            with open(UDP_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {line}\n")
        except Exception:
            pass

def _tag(i, n):
    return f"{i:>2}/{n}"

def gen_nickname(prefix="vai"):
    chars = string.ascii_lowercase + string.digits
    suffix = ''.join(random.choices(chars, k=4))
    return f"{prefix}_{suffix}"

def enc_aes(data):
    return AES.new(KEY, AES.MODE_CBC, IV).encrypt(pad(data, 16))

def dec_aes(data):
    try:
        return unpad(AES.new(KEY, AES.MODE_CBC, IV).decrypt(data), 16)
    except ValueError:
        return AES.new(KEY, AES.MODE_CBC, IV).decrypt(data)

def sign_body(body):
    return hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()

def encode_open_id(open_id):
    return bytes(ord(open_id[i]) ^ _KEYSTREAM[i % len(_KEYSTREAM)] for i in range(len(open_id)))

def decode_jwt_payload(token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        p2 = parts[1] + "=" * (-len(parts[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(p2))
    except Exception:
        return {}

def enc_varint(v):
    out = bytearray()
    while True:
        b = v & 0x7F
        v >>= 7
        out.append(b | (0x80 if v else 0))
        if not v:
            return bytes(out)

def read_varint(data, off):
    v, s = 0, 0
    while True:
        b = data[off]
        off += 1
        v |= (b & 0x7F) << s
        if not (b & 0x80):
            return v, off
        s += 7

def ptag(f, wt):
    return enc_varint((f << 3) | wt)

def f_vint(f, n):
    return ptag(f, 0) + enc_varint(n)

def f_bytes(f, b):
    return ptag(f, 2) + enc_varint(len(b)) + b

def f_str(f, s):
    b = s.encode("utf-8")
    return ptag(f, 2) + enc_varint(len(b)) + b

def parse_proto(data):
    fields = {}
    i = 0
    while i < len(data):
        try:
            key, i = read_varint(data, i)
        except Exception:
            break
        fn, wt = key >> 3, key & 7
        try:
            if wt == 0:
                v, i = read_varint(data, i)
                fields.setdefault(fn, []).append(("varint", v))
            elif wt == 1:
                v = int.from_bytes(data[i:i+8], "little")
                i += 8
                fields.setdefault(fn, []).append(("u64", v))
            elif wt == 2:
                ln, i = read_varint(data, i)
                raw = data[i:i+ln]
                i += ln
                s_ok = False
                try:
                    s = raw.decode("utf-8")
                    if s.isprintable():
                        fields.setdefault(fn, []).append(("string", s))
                        s_ok = True
                except UnicodeDecodeError:
                    pass
                if not s_ok:
                    fields.setdefault(fn, []).append(("bytes", raw.hex()))
            elif wt == 5:
                v = int.from_bytes(data[i:i+4], "little")
                i += 4
                fields.setdefault(fn, []).append(("u32", v))
            else:
                break
        except Exception:
            break
    return fields

# ── Avatar Logic ─────────────────────────────────────────────
async def update_avatar(jwt_token, base_url):
    host = urlsplit(base_url).netloc
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "deflate, gzip",
        "Authorization": f"Bearer {jwt_token.strip()}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": host,
        "ReleaseVersion": "OB55",
        "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4.12f1",
    }

    actions = (
        ("ClaimAvatarProficiencyAward", AVATAR_BODY_HEX_1),
        ("ChooseHeadPic", AVATAR_BODY_HEX_2),
    )

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    timeout = aiohttp.ClientTimeout(total=15)
    ok = True

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for endpoint, body_hex in actions:
            payload = bytes.fromhex(body_hex.replace(" ", ""))
            req_headers = dict(headers)
            req_headers["X-GA-SV"] = str(int(time.time()))
            req_headers["Content-Length"] = str(len(payload))
            
            try:
                async with session.post(base_url + endpoint, headers=req_headers, data=payload, ssl=ssl_ctx) as response:
                    await response.read()
                    if not (200 <= response.status < 300):
                        ok = False
            except Exception:
                ok = False
    return ok

# ── Add Friend Logic ─────────────────────────────────────────
def Encrypt_ID(x):
    x = int(x)
    dec = [ '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']
    xxx= [ '1','01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f']
    x = x/128 
    if x>128:
        x =x/128
        if x >128:
            x= x/128
            if x>128:
                x= x/128
                strx= int(x)
                y= (x-int(strx))*128
                stry =str(int(y))
                z = (y-int(stry))*128
                strz =str(int(z))
                n =(z-int(strz))*128
                strn=str(int(n))
                m=(n-int(strn))*128
                return dec[int(m)]+dec[int(n)]+dec[int(z)]+dec[int(y)]+xxx[int(x)]
            else:
                strx= int(x)
                y= (x-int(strx))*128
                stry =str(int(y))
                z = (y-int(stry))*128
                strz =str(int(z))
                n =(z-int(strz))*128
                strn=str(int(n))
                return dec[int(n)]+dec[int(z)]+dec[int(y)]+xxx[int(x)]
        else:
            strx= int(x)
            y= (x-int(strx))*128
            stry =str(int(y))
            z = (y-int(stry))*128
            strz =str(int(z))
            return dec[int(z)]+dec[int(y)]+xxx[int(x)] 
    else:
        strx= int(x)
        if strx ==0:
            y= (x-int(strx))*128
            inty =int(y)
            return  xxx[inty]
        else:
            y= (x-int(strx))*128
            stry =str(int(y))
            return dec[int(y)]+xxx[int(x)]

def send_add_friend(author_uid, target_uid, token):
    region = str(decode_jwt_payload(token).get("lock_region") or "IND").upper()
    base_url = "https://client.ind.freefiremobile.com/" if region == "IND" else ("https://client.us.freefiremobile.com/" if region in {"BR", "US", "SAC", "NA"} else "https://clientbp.ppmainecoonghj.com/")
    
    encrypted_id = Encrypt_ID(target_uid)
    payload = f"08a7c4839f1e10{encrypted_id}1801"
    enc = enc_aes(bytes.fromhex(payload))
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Unity-Version": "2018.4.12f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB55",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)"
    }
    
    try:
        r = requests.post(base_url + "RequestAddingFriend", headers=headers, data=enc, timeout=15, verify=False)
        if r.status_code == 200:
            return True, "Success"
        return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)

async def add_friend_interactive():
    print(f"\n  Enter Target UID => ", end="")
    try: target_uid = input().strip()
    except (EOFError, KeyboardInterrupt): return
    if not target_uid.isdigit():
        print(f"  X Target UID must be numeric")
        return
        
    jwt_cache = _load_json_dict(JWT_CACHE_FILE)
    if not jwt_cache:
        print(f"  X No jwt.json found or empty.")
        return
        
    print(f"\n  Found {len(jwt_cache)} bot accounts in jwt.json.")
    print(f"  Starting friend requests to {target_uid}...\n")
    
    success = 0
    fail = 0
    for uid, data in jwt_cache.items():
        token = data.get("jwt")
        ingame_id = data.get("ingame_id", 0)
        
        if not token:
            print(f"  X Bot {ingame_id} => No JWT in cache")
            fail += 1
            continue
            
        ok, msg = await asyncio.to_thread(send_add_friend, ingame_id, target_uid, token)
        if ok:
            print(f"  ✔ Sent => Bot {ingame_id} (Author: {ingame_id})")
            success += 1
        else:
            print(f"  X Failed => Bot {ingame_id} ({msg})")
            fail += 1
            
        await asyncio.sleep(1.0)
        
    print(f"\n  DONE: {success} sent, {fail} failed.")

# ─────────────────────────────────────────────────────────────

def _decode_gri_block(body):
    if not body or len(body) < 2:
        return {}
    try:
        blen = struct.unpack_from("<H", body, 0)[0]
    except struct.error:
        return {}
    p, end, f = 2, min(2 + blen, len(body)), {}
    while p < end:
        fid = body[p]; p += 1
        if p >= end:
            break
        try:
            v, p = _rd_varint(body, p)
        except (IndexError, ValueError):
            break
        f[fid] = v
    return f

def decode_safezone(body):
    if not body:
        return None
    try:
        p = 0
        stage = body[p]; p += 1
        ox, p = _rd_varint(body, p); oz, p = _rd_varint(body, p)
        outer_r, p = _rd_varint(body, p)
        ix, p = _rd_varint(body, p); iz, p = _rd_varint(body, p)
        inner_r, p = _rd_varint(body, p)
        if p < len(body):
            p += 1
        start, p = _rd_varint(body, p)
        end, p = _rd_varint(body, p)
        return {
            "stage": stage,
            "outer_center": (_zag(ox), _zag(oz)), "outer_radius": outer_r,
            "inner_center": (_zag(ix), _zag(iz)), "inner_radius": inner_r,
            "start": start, "end": end,
        }
    except (IndexError, ValueError):
        return None

def _get_match_phase(body):
    f = _decode_gri_block(body)
    if 3 not in f:
        return None
    v = f[3]
    if v < 0x10000:
        return None
    return (v >> 16) & 0xFFFF, f.get(2), (v >> 32) & 0xFFFFFFFF, v & 0xFFFF

def parse_join_skills(body):
    out = []
    n = len(body)
    for i in range(n):
        if i > 0 and body[i - 1] >= 0x80:
            continue
        try:
            v, p = _rd_varint(body, i)
        except (IndexError, ValueError):
            continue
        if p - i < 2 or not (100 <= v <= 99999 and v % 100 == 6):
            continue
        chain = [v]
        q = p
        while q < n:
            try:
                v2, q2 = _rd_varint(body, q)
            except (IndexError, ValueError):
                break
            if q2 - q >= 2 and 100 <= v2 <= 99999 and v2 % 100 == 6:
                chain.append(v2); q = q2
            else:
                break
        if q < n and body[q] == 0x00 and (i == 0 or body[i - 1] in (0x00, 0x02, 0x08)):
            for c in chain:
                if c not in out:
                    out.append(c)
    return out

def parse_preset_skills(body):
    try:
        p = 0; vals = []
        while p < len(body):
            v, p = _rd_varint(body, p); vals.append(v)
    except (IndexError, ValueError):
        return []
    for i in range(1, len(vals) - 1):
        if vals[i - 1] == 0 and 100 <= vals[i] <= 99999 and vals[i + 1] == 1:
            out = []; j = i
            while j + 1 < len(vals) and 100 <= vals[j] <= 99999 and 1 <= vals[j + 1] <= 9:
                out.append((vals[j], vals[j + 1])); j += 2
            return out
    return []

def build_emote_body(emotion_id=EMOTE_ID, nickname="", server_tick=0, create_time=0):
    b = bytearray()
    _put_varint(b, int(emotion_id))
    b.append(0)
    b.append(0)
    b.append(0)
    _put_varint(b, 0xFFFFFFFF)
    _put_varint(b, int(server_tick) & 0xFFFFFFFF)
    _put_varint(b, int(create_time) & 0xFFFFFFFF)
    raw = nickname.encode("utf-8") if isinstance(nickname, str) else bytes(nickname)
    _put_zigvarint(b, len(raw))
    b += raw
    b.append(0)
    b.append(0)
    b.append(0)
    return bytes(b)
    
async def select_homer_loadout(token, base_url, account_id, skill_id=HOMER_SKILL_ID):
    url = f"{base_url.rstrip('/')}/SelectPresetLoadout"

    def _vi(n):
        o = bytearray()
        while True:
            b = n & 0x7F; n >>= 7
            o.append(b | (0x80 if n else 0))
            if not n:
                return bytes(o)

    def _pb(d):
        out = bytearray()
        for k, v in d.items():
            k = int(k)
            if isinstance(v, bool):
                v = int(v)
            if isinstance(v, int):
                out += _vi((k << 3) | 0) + _vi(v)
            elif isinstance(v, str):
                b = v.encode()
                out += _vi((k << 3) | 2) + _vi(len(b)) + b
            elif isinstance(v, (bytes, bytearray)):
                out += _vi((k << 3) | 2) + _vi(len(v)) + bytes(v)
            elif isinstance(v, dict):
                inner = _pb(v)
                out += _vi((k << 3) | 2) + _vi(len(inner)) + inner
        return bytes(out)

    fields = {
        1:  {1: int(skill_id)},
        2:  {1: int(skill_id), 2: 50462976, 3: 414929892933512066, 4: 0},
        6:  {1: {1: 1, 2: int(skill_id), 3: {1: 3, 2: 706},
                 6: "PRESET 1", 7: 1}},
        11: 1,
    }
    plain = _pb(fields)
    enc = enc_aes(plain)

    headers = {
        "Accept-Encoding": "gzip", "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "ReleaseVersion": _OB_VERSION, "User-Agent": USER_AGENT_UNITY,
        "X-GA": "v1 1", "X-Unity-Version": "2018.4.12f1",
        "Authorization": f"Bearer {token}",
        "Host": base_url.replace("https://", "").replace("http://", "").split("/")[0],
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=enc, headers=headers,
                                    ssl=False, timeout=20) as r:
                body = await r.read()
                _log(f"select_homer_loadout({account_id}) status={r.status} resp_len={len(body)}")
                return r.status == 200
    except Exception as e:
        _log(f"select_homer_loadout({account_id}) err: {e}")
        return False
        
def first_value(fields, field_num, want_kind=None):
    for kind, v in fields.get(field_num, []):
        if want_kind is None or kind == want_kind:
            return v
    return None

def _load_json_dict(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    out = []
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            p = line.split("|")
            if len(p) < 9:
                continue
            out.append({
                "uid": p[0],
                "pass": p[1],
                "name": p[2],
                "region": p[3],
                "open_id": p[4],
                "access_token": p[5],
                "jwt": p[6],
                "ingame_id": int(p[7]) if p[7].isdigit() else 0,
                "game_url": p[8],
            })
    return out

def append_account(acc):
    line = "|".join([
        acc["uid"], acc["pass"], acc["name"], acc["region"],
        acc["open_id"], acc["access_token"], acc["jwt"],
        str(acc["ingame_id"]), acc["game_url"],
    ])
    with _file_lock:
        with open(ACCOUNTS_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

def _extract_leave_info(decoded):
    if not isinstance(decoded, dict):
        return None, "UNKNOWN"
    data = decoded.get("5", {})
    if not isinstance(data, dict):
        return None, "UNKNOWN"
    lid = data.get("1")
    if isinstance(lid, dict):
        lid = lid.get("data")
    reason = data.get("2")
    if isinstance(reason, dict):
        reason = reason.get("data")
    if isinstance(reason, int):
        rname = LEAVE_REASONS.get(reason, f"UNKNOWN_{reason}")
    else:
        rname = f"UNKNOWN_{reason}" if reason is not None else "UNKNOWN"
    return lid, rname

def _dump_frame_response(tag, ptype, cmd, decoded, payload):
    # REDUCED LOGGING: Only print essential frames
    if cmd in (101, 117, 130, 103, 248, 250, 823, 538, 542, 1901):
        _log(f"{tag}  ↳ {describe(ptype, cmd)}  len={len(payload)}")

def collect_all_ints(obj, out):
    if isinstance(obj, dict):
        if "data" in obj and isinstance(obj["data"], int):
            out.add(obj["data"])
        for v in obj.values():
            collect_all_ints(v, out)
    elif isinstance(obj, list):
        for x in obj:
            collect_all_ints(x, out)
    elif isinstance(obj, int):
        out.add(obj)
        
def load_clan_tracker():
    return _load_json_dict(CLAN_TRACKER_FILE)

def save_clan_tracker(tracker):
    with _file_lock:
        with open(CLAN_TRACKER_FILE, "w", encoding="utf-8") as f:
            json.dump(tracker, f, indent=2, ensure_ascii=False)

def track_account_clan(uid, clan_id, account_name="", ingame_id=""):
    tracker = load_clan_tracker()
    if "clans" not in tracker:
        tracker["clans"] = {}
    if "accounts" not in tracker:
        tracker["accounts"] = {}
    clan_key = str(clan_id)
    if clan_key not in tracker["clans"]:
        tracker["clans"][clan_key] = {"accounts": [], "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    if uid not in tracker["clans"][clan_key]["accounts"]:
        tracker["clans"][clan_key]["accounts"].append(uid)
    tracker["accounts"][uid] = {
        "clan_id": clan_key,
        "name": account_name,
        "ingame_id": ingame_id,
        "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_clan_tracker(tracker)
    return True

def get_play_store_version():
    headers = {"User-Agent": USER_AGENT_WEB, "Accept-Language": "en-US,en;q=0.9"}
    html = requests.get(PLAYSTORE_URL, headers=headers, timeout=15).text
    versions = re.findall(r"\b(1\.\d{1,3}\.\d{1,3})\b", html)
    if not versions:
        raise RuntimeError("no version on playstore page")
    real = [v for v in versions if v != "1.000.000"]
    return (real or versions)[-1]

def fetch_ver_config(initial_version, region=None, lang=None):
    region = region or REGION
    lang = lang or REGION_LANG.get(region, "en")
    version = initial_version
    last = None
    for attempt in range(1, VER_MAX_ATTEMPTS + 1):
        url = (
            f"{VER_URL_BASE}?version={version}"
            f"&lang={lang}&device=android&channel=3rd_party&appstore=thirdparty"
            f"&region={region}&whitelist_version=1.7.0&whitelist_sp_version=1.0.0"
            f"&device_name=vivo%20V2538"
            f"&device_CPU=ARM64%20FP%20ASIMD%20AES"
            f"&device_GPU=Adreno%20%28TM%29%20722"
            f"&device_mem=7282"
        )
        try:
            cfg = requests.get(url, timeout=15).json()
        except Exception as e:
            last = e
            time.sleep(1.0 * attempt)
            continue
        if cfg.get("code") == 0:
            grp = REGION_GROUP.get(region, "OTHERS")
            cfg["region"] = region
            cfg["lang"] = lang
            cfg["country_code"] = region
            cfg["server_url"] = REGION_URLS[grp]["server"]
            cfg["client_url"] = REGION_URLS[grp]["client"]
            return cfg
        if cfg.get("remote_version"):
            version = cfg["remote_version"]
        last = cfg
        time.sleep(1.0 * attempt)
    raise RuntimeError(f"ver.php failed: {last}")

def get_datadome(tag, force=False):
    global _dd_session_cookie, _dd_expires_at
    with _dd_lock:
        now = time.time()
        if not force and _dd_session_cookie and _dd_expires_at > now:
            return _dd_session_cookie
        headers = {
            "User-Agent": USER_AGENT_WEB,
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://sso.garena.com/universal/register?locale=en-SG",
            "Origin": "https://sso.garena.com",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        payload = {
            "jsType": "le",
            "eventCounters": '{"mousemove":1,"click":1,"keydown":11}',
            "ddk": "AE3F04AD3F0D3A462481A337485081",
            "Referer": "https://sso.garena.com/universal/register?locale=en-SG",
            "request": "/universal/register?locale=en-SG",
            "responsePage": "origin",
            "ddv": "5.7.0",
        }
        last = None
        for attempt in range(1, DATADOME_MAX_RETRIES + 1):
            try:
                r = requests.post(DATADOME_URL, data=payload, headers=headers, timeout=15)
                r.raise_for_status()
                result = r.json()
            except Exception as e:
                last = e
                time.sleep(1.5 * attempt)
                continue
            if result.get("status") == 200 and result.get("cookie"):
                for part in result["cookie"].split(";"):
                    if "datadome=" in part:
                        dd = part.replace("datadome=", "").strip()
                        if dd:
                            _dd_session_cookie = dd
                            _dd_expires_at = now + 300.0
                            return dd
            last = result
            time.sleep(1.5 * attempt)
        raise RuntimeError(f"DataDome failed: {last}")

def _normalize_uid(uid):
    s = str(uid).strip()
    if s.isdigit():
        return int(s)
    return s

def _wait_register_slot(tag):
    global _last_register_time
    while True:
        with _gate_lock:
            now = time.time()
            wait = MIN_REGISTER_INTERVAL - (now - _last_register_time)
            if wait <= 0:
                _last_register_time = now
                return
        time.sleep(min(wait, 0.5))

def guest_register(tag, device_id, max_retries=REGISTER_MAX_RETRIES):
    pwd = ''.join(random.choices(string.ascii_uppercase + string.digits, k=64))
    payload = {"app_id": APP_ID, "client_type": CLIENT_TYPE, "password": pwd, "source": SOURCE}
    body = json.dumps(payload, separators=(",", ":"))
    last_err = None
    for attempt in range(1, max_retries + 1):
        _wait_register_slot(tag)
        datadome = get_datadome(tag, force=(attempt > 1 and attempt % 3 == 0))
        headers = {
            "User-Agent": USER_AGENT_MSDK,
            "Authorization": f"Signature {sign_body(body)}",
            "Cookie": f"datadome={datadome}",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        }
        try:
            r = requests.post(REGISTER_URL, data=body, headers=headers, timeout=25)
            data = r.json()
        except Exception as e:
            last_err = e
            time.sleep(2.0 * attempt)
            continue
        code = data.get("code")
        if code == 0:
            return str(data["data"]["uid"]), pwd
        if code in (1006, 1005):
            wait = min(REGISTER_BACKOFF_START * (2 ** (attempt - 1)), REGISTER_BACKOFF_MAX)
            last_err = data
            time.sleep(wait)
            continue
        raise RuntimeError(f"guest:register failed: {data}")
    raise RuntimeError(f"guest:register gave up: {last_err}")

async def give_newbie_roles(token, base_url, account_id):
    url = f"{base_url.rstrip('/')}/GiveAccountNewbieRoles"
    plain = bytes([0x08, 0x01])
    enc = enc_aes(plain)
    host = base_url.replace("https://", "").replace("http://", "").split("/")[0]
    headers = {
        "Accept-Encoding": "gzip", "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "ReleaseVersion": _OB_VERSION, "User-Agent": USER_AGENT_UNITY,
        "X-GA": "v1 1", "X-Unity-Version": "2018.4.12f1",
        "Authorization": f"Bearer {token}", "Host": host,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=enc, headers=headers,
                                    ssl=False, timeout=20) as r:
                rb = await r.read()
                _log(f"give_newbie_roles({account_id}) status={r.status} hex={rb.hex()}")
                return r.status == 200
    except Exception as e:
        _log(f"give_newbie_roles({account_id}) err: {e}")
        return False
        
def guest_token(tag, uid, device_id, password):
    uid_val = _normalize_uid(uid)
    payload = {
        "client_id": APP_ID, "client_secret": SECRET, "client_type": CLIENT_TYPE,
        "device_id": device_id, "password": password, "response_type": "token", "uid": uid_val,
    }
    body = json.dumps(payload, separators=(",", ":"))
    datadome = get_datadome(tag)
    last_err = None
    for attempt in range(1, 5):
        headers = {
            "User-Agent": USER_AGENT_MSDK,
            "Authorization": f"Signature {sign_body(body)}",
            "Cookie": f"datadome={datadome}",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        }
        try:
            r = requests.post(GRANT_URL, data=body, headers=headers, timeout=20)
            data = r.json()
        except Exception as e:
            last_err = e
            time.sleep(2.0 * attempt)
            continue
        code = data.get("code")
        if code == 0:
            return data["data"]
        if code in (1006, 1005):
            wait = min(REGISTER_BACKOFF_START * (2 ** (attempt - 1)), REGISTER_BACKOFF_MAX)
            last_err = data
            time.sleep(wait)
            continue
        last_err = data
        if attempt < 4:
            datadome = get_datadome(tag, force=True)
            time.sleep(1.5 * attempt)
            continue
    raise RuntimeError(f"guest/token:grant failed: {last_err}")

def major_register(tag, open_id, access_token, name, password, cfg):
    url = cfg["server_url"].rstrip("/") + "/MajorRegister"
    lang = cfg.get("lang", "en")
    body = f_str(1, name)
    body += f_str(2, access_token)
    body += f_str(3, open_id)
    body += f_vint(5, 102000007)
    body += f_vint(6, 4)
    body += f_vint(7, 1)
    body += f_vint(13, 1)
    body += f_bytes(14, encode_open_id(open_id))
    body += f_str(15, lang)
    body += f_vint(16, 2)
    body += f_str(22, password)
    headers = {
        "User-Agent": USER_AGENT_UNITY,
        "Accept": "*/*",
        "Accept-Encoding": "deflate, gzip",
        "Authorization": "Bearer",
        "X-GA": "v1 1",
        "X-GA-SV": str(int(time.time())),
        "ReleaseVersion": cfg["latest_release_version"],
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2018.4.12f1",
    }
    r = requests.post(url, data=enc_aes(body), headers=headers, timeout=20)
    try:
        fields = parse_proto(dec_aes(r.content))
    except Exception:
        fields = parse_proto(r.content)
    result = first_value(fields, 1, "varint")
    return result == 1
    
def _vai_varint(n):
    r = bytearray()
    while n > 127:
        r.append((n & 127) | 128)
        n >>= 7
    r.append(n)
    return bytes(r)

def _enc_fields(fields):
    pb = b""
    for k, v in fields.items():
        f = int(k)
        if isinstance(v, bool):
            pb += _vai_varint((f << 3) | 0) + _vai_varint(1 if v else 0)
        elif isinstance(v, int):
            pb += _vai_varint((f << 3) | 0) + _vai_varint(v)
        elif isinstance(v, str):
            ev = v.encode()
            pb += _vai_varint((f << 3) | 2) + _vai_varint(len(ev)) + ev
        elif isinstance(v, (bytes, bytearray)):
            pb += _vai_varint((f << 3) | 2) + _vai_varint(len(v)) + bytes(v)
    return AES.new(KEY, AES.MODE_CBC, IV).encrypt(pad(pb, AES.block_size)).hex()

def send_choose_newbie_choice(account_id, cfg, choice1=3, choice2=3):
    body_hex = _enc_fields({"1": int(account_id), "2": int(choice1), "3": int(choice2)})
    headers = {
        "User-Agent": USER_AGENT_UNITY,
        "Accept": "*/*",
        "Accept-Encoding": "deflate, gzip",
        "X-GA-SV": str(int(time.time())),
        "Authorization": "Bearer",
        "X-GA": "v1 1",
        "ReleaseVersion": cfg["latest_release_version"],
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2018.4.12f1",
    }
    url = cfg["server_url"].rstrip("/") + "/ChooseNewbieChoice"
    try:
        r = requests.post(url, headers=headers, data=bytes.fromhex(body_hex),
                          verify=False, allow_redirects=False, timeout=60)
        return r.status_code, r.content
    except Exception as e:
        return -1, str(e).encode()

def build_major_login_pb2(open_id, access_token, platform, client_version, region="IND",
                          country="IND", lang="en"):
    p = MajorloginReqBuild_pb2.MajorLogin()
    p.open_id = open_id
    p.access_token = access_token
    p.client_version = client_version
    p.event_time = str(int(time.time()))
    p.game_name = "free fire"
    p.platform_id = 1
    p.system_software = "Android OS 16 / API-36 (BP4A.251205.006/M066BXXS8CZI1)"
    p.system_hardware = "Handheld"
    p.telecom_operator = "WIFI"
    p.network_type = "WIFI"
    p.screen_width = 1600
    p.screen_height = 720
    p.screen_dpi = "300"
    p.processor_details = "ARM64 FP ASIMD AES | 2400 | 8"
    p.memory = 3507
    p.gpu_renderer = "Mali-G57 MC2"
    p.gpu_version = "OpenGL ES 3.2 v1.r38p1"
    p.unique_device_id = "Google|6acc6a56-b955-42d6-9920-7c3faa8992e3"
    p.client_ip = "122.174.21.30"
    p.language = lang
    p.open_id_type = "4"
    p.device_type = "Handheld"
    p.device_model = "samsung SM-M066B"
    p.country_code = country
    p.platform_sdk_id = 1
    p.network_operator_a = "WIFI"
    p.network_type_a = "WIFI"
    p.client_using_version = SESSION_HASH
    p.external_storage_total = 47195
    p.external_storage_available = 19418
    p.internal_storage_total = 5135
    p.internal_storage_available = 5135
    p.game_disk_storage_available = 19546
    p.game_disk_storage_total = 47195
    p.external_sdcard_avail_storage = 19546
    p.external_sdcard_total_storage = 47195
    p.field_70 = 4
    p.login_by = 3
    p.library_path = "/data/app/~~bsxEK2UVui2u9YoL_QKi_w==/com.garena.game.ffi-p7Uh_JDc-8hCjRgLvsaRqg==/lib/arm64"
    p.reg_avatar = 3
    p.library_token = ("dd9d4c174e0472d34b7fd34bd5924bc9|"
                       "/data/app/~~bsxEK2UVui2u9YoL_QKi_w==/com.garena.game.ffi-p7Uh_JDc-8hCjRgLvsaRqg==/base.apk")
    p.channel_type = 3
    p.cpu_type = 2
    p.cpu_architecture = "64"
    p.client_version_code = "2019121269"
    p.field_85 = 3
    p.graphics_api = "OpenGLES2"
    p.supported_astc_bitset = 8191
    p.login_open_id_type = 4
    p.loading_time = 13070
    p.release_channel = "android"
    p.extra_info = ("KqsHT3kf8XDT3vqFEnlSSQFMl5SRiWL2SxIxcx47LozWRI7AqvwWJ9eJ/"
                    "fXX0amawG9xA6DLOyWSJCij9Fp7M5o3bzp7/MjO1jDqX8PwDD8qq5vO")
    p.android_engine_init_flag = 111107
    p.field_96 = json.dumps({"cur_rate": [90, 60], "support_etc2": False},
                            separators=(",", ":"))
    p.if_push = 1
    p.is_vpn = 1
    p.origin_platform_type = "4"
    p.primary_platform_type = "4"
    p.field_102 = b""
    p.field_104 = 80395
    p.field_105 = 1
    p.field_106 = ("https://dl-tata.freefireind.in/live/ABHotUpdates/"
                   "|https://core-tata.freefireind.in/live/ABHotUpdates/"
                   "|dff941d41e6e3a9e76f05ed71fdc8d87")
    p.field_107 = "1.6168622e0868ddbd"
    return enc_aes(p.SerializeToString())

def build_get_login_data_pb2(open_id, access_token, platform, client_version, jwt,
                             server_url, region="IND", country="IND", lang="en"):
    p = MajorloginReqBuild_pb2.MajorLogin()
    p.open_id = open_id
    p.access_token = access_token
    p.client_version = client_version
    p.event_time = str(int(time.time()))
    p.game_name = "free fire"
    p.platform_id = 1
    p.system_software = "Android OS 16 / API-36 (BP4A.251205.006/M066BXXS8CZI1)"
    p.system_hardware = "Handheld"
    p.telecom_operator = "WIFI"
    p.network_type = "WIFI"
    p.screen_width = 1600
    p.screen_height = 720
    p.screen_dpi = "300"
    p.processor_details = "ARM64 FP ASIMD AES | 2400 | 8"
    p.memory = 3507
    p.gpu_renderer = "Mali-G57 MC2"
    p.gpu_version = "OpenGL ES 3.2 v1.r38p1"
    p.unique_device_id = "Google|6acc6a56-b955-42d6-9920-7c3faa8992e3"
    p.client_ip = "122.174.21.30"
    p.language = lang
    p.open_id_type = "4"
    p.device_type = "Handheld"
    p.device_model = "samsung SM-M066B"
    p.country_code = country
    p.platform_sdk_id = 1
    p.network_operator_a = "WIFI"
    p.network_type_a = "WIFI"
    p.client_using_version = SESSION_HASH
    p.external_storage_total = 47195
    p.external_storage_available = 19418
    p.internal_storage_total = 5135
    p.internal_storage_available = 5135
    p.game_disk_storage_available = 19546
    p.game_disk_storage_total = 47195
    p.external_sdcard_avail_storage = 19546
    p.external_sdcard_total_storage = 47195
    p.field_70 = 4
    p.login_by = 3
    p.library_path = "/data/app/~~bsxEK2UVui2u9YoL_QKi_w==/com.garena.game.ffi-p7Uh_JDc-8hCjRgLvsaRqg==/lib/arm64"
    p.reg_avatar = 3
    p.library_token = ("dd9d4c174e0472d34b7fd34bd5924bc9|"
                       "/data/app/~~bsxEK2UVui2u9YoL_QKi_w==/com.garena.game.ffi-p7Uh_JDc-8hCjRgLvsaRqg==/base.apk")
    p.channel_type = 3
    p.cpu_type = 2
    p.cpu_architecture = "64"
    p.client_version_code = "2019121269"
    p.field_85 = 3
    p.graphics_api = "OpenGLES2"
    p.supported_astc_bitset = 8191
    p.login_open_id_type = 4
    p.loading_time = 13070
    p.release_channel = "android"
    p.extra_info = ("KqsHT3kf8XDT3vqFEnlSSQFMl5SRiWL2SxIxcx47LozWRI7AqvwWJ9eJ/"
                    "fXX0amawG9xA6DLOyWSJCij9Fp7M5o3bzp7/MjO1jDqX8PwDD8qq5vO")
    p.android_engine_init_flag = 111107
    p.field_96 = json.dumps({"cur_rate": [90, 60], "support_etc2": False},
                            separators=(",", ":"))
    p.if_push = 1
    p.is_vpn = 1
    p.origin_platform_type = "4"
    p.primary_platform_type = "4"
    p.field_102 = b""
    p.field_104 = 80395
    p.field_105 = 1
    p.field_106 = ("https://dl-tata.freefireind.in/live/ABHotUpdates/"
                   "|https://core-tata.freefireind.in/live/ABHotUpdates/"
                   "|dff941d41e6e3a9e76f05ed71fdc8d87")
    p.field_107 = "1.6168622e0868ddbd"
    return enc_aes(p.SerializeToString())

def major_login(tag, open_id, access_token, cfg, platform, region=None):
    url = cfg["server_url"].rstrip("/") + "/MajorLogin"
    plain = build_major_login_pb2(open_id, access_token, platform,
                                  cfg["remote_version"], cfg.get("region", "IND"),
                                  cfg.get("country_code", "IN"), cfg.get("lang", "en"))
    headers = {
        "User-Agent": USER_AGENT_UNITY,
        "Accept": "*/*",
        "Accept-Encoding": "deflate, gzip",
        "Authorization": "Bearer",
        "X-GA": "v1 1",
        "X-GA-SV": str(int(time.time())),
        "ReleaseVersion": cfg["latest_release_version"],
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2018.4.12f1",
    }
    r = requests.post(url, data=plain, headers=headers, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"MajorLogin HTTP {r.status_code}")
    body = r.content

    def _try(blob):
        if len(blob) < 10:
            return None
        try:
            m = MajorLoginResponse()
            m.ParseFromString(blob)
            if getattr(m, "token", "") and getattr(m, "account_id", 0):
                return m
        except Exception:
            return None

    cand = _try(body)
    if not cand and len(body) > 64:
        cand = _try(body[64:])
    if not cand:
        for off in range(1, min(128, len(body))):
            cand = _try(body[off:])
            if cand:
                break
    if not cand:
        raise RuntimeError("MajorLogin parse failed")
    return {
        "account_id": cand.account_id,
        "jwt": cand.token,
        "game_url": getattr(cand, "server_url", "") or cfg["server_url"],
        "region": getattr(cand, "lock_region", "") or cfg.get("region", "IND"),
        "aes_key": getattr(cand, "ak", b""),
        "aes_iv": getattr(cand, "aiv", b""),
        "server_time": getattr(cand, "kts", 0),
    }

def get_login_data(tag, open_id, access_token, cfg, platform, jwt):
    url = cfg["client_url"].rstrip("/") + "/GetLoginData"
    plain = build_get_login_data_pb2(open_id, access_token, platform,
                                     cfg["remote_version"], jwt,
                                     cfg["client_url"], cfg.get("region", "IND"),
                                     cfg.get("country_code", "IN"), cfg.get("lang", "en"))
    headers = {
        "User-Agent": USER_AGENT_UNITY,
        "Accept": "*/*",
        "Accept-Encoding": "deflate, gzip",
        "Authorization": f"Bearer {jwt}",
        "X-GA": "v1 1",
        "X-GA-SV": str(int(time.time())),
        "ReleaseVersion": cfg["latest_release_version"],
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2018.4.12f1",
    }
    r = requests.post(url, data=plain, headers=headers, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"GetLoginData HTTP {r.status_code}")
    body = r.content

    def _try(blob):
        try:
            m = PorTs_pb2.GetLoginData()
            m.ParseFromString(blob)
            if getattr(m, "AccountUID", 0) or getattr(m, "Online_IP_Port", ""):
                return m
        except Exception:
            return None

    cand = _try(body)
    if not cand and len(body) > 64:
        cand = _try(body[64:])
    if not cand:
        for off in range(1, min(128, len(body))):
            cand = _try(body[off:])
            if cand:
                break
    if not cand:
        raise RuntimeError("GetLoginData parse failed")
    return {
        "account_id": getattr(cand, "AccountUID", 0),
        "region": getattr(cand, "Region", "") or cfg.get("region", "IND"),
        "nickname": getattr(cand, "Nickname", ""),
        "game_server": getattr(cand, "Online_IP_Port", ""),
        "chat_server": getattr(cand, "Chat_IP_Port", ""),
        "event_url": getattr(cand, "Event_URL", ""),
    }

def build_region_cfg(region):
    region = region.upper()
    grp = REGION_GROUP.get(region, "OTHERS")
    cfg = dict(HARDCODED_CONFIG)
    cfg["region"] = region
    cfg["lang"] = REGION_LANG.get(region, "en")
    cfg["country_code"] = region
    cfg["server_url"] = REGION_URLS[grp]["server"]
    cfg["client_url"] = REGION_URLS[grp]["client"]
    return cfg

async def _equip_homer_at_gen(jwt, server_url, account_id):
    await give_newbie_roles(jwt, server_url, account_id)
    await asyncio.sleep(0.6)
    await select_homer_loadout(jwt, server_url, account_id)

def create_one_account(index, total, cfg, custom_name=None):
    tag = _tag(index, total)
    time.sleep(random.uniform(0.05, 0.5))
    try:
        print(f"  [{tag}] register...", end="", flush=True)
        device_id = "02-" + str(uuid.uuid4())
        uid, password = guest_register(tag, device_id)
        print(f" uid={uid}", end="", flush=True)

        print(f"  token...", end="", flush=True)
        tokens = guest_token(tag, uid, device_id, password)
        open_id = tokens["open_id"]
        access_token = tokens["access_token"]
        platform = int(tokens.get("platform", tokens.get("main_active_platform", 4)) or 4)
        print(f" ok", end="", flush=True)

        print(f"  nick...", end="", flush=True)
        nickname = gen_nickname(custom_name if custom_name else "vai")
        print(f" {nickname}", end="", flush=True)

        print(f"  majreg...", end="", flush=True)
        ok = major_register(tag, open_id, access_token, nickname, password, cfg)
        print(f" {'ok' if ok else 'skip'}", end="", flush=True)

        print(f"  newbie...", end="", flush=True)
        newbie_status, _ = send_choose_newbie_choice(int(uid), cfg, 3, 3)
        print(f" {newbie_status}", end="", flush=True)

        ingame_id   = 0
        jwt_token   = ""
        game_server = ""
        chat_server = ""
        server_url  = cfg["server_url"]
        login_result = None

        if ok:
            print(f"  login...", end="", flush=True)
            for attempt in range(1, 4):
                try:
                    login_result = major_login(tag, open_id, access_token, cfg, platform, cfg.get("region", "IND"))
                    break
                except Exception as e:
                    login_result = None
                    if attempt < 3:
                        time.sleep(2.0 * attempt)
                    else:
                        print(f" fail({e})", end="", flush=True)
            if login_result:
                ingame_id  = int(login_result.get("account_id") or 0)
                jwt_token  = login_result.get("jwt") or ""
                server_url = login_result.get("game_url") or cfg["server_url"]
                print(f" ok", end="", flush=True)
            else:
                ok = False

        if ok and jwt_token:
            print(f"  profile...", end="", flush=True)
            try:
                ld = get_login_data(tag, open_id, access_token, cfg, platform, jwt_token)
                game_server = ld.get("game_server", "")
                chat_server = ld.get("chat_server", "")
                print(f" ok", end="", flush=True)
            except Exception as e:
                print(f" fail({e})", end="", flush=True)

            time.sleep(1.5)

            print(f"  role...", end="", flush=True)
            role_ok = False
            for attempt in range(1, 4):
                try:
                    role_ok = asyncio.run(give_newbie_roles(jwt_token, server_url, ingame_id))
                except Exception as e:
                    role_ok = False
                if role_ok:
                    print(f" ok", end="", flush=True)
                    break
                if attempt < 3:
                    time.sleep(2.0 * attempt)
                else:
                    print(f" FAIL", end="", flush=True)

            print(f"  equip...", end="", flush=True)
            try:
                asyncio.run(select_homer_loadout(jwt_token, server_url, ingame_id))
                print(f" ok", end="", flush=True)
            except Exception as e:
                print(f" FAIL({e})", end="", flush=True)

            print(f"  avatar...", end="", flush=True)
            try:
                client_url = cfg.get("client_url", "https://client.ind.freefiremobile.com/")
                if not client_url.endswith("/"): client_url += "/"
                avatar_ok = asyncio.run(update_avatar(jwt_token, client_url))
                print(f" ok" if avatar_ok else f" skip", end="", flush=True)
            except Exception as e:
                print(f" fail({e})", end="", flush=True)

            print(f"  cache...", end="", flush=True)
            try:
                _set_cached_jwt(uid, {
                    "jwt":         jwt_token,
                    "key":         login_result.get("aes_key") or b"",
                    "iv":          login_result.get("aes_iv")  or b"",
                    "ts":          login_result.get("server_time", 0),
                    "game_server": game_server,
                    "chat_server": chat_server,
                    "server_url":  server_url,
                    "region":      cfg.get("region", cfg["country_code"]),
                    "ingame_id":   ingame_id,
                })
                print(f" ok", end="", flush=True)
            except Exception as e:
                print(f" fail({e})", end="", flush=True)

        account = {
            "uid": uid,
            "pass": password,
            "name": nickname,
            "ingame_id": ingame_id,
            "region": cfg["country_code"],
            "open_id": open_id,
            "access_token": access_token,
            "refresh_token": tokens.get("refresh_token"),
            "jwt": jwt_token,
            "game_server": game_server,
            "chat_server": chat_server,
            "game_url": server_url,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        append_account(account)

        global _success_count
        with _count_lock:
            _success_count += 1
        print(f" done", flush=True)
        return account
    except Exception as e:
        global _failure_count
        with _count_lock:
            _failure_count += 1
        print(f"  X [{tag}] FAILED: {e}")
        return None

def ask_region_menu(default="IND"):
    print(f"\n  Choose Region:")
    row = []
    for i, r in enumerate(REGION_LIST, 1):
        row.append(f"{i:>2}. {r}")
        if i % 3 == 0:
            print(f"      " + "      ".join(row))
            row = []
    if row:
        print(f"      " + "      ".join(row))
    while True:
        try:
            raw = input("  > ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
        if not raw:
            return default
        if raw in REGION_LIST:
            return raw
        if raw.isdigit() and 1 <= int(raw) <= len(REGION_LIST):
            return REGION_LIST[int(raw) - 1]
        print(f"  ! invalid, try again")

def generate_accounts_interactive():
    print(f"\n  Gen Count => ", end="")
    try:
        count = int(input().strip())
    except (ValueError, EOFError, KeyboardInterrupt):
        return []
    if count <= 0:
        return []

    print(f"  Name => ", end="")
    try:
        name_prefix = input().strip()
    except (EOFError, KeyboardInterrupt):
        return []
    if not name_prefix:
        name_prefix = "vai"

    global REGION, LANG_CODE
    REGION = ask_region_menu(default=REGION)
    LANG_CODE = REGION_LANG.get(REGION, "en")
    print(f"\n  Region => {REGION}\n")

    cfg = build_region_cfg(REGION)

    try:
        pv = get_play_store_version()
        fresh = fetch_ver_config(pv, region=REGION, lang=LANG_CODE)
        for k, v in fresh.items():
            if v:
                cfg[k] = v
    except Exception:
        pass

    accounts = []
    for i in range(1, count + 1):
        try:
            acc = create_one_account(i, count, cfg, name_prefix)
            if acc:
                accounts.append(acc)
                print(f"  Gen => {acc['name']}")
        except Exception as e:
            print(f"  X [{i}/{count}] failed: {e}")
        time.sleep(0.5)

    return accounts

async def EnC_Vr(N):
    if N < 0:
        return b''
    H = []
    while True:
        BesTo = N & 0x7F
        N >>= 7
        if N:
            BesTo |= 0x80
        H.append(BesTo)
        if not N:
            break
    return bytes(H)

async def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return await EnC_Vr(field_header) + await EnC_Vr(value)

async def CrEaTe_LenGTh(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return await EnC_Vr(field_header) + await EnC_Vr(len(encoded_value)) + encoded_value

async def CrEaTe_ProTo(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    nested = await CrEaTe_ProTo(item)
                    packet.extend(await CrEaTe_LenGTh(field, nested))
                elif isinstance(item, int):
                    packet.extend(await CrEaTe_VarianT(field, item))
                elif isinstance(item, (str, bytes)):
                    packet.extend(await CrEaTe_LenGTh(field, item))
        elif isinstance(value, dict):
            nested_packet = await CrEaTe_ProTo(value)
            packet.extend(await CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(await CrEaTe_VarianT(field, value))
        elif isinstance(value, (str, bytes)):
            packet.extend(await CrEaTe_LenGTh(field, value))
    return packet

async def encrypted_proto(encoded_hex):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(bytes(encoded_hex), AES.block_size)
    return cipher.encrypt(padded_message)

async def GeNeRaTeAccEss(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    versions = ['4.0.18P6', '4.0.19P7', '4.0.20P1', '4.1.0P3', '4.1.5P2', '4.2.1P8', '4.2.3P1', '5.0.1B2', '5.0.2P4', '5.1.0P1', '5.2.0B1', '5.2.5P3', '5.3.0B1', '5.3.2P2', '5.4.0P1', '5.4.3B2', '5.5.0P1', '5.5.2P3']
    models = ['SM-A125F', 'SM-A225F', 'SM-A325M', 'SM-A515F', 'SM-A725F', 'SM-M215F', 'SM-M325FV', 'Redmi 9A', 'Redmi 9C', 'POCO M3', 'POCO M4 Pro', 'RMX2185', 'RMX3085', 'moto g(9) play', 'CPH2239', 'V2027', 'OnePlus Nord', 'ASUS_Z01QD']
    android_versions = ['9', '10', '11', '12', '13', '14']
    languages = ['en-US', 'es-MX', 'pt-BR', 'id-ID', 'ru-RU', 'hi-IN']
    countries = ['USA', 'MEX', 'BRA', 'IDN', 'RUS', 'IND']
    ua = (f"GarenaMSDK/{random.choice(versions)}({random.choice(models)};Android {random.choice(android_versions)};{random.choice(languages)};{random.choice(countries)};)")
    headers = {"Host": "100067.connect.garena.com", "User-Agent": ua, "Content-Type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip, deflate, br", "Connection": "close"}
    data = {"uid": uid, "password": password, "response_type": "token", "client_type": "2", "client_secret": SECRET, "client_id": "100067"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status != 200: return None, None, None
                response_data = await response.json()
                return response_data.get("open_id"), response_data.get("access_token"), response_data.get("platform")
    except Exception:
        return None, None, None

async def SendRequestJoinClan(base_url, jwt, clan_id, region, account_id):
    url = f"{base_url.rstrip('/')}/RequestJoinClan"
    body = bytearray()
    body += f_vint(1, int(clan_id))
    payload = enc_aes(bytes(body))
    headers = {"User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)", "Accept": "*/*", "Accept-Encoding": "deflate, gzip", "Authorization": f"Bearer {jwt}", "X-GA": "v1 1", "X-GA-SV": str(int(time.time())), "ReleaseVersion": _OB_VERSION, "Content-Type": "application/x-www-form-urlencoded", "X-Unity-Version": "2018.4.12f1", "Connection": "Keep-Alive", "Host": base_url.replace("https://", "").replace("http://", "").split("/")[0], "X-Region": str(region).upper()}
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_context) as response:
            resp = await response.read()
            return response.status, resp

async def join_clan_for_account(account, clan_id):
    uid = str(account.get("uid") or "").strip()
    password = account.get("pass") or account.get("password")
    if not uid or not password: return False, "Missing uid or password"
    account_region = (account.get("region") or REGION).upper()
    try:
        open_id, access_token, platform = await GeNeRaTeAccEss(uid, password)
    except Exception as e:
        return False, f"Token grant failed: {e}"
    if not open_id or not access_token: return False, "Failed to get token"
    platform = int(platform or 4)
    cfg_local = build_region_cfg(account_region)
    try:
        login = await asyncio.to_thread(major_login, "[clan]", open_id, access_token, cfg_local, platform, account_region)
    except Exception as e:
        msg = str(e)
        if "HTTP 400" in msg: return False, f"MajorLogin 400 — account region is not {account_region}"
        return False, f"MajorLogin failed: {e}"
    jwt = login.get("jwt")
    account_id = int(login.get("account_id") or 0)
    base_url = login.get("game_url") or cfg_local["server_url"]
    payload = decode_jwt_payload(jwt) if jwt else {}
    region_from_jwt = (payload.get("lock_region") or account_region).upper()
    if region_from_jwt != account_region: return False, f"Region mismatch: acc={account_region} jwt={region_from_jwt}"
    try:
        status, resp = await SendRequestJoinClan(base_url, jwt, clan_id, region_from_jwt, account_id)
    except Exception as e:
        return False, f"JoinClan failed: {e}"
    if status == 200:
        track_account_clan(uid, clan_id, account.get("name", ""), account.get("ingame_id", ""))
        return True, "Successfully sent join request"
    try:
        body_preview = resp[:200].decode("utf-8", "replace")
    except Exception:
        body_preview = ""
    if status == 400 and ("already" in body_preview.lower() or "in clan" in body_preview.lower()):
        track_account_clan(uid, clan_id, account.get("name", ""), account.get("ingame_id", ""))
        return True, "Already in clan (marked)"
    return False, f"HTTP {status} body={body_preview!r}"

async def join_clan_interactive():
    print(f"\n  Enter Guild Uid => ", end="")
    try: clan_id = input().strip()
    except (EOFError, KeyboardInterrupt): return
    if not clan_id or not clan_id.isdigit():
        print(f"  X Guild Uid must be numeric")
        return
    accounts = load_accounts()
    if not accounts:
        print(f"  X No accounts found.")
        return
    tracker = load_clan_tracker()
    accounts_in_clans = tracker.get("accounts", {})
    available = [a for a in accounts if a.get("uid") not in accounts_in_clans]
    if not available:
        print(f"  ! All accounts already in clans.")
        return
    print()
    for acc in available:
        ok_flag, msg = await join_clan_for_account(acc, clan_id)
        if ok_flag: print(f"  Joined => {acc.get('name', '?')}")
        else: print(f"  X {acc.get('name', '?')} => {msg}")
        await asyncio.sleep(1.0)

def _to_bytes(v):
    if isinstance(v, bytes): return v
    if isinstance(v, str):
        try: return bytes.fromhex(v)
        except ValueError: return v.encode()
    if v is None: raise ValueError("cannot convert None")
    return bytes(v)

AUTH_AES_KEY = bytes([0x19, 0x47, 0xB9, 0x74, 0xD9, 0x73, 0xF3, 0x7F, 0x42, 0x06, 0x01, 0x38, 0x42, 0x00, 0x10, 0x30])
AUTH_AES_IV = bytes([0x28, 0x7F, 0xCA, 0x7A, 0xF9, 0x67, 0xF3, 0x7A, 0x65, 0x02, 0x01, 0x10, 0x40, 0x40, 0x00, 0x30])
AUTH_CMD = 0x65

def _auth_region_byte(region):
    reg = str(region or "IND").upper()
    if reg == "IND": return 0x14
    if reg == "BD": return 0x19
    if reg == "ME": return 0x15
    return 0x15

async def build_auth_datagram(token, account_id, region=REGION):
    payload = token.encode("utf-8") if isinstance(token, str) else token
    p = 16 - (len(payload) % 16)
    data = AES.new(AUTH_AES_KEY, AES.MODE_CBC, AUTH_AES_IV).encrypt(payload + bytes([p]) * p)
    out = bytearray()
    out.append(AUTH_CMD & 0xFF)
    out.append(_auth_region_byte(region) & 0xFF)
    out += struct.pack(">Q", int(account_id) & 0xFFFFFFFFFFFFFFFF)
    out += struct.pack(">I", int(time.time()) & 0xFFFFFFFF)
    out += struct.pack(">i", len(data))
    out += data
    return bytes(out)

async def build_auth_packet(account_id, token, server_time, key, iv, region=REGION, typ="OnLine"):
    uid_hex = f"{int(account_id):016x}"
    ts_hex = f"{int(server_time):08x}"
    enc = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(token.encode(), 16)).hex()
    enc_len = f"{len(enc) // 2:08x}"
    reg = str(region).upper()
    if reg == "BD": pre_on, pre_chat = "7119", "9219"
    elif reg == "IND": pre_on, pre_chat = "7114", "9214"
    else: pre_on, pre_chat = "7115", "9215"
    if typ == "OnLine":
        return bytes.fromhex(pre_on + uid_hex + ts_hex + "00000000" + enc_len + enc)
    return bytes.fromhex(pre_chat + uid_hex + ts_hex + enc_len + enc)

async def send_keep_alive(region=REGION):
    reg = str(region).upper()
    return bytes.fromhex("0214" if reg == "IND" else ("0219" if reg == "BD" else "0215"))

CRC7_TABLE = bytes([0,9,18,27,36,45,54,63,72,65,90,83,108,101,126,119,25,16,11,2,61,52,47,38,81,88,67,74,117,124,103,110,50,59,32,41,22,31,4,13,122,115,104,97,94,87,76,69,43,34,57,48,15,6,29,20,99,106,113,120,71,78,85,92,100,109,118,127,64,73,82,91,44,37,62,55,8,1,26,19,125,116,111,102,89,80,75,66,53,60,39,46,17,24,3,10,86,95,68,77,114,123,96,105,30,23,12,5,58,51,40,33,79,70,93,84,107,98,121,112,7,14,21,28,35,42,49,56,65,72,83,90,101,108,119,126,9,0,27,18,45,36,63,54,88,81,74,67,124,117,110,103,16,25,2,11,52,61,38,47,115,122,97,104,87,94,69,76,59,50,41,32,31,22,13,4,106,99,120,113,78,71,92,85,34,43,48,57,6,15,20,29,37,44,55,62,1,8,19,26,109,100,127,118,73,64,91,82,60,53,46,39,24,17,10,3,116,125,102,111,80,89,66,75,23,30,5,12,51,58,33,40,95,86,77,68,123,114,105,96,14,7,28,21,42,35,56,49,70,79,84,93,98,107,112,121])

_DELTA = 0x9E3779B9
_ROUNDS = 16
_FIELD_SIZES = {0: 1, 1: 2, 2: 2, 3: 1, 4: 2}
_FIELD_NAMES = {0: "sendOption", 1: "cmd", 2: "orderId", 3: "flags", 4: "length"}
HDR_RELIABLE = 10
UDP_HEAD_AND_ENCRY_SIZE = 40
MTU_LIMIT = 1300
_SALT_LEN, _ZERO_LEN = 2, 7

def optimize_udp_socket(sock):
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 262144)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
    except Exception: pass

async def crc7_buff(crc, buf):
    c = crc & 0x7F
    for b in buf: c = CRC7_TABLE[((2 * (c & 0xFF)) ^ (b & 0xFF)) & 0xFF] & 0x7F
    return c & 0x7F

async def uleb_encode(n):
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)

async def tea_enc(v0, v1, k0, k1, k2, k3):
    s = 0
    for _ in range(_ROUNDS):
        s = (s + _DELTA) & 0xFFFFFFFF
        v0 = (v0 + (((((v1 << 4) & 0xFFFFFFFF) + k0) & 0xFFFFFFFF ^ ((v1 + s) & 0xFFFFFFFF) ^ (((v1 >> 5) + k1) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        v1 = (v1 + (((((v0 << 4) & 0xFFFFFFFF) + k2) & 0xFFFFFFFF ^ ((v0 + s) & 0xFFFFFFFF) ^ (((v0 >> 5) + k3) & 0xFFFFFFFF)))) & 0xFFFFFFFF
    return v0, v1

async def tea_dec(v0, v1, k0, k1, k2, k3):
    s = (_DELTA * _ROUNDS) & 0xFFFFFFFF
    for _ in range(_ROUNDS):
        v1 = (v1 - (((((v0 << 4) & 0xFFFFFFFF) + k2) & 0xFFFFFFFF ^ ((v0 + s) & 0xFFFFFFFF) ^ (((v0 >> 5) + k3) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        v0 = (v0 - (((((v1 << 4) & 0xFFFFFFFF) + k0) & 0xFFFFFFFF ^ ((v1 + s) & 0xFFFFFFFF) ^ (((v1 >> 5) + k1) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        s = (s - _DELTA) & 0xFFFFFFFF
    return v0, v1

async def tea_cbc_encrypt(padded, key_bytes):
    k0, k1, k2, k3 = (struct.unpack_from("<I", key_bytes, o)[0] for o in (0, 4, 8, 12))
    out = bytearray(len(padded)); prev_cipher = bytearray(8); prev_intermediate = bytearray(8)
    for i in range(0, len(padded), 8):
        xored = bytearray(8)
        for j in range(8): xored[j] = padded[i + j] ^ prev_cipher[j]
        e0, e1 = await tea_enc(struct.unpack_from("<I", xored, 0)[0], struct.unpack_from("<I", xored, 4)[0], k0, k1, k2, k3)
        enc = bytearray(8)
        struct.pack_into("<I", enc, 0, e0); struct.pack_into("<I", enc, 4, e1)
        for j in range(8): out[i + j] = enc[j] ^ prev_intermediate[j]
        prev_cipher[:] = out[i:i + 8]; prev_intermediate[:] = xored
        if i % 64 == 0: await asyncio.sleep(0)
    return bytes(out)

async def tea_cbc_decrypt(body, key_bytes):
    k0, k1, k2, k3 = (struct.unpack_from("<I", key_bytes, o)[0] for o in (0, 4, 8, 12))
    out = bytearray(len(body)); prev_intermediate = bytearray(8); prev_cipher = bytearray(8)
    xored = bytearray(8); dec = bytearray(8)
    for i in range(0, len(body), 8):
        for j in range(8): xored[j] = body[i + j] ^ prev_intermediate[j]
        d0, d1 = await tea_dec(struct.unpack_from("<I", xored, 0)[0], struct.unpack_from("<I", xored, 4)[0], k0, k1, k2, k3)
        struct.pack_into("<I", dec, 0, d0); struct.pack_into("<I", dec, 4, d1)
        for j in range(8): out[i + j] = dec[j] ^ prev_cipher[j]
        prev_cipher[:] = body[i:i + 8]; prev_intermediate[:] = dec
        if i % 64 == 0: await asyncio.sleep(0)
    return bytes(out)

async def build_padded(content):
    pad_len = (8 - (len(content) + 10) % 8) % 8
    return bytes([pad_len, 0, 0]) + b"\x00" * pad_len + content + b"\x00" * 7

async def oicq_unpad(padded):
    if not padded or len(padded) < 8: return None
    if not all(padded[-1 - i] == 0 for i in range(7)): return None
    pad_len = padded[0] & 0x07
    s = 3 + pad_len; e = len(padded) - 7
    return padded[s:e] if s < e else b""

async def encode_header(layout, so, cmd, oid, flags, length, k, v80):
    out = bytearray()
    for code in layout:
        value = {0: so, 1: cmd, 2: oid, 3: flags, 4: length}[code]
        if _FIELD_SIZES[code] == 1: out.append((value & 0xFF) ^ k)
        else:
            v = ((value & 0xFFFF) ^ v80) & 0xFFFF
            out.append(v & 0xFF); out.append((v >> 8) & 0xFF)
    return bytes(out)

async def layouts_from_mask(mask):
    s = str(mask).strip()
    try: ru = [int(c) for c in s]
    except ValueError: ru = [0, 1, 2, 3, 4]
    if sorted(ru) != [0, 1, 2, 3, 4]: ru = [0, 1, 2, 3, 4]
    return ru, [c for c in ru if c != 2]

async def send_start_fire_punch():
    try:
        tick = brain.server_time_now(time.time()) & 0xFFFF
        sb = bytearray()
        _put_varint(sb, int(brain.pid))
        _put_varint(sb, 0)      # WeaponUniqueID = 0 (Punch)
        _put_varint(sb, int(tick))
        _put_varint(sb, 1)      # FireState = 1
        sb += b"\x00" * 4
        await send_reliable(104, bytes(sb))
    except Exception:
        pass
        
async def build_packet(msg_key, layout, so, cmd, oid, flags, content, key, encrypted=True):
    k = key[0]; v80 = ((k << 8) | k) & 0xFFFF
    body = await tea_cbc_encrypt(await build_padded(content), key) if encrypted else content
    hdr = bytearray([msg_key, 0])
    for code in layout:
        value = {0: so, 1: cmd, 2: oid, 3: flags, 4: len(body)}[code]
        if _FIELD_SIZES[code] == 1: hdr.append((value & 0xFF) ^ k)
        else:
            v = ((value & 0xFFFF) ^ v80) & 0xFFFF
            hdr.append(v & 0xFF); hdr.append((v >> 8) & 0xFF)
    packet = bytearray(hdr + body)
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    return bytes(packet)

async def build_hello_packet(text, key, layout):
    data = text.encode("utf-8")[:25]
    content = len(data).to_bytes(4, "little") + data + b"\x00" * 9
    k = key[0]; v80 = ((k << 8) | k) & 0xFFFF
    layout = [int(c) for c in str(layout).strip()]
    enc_body = await tea_cbc_encrypt(await build_padded(content), key)
    header_bytes = await encode_header(layout, 1, 1, 0, 1, len(enc_body), k, v80)
    packet = bytearray([0x63, 0x00]) + header_bytes + enc_body
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    return bytes(packet).hex()

def _put_varint(out, v):
    v = int(v)
    while v >= 0x80:
        out.append((v & 0x7F) | 0x80); v >>= 7
    out.append(v & 0x7F)

def _put_zigvarint(out, v):
    z = (int(v) << 1) ^ (int(v) >> 63)
    _put_varint(out, z & 0xFFFFFFFFFFFFFFFF)

def _put_string(out, s):
    raw = s.encode("utf-8") if isinstance(s, str) else s
    _put_zigvarint(out, len(raw)); out += raw

def _rd_varint(b, p):
    v = i = 0
    while True:
        c = b[p + i]; v |= (c & 0x7F) << (7 * i); i += 1
        if not c & 0x80: return v, p + i

def _zag(v): return (v >> 1) ^ -(v & 1)
def _tea_encrypt_len(n):
    t = 1 + _SALT_LEN + n + _ZERO_LEN
    r = t % 8
    return t + (8 - r if r else 0)

def _dg_size(token_len, reliable=True):
    zv = bytearray()
    _put_zigvarint(zv, token_len)
    body = len(zv) + token_len
    return (HDR_RELIABLE if reliable else 8) + _tea_encrypt_len(body)

def split_token_bytes(token_bytes):
    n = len(token_bytes); raw = int(n * 0.85); p1 = raw - (raw % 40)
    while UDP_HEAD_AND_ENCRY_SIZE + _dg_size(p1) > MTU_LIMIT and p1 > 40: p1 -= 40
    return token_bytes[:p1], token_bytes[p1:]

def build_join_info_head(account_id, game_mode=15, match_mode=1, map_id=1, country="IN", client_version="1.132.16", client_version_code="2019121229", client_url=("csoversea.stronghold.freefiremobile.com;0.0.0.0;34.126.76.45;34.87.177.14;34.87.170.230;35.185.183.57"), room_id=0, match_id=0, drift_bottle_owner_id=0, drift_bottle_owner_name="", enable_antihack_tick=1, friend_count=0, client_ip="", client_fingerprint="", session_tag=0, is_emulator=0):
    room = int(match_id or room_id)
    b = bytearray()
    _put_varint(b, int(account_id)); _put_varint(b, room)
    b.append(1); b.append(int(game_mode) & 0xFF)
    _put_varint(b, room); b.append(int(map_id) & 0xFF); b.append(0)
    _put_varint(b, 0); _put_varint(b, 0); b.append(0); b.append(int(is_emulator) & 0xFF)
    b.append(0); b.append(1); b.append(2); b.append(3); b.append(int(enable_antihack_tick) & 0xFF)
    b.append(1); _put_string(b, country); _put_varint(b, 0); b.append(1); b.append(3)
    b.append(0); b.append(3); b.append(1); b.append(0); b.append(4)
    _put_string(b, client_version); _put_string(b, client_version_code); _put_string(b, client_url)
    b.append(0); b.append(0); _put_varint(b, int(friend_count)); b.append(0); _put_varint(b, 0); _put_string(b, "")
    b.append(1); _put_string(b, ""); _put_string(b, ""); b.append(0)
    _put_varint(b, 0); _put_varint(b, 0); b.append(0); b.append(0); b.append(0)
    _put_varint(b, 0); _put_string(b, ""); _put_varint(b, 0)
    b.append(0); b.append(1); b.append(0); b.append(0)
    _put_varint(b, 0); _put_varint(b, 0); b.append(0); b.append(1)
    _put_string(b, ""); _put_varint(b, 0); b.append(0); b.append(0); b.append(0)
    b.append(int(match_mode) & 0xFF); b.append(0)
    _put_varint(b, int(session_tag)); b.append(2); b.append(0)
    _put_string(b, client_ip or ""); _put_string(b, client_fingerprint or "")
    return bytes(b)

def build_join_post_body(account_id, token_part2, **kw):
    body = bytearray()
    body += build_join_info_head(account_id, **kw)
    _put_string(body, token_part2)
    return bytes(body)

async def build_join_match_startup(join_token, udp_key, match_code, account_id, block_val, server_ip="", region="BD", client_version="1.132.16", client_version_code="2019121229", access_token="", match_id=0, country="IN", map_id=1, game_mode=15, match_mode=1):
    join_token = join_token.strip(); udp_key_b = bytes.fromhex(udp_key); match_code = [int(c) for c in str(match_code).strip()]
    enc_token = join_token.encode("utf-8") if isinstance(join_token, str) else join_token
    part1, part2 = split_token_bytes(enc_token)
    prepare_body = bytearray(); _put_string(prepare_body, part1)
    prepare_pkt = (await build_packet(0x5E, match_code, 2, 447, 0, 1, bytes(prepare_body), udp_key_b)).hex()
    post_body = build_join_post_body(account_id, part2, game_mode=game_mode, match_mode=match_mode, map_id=map_id, country=country, client_version=client_version, client_version_code=client_version_code, match_id=int(match_id or block_val), client_ip="10.0.2.15", client_fingerprint="0", session_tag=0, is_emulator=0)
    post_pkt = await build_packet(0x5A, match_code, 2, 448, 1, 1, post_body, udp_key_b)
    return [prepare_pkt], post_pkt.hex()

async def decode_packet(packet, key, mask=None):
    import itertools
    data = bytes(packet) if isinstance(packet, bytes) else bytes.fromhex(packet)
    if len(data) < 8: return None
    k = key[0]; v80 = ((k << 8) | k) & 0xFFFF
    crc_ok = (data[1] & 0x7F) == await crc7_buff(0, data[2:])
    if mask:
        ru, nr = await layouts_from_mask(mask); layouts = [("RUDP", ru), ("nonRUDP", nr)]
    else:
        layouts = [("RUDP", list(p)) for p in itertools.permutations([0, 1, 2, 3, 4])]
        layouts += [("nonRUDP", list(p)) for p in itertools.permutations([0, 1, 3, 4])]
    cands = []
    for kind, layout in layouts:
        off = 2; f = {}; ok = True
        for code in layout:
            size = _FIELD_SIZES[code]
            if off + size > len(data): ok = False; break
            f[_FIELD_NAMES[code]] = (data[off] ^ k) if size == 1 else ((data[off] | (data[off + 1] << 8)) ^ v80) & 0xFFFF
            off += size
        if not ok: continue
        if f["flags"] > 7 or f["sendOption"] > 7: continue
        if f["length"] != len(data) - off: continue
        body = data[off:off + f["length"]]
        content = None
        if f["flags"] & 1:
            if len(body) < 8 or len(body) % 8 != 0: continue
            content = await oicq_unpad(await tea_cbc_decrypt(body, key))
            if content is None: continue
        else: content = body
        score = (1 if crc_ok else 0) + (1 if content is not None else 0)
        cands.append({"kind": kind, "layout": layout, "headerLen": off, "msgKey": data[0], "cmd": f["cmd"], "flags": f["flags"], "sendOrder": f["sendOption"], "orderId": f.get("orderId"), "length": f["length"], "content": content, "crcOk": crc_ok, "score": score})
    if not cands: return None
    cands.sort(key=lambda c: c["score"], reverse=True)
    return cands[0]

PROTOCOL = {0: "NONE", 1: "INIT", 2: "HEARTBEAT", 3: "MATCHMAKING", 4: "STATS", 5: "GROUP", 6: "FRIEND", 7: "MAIL", 8: "INVENTORY", 9: "BACKPACK", 10: "ACTIVITY", 11: "ACCOUNT", 12: "CLAN", 13: "PROFILE", 14: "ROOM", 15: "PRESENCE", 16: "ELITEPASS", 17: "RECONNECTION", 18: "CHANNEL", 19: "STORE", 21: "PET", 22: "MANUAL", 23: "CHAMPIONSHIP", 24: "ANTIADDICTION", 25: "FRESH", 26: "LINKAGE", 27: "ATTENDANCE", 28: "LIMITEDEVENT", 29: "FFANTI", 30: "CHAT", 31: "CUP", 32: "VIPCARD", 34: "CREDITSCORE", 35: "GAMESERVERMANAGER", 36: "MINIGAME", 37: "WORKSHOP", 38: "CUSTOMEVENT", 39: "ACHIEVEMENT", 40: "GIN", 41: "WEAPONPOWER", 42: "CSRANKINGMATCH", 43: "BRRANKINGMATCH", 44: "OCCUPATION", 45: "MODESTATS", 46: "HIPPOINVENTORY", 47: "PRIME", 48: "TEAMTOPUP", 49: "RELAYMART", 50: "REMATCH", 51: "GOOGLE_PLAY", 52: "LBS", 53: "SHAREDGACHA", 54: "ESPORTS", 55: "SOCIALHALL"}
GROUP_CMD = {0: "NONE", 1: "CREATE", 2: "INVITE", 3: "INVITE_NTF", 4: "ACCEPT", 5: "REFUSE", 6: "JOIN_NTF", 7: "LEAVE", 8: "LEAVE_NTF", 9: "START", 10: "START_NTF", 11: "STOP", 12: "STOP_NTF", 13: "DISMISS_NTF", 14: "GROUPINFO", 15: "READY", 16: "READY_NTF", 17: "CHANGE", 18: "CHANGE_NTF", 19: "JOINROOM", 20: "SPECTATEROOM", 21: "SHOWEMOTE", 22: "SHOWEMOTE_NTF", 33: "JOIN", 34: "JOINREQUEST_NTF", 35: "KICKOUT", 44: "ACCEPTJOIN_NTF", 45: "START_ROOM_MATCHMAKING", 46: "STOP_ROOM_MATCHMAKING", 47: "START_ROOM_MATCHMAKING_NTF", 48: "STOP_ROOM_MATCHMAKING_NTF", 49: "CREATE_ROOM", 55: "MIGRATE_GROUP", 56: "MIGRATE_GROUP_NTF", 57: "TRANSFER_LEADER", 58: "TRANSFER_LEADER_NTF", 102: "GROUP_NOTIFY_102"}
MATCHMAKING_CMD = {0: "NONE", 1: "START", 2: "CANCEL", 3: "GROUPSTART", 4: "GROUPCANCEL", 5: "MATCHMAKINGSUSS_NTF", 6: "DROPMATCH", 7: "GAMEOPENINGINFO", 8: "CHECKINGAMEPLAYER", 9: "CLEARINGAMEPLAYER", 10: "ANTIADDICTION_NTF", 11: "START_NTF", 14: "STOP_NTF", 15: "RANKING_BANNED", 16: "TEAMMATE_RANKING_BANNED", 17: "CDT_HACKER_NTF", 18: "GETMATCHMAKINGINFO", 19: "PUNISHINGAMEPLAYER", 23: "SPECTATE"}
RECONNECTION_CMD = {0: "NONE", 1: "RECONNECT", 2: "TIMEOUT", 3: "MATCHMAKINGSUSS_NTF", 4: "CANCEL", 5: "GROUPINFO", 6: "LEAVEMATCH_NTF"}
STATS_CMD = {0: "NONE", 1: "MATCHSTATS_NTF", 2: "UPDATEMMR_NTF"}
CMD_TABLES = {3: MATCHMAKING_CMD, 4: STATS_CMD, 5: GROUP_CMD, 17: RECONNECTION_CMD}
UDP_CMD = {1: "UDP_HELLO", 2: "UDP_ACK", 3: "UDP_PING", 4: "UDP_BYEBYE", 5: "UDP_LONGTIMENOSEE", 6: "MUDP_CONNECT_ACK", 100: "RUDP_JOIN_MATCH", 101: "RUDP_PLAYER_JOIN", 102: "RUDP_PLAYER_QUIT", 103: "RUDP_MATCH_END", 107: "RUDP_DEAD", 110: "RUDP_BATTLE_START", 116: "RUDP_SYNC_SCENE_INFO", 117: "RUDP_SAFE_ZONE", 130: "RUDP_JOIN_MATCH_FINISHED", 551: "RUDP_QUICK_CHAT", 1901: "RUDP_GRI_SYNC", 2000: "RUDP_SERVER_TIME", 2001: "RUDP_MY_STATE", 2012: "RUDP_OTHER_STATES", 447: "RUDP_JOIN_MATCH_PREPARE", 448: "RUDP_JOIN_MATCH_POST"}
LEAVE_REASONS = {0: "NORMAL", 1: "OFFLINE", 2: "DROPMATCH", 3: "ALLJOINROOM", 4: "SOLOJOINROOM", 5: "KICKOUT", 6: "MERGEGROUP", 7: "TIMEOUT"}

def describe(ptype, cmd):
    p = PROTOCOL.get(ptype, f"UNKNOWN_{ptype}")
    if isinstance(cmd, int): return f"{p}/{CMD_TABLES.get(ptype, {}).get(cmd, f'CMD_{cmd}')}"
    return p

def udp_cmd_name(cmd): return UDP_CMD.get(cmd, f"CMD_{cmd}")

def _rbyte(region):
    reg = str(region or "IND").upper()
    return 0x14 if reg == "IND" else (0x19 if reg == "BD" else 0x15)

def _idc_entries(region):
    reg = str(region or REGION).upper()
    return [{1: "IDC1", 2: 75, 3: reg}, {1: "IDC2", 2: 123, 3: reg}]

def _vi(n):
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        if n: out.append(b | 0x80)
        else:
            out.append(b); break
    return bytes(out)

def _one(field, v):
    if isinstance(v, dict):
        body = _pb(v)
        return _vi((field << 3) | 2) + _vi(len(body)) + body
    if isinstance(v, int): return _vi(field << 3) + _vi(v)
    if isinstance(v, (str, bytes)):
        b = v.encode() if isinstance(v, str) else v
        return _vi((field << 3) | 2) + _vi(len(b)) + b
    raise TypeError(type(v))

def _pb(fields):
    out = bytearray()
    for f, v in fields.items():
        if isinstance(v, list):
            for it in v: out += _one(f, it)
        else: out += _one(f, v)
    return bytes(out)

def _br_rbyte(region):
    r = str(region or "BD").upper()
    return 0x19 if r == "BD" else (0x14 if r == "IND" else 0x15)

def _br_frame(ptype, region, proto, key, iv):
    enc = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(proto, 16))
    return bytes([ptype, _br_rbyte(region)]) + len(enc).to_bytes(4, "big") + enc

def _br_idc(reg, pings=(75, 123)):
    return [{1: "IDC1", 2: pings[0], 3: reg}, {1: "IDC2", 2: pings[1], 3: reg}]

_C_S1 = "0200044B122D3B02010000000000000000000000000000E3172CED00"
_C_14_1 = b"\x32" + bytes([len(_C_S1)]) + _C_S1.encode() + b"\x30\x30" * 3
_C_14_3 = bytes.fromhex("7e585c521207074f5d030c5c545104570455070f0a555a085201095701025b560601545606010f07100802487d5c4043481e071f081a1709034c0757787500566b45627e7a6548407565577a700e7708627a047e7e041005447b5d655070547e437c607f76565675704e5877525b5a5b515662410a105f5c5a4c1e637f1c7147430b4f6c557778605b67416b50635850500056575e005a7606057005067e0c15060045455e56447a665a6672694b5046524b057b79427c715560577b575f0a120e4b470e631b536262186b0f73406359475343795c481d7918564b47790c13054d1d714b5d75451740515f7e586d414e40595a03000e654e0741507a091b084c6668777b1c4c676517505d6e7a4c4e7d7c791f5269057f42440207041005004d7e5c5977037d4a631f560255026b7a647e6b0007015503746353500e1a0048701a0153626506774f18065e0558610457421856007313771b60010b140745554d7f50477d68770662600646696876026242541c4a49037f74750a1204074f487402135059457f517b415266604a434506064e79004c5a7b4f700d14044a58454a5a7c5e5f5b764354425e1267735041537d6041180a6d694305")
_C_14_7 = bytes.fromhex("1d02474b420204030506171d677c716374687d5f557051565753")
_C_14_11 = b"\x03" + ("bbSQ69i8H3F5AdV2KyoVlWj2cgPtsEL3Pi8QcWkc/NJiGxtxXsmeZDDwFPKPbvd56sULGeaD3qha9S6hKIkIb3oXVAAFErlI76uU2p2AqNdJyaucxz1ba5ecHPCBohQR6E5Y1UzpsgpxutURpI8pbqY0tCpeL1bOT+F5UaysgFmTeoIalHxxEYPQx7OVJHElCV5el0vpIs98JSA3nB8FWin6ckz5Fd0sG4n2g0B7OUOvcreqilCT737xI24wPxLdidSr1AJ2MK0/m3ugV1iqzPXhttKyvfmMNVY8DoXBBUcYt3vpK7mgbnietrOqJIbJC3O4ygX6IWl/hkp+ngsjfeOZSornpzFnxM/kkqZgZjVOweXe61FRU6JsGSeTeY63kqA/mbCPfdwodSYJE2hXfVJofxRG1644gFPYRkCPUjJazd2l9WAh9kd86kYbjphbxwz55ciWvZ3sDJR11W96ezyxJPhJPD8FQoQVmno6BP4e7QI1xe+h35bkS1epZq6K6xUP5YtHFvqbhARMNQKUYYzXQWRFMNL1JgAeMJNO0+eCPL57+RXzRKtlgM/rVsIWhNw8Oo9SdP+7wsGrMK+HIOJaF1apAXNRQ9mCqxI=").encode()

def br_create_squad_pkt(region, client_version, key, iv):
    reg = str(region or "IND").upper()
    f = {1: 1, 2: {2: b"\x01", 3: 15, 4: SQUAD_PLAYERS - 1, 5: "en", 8: _br_idc(reg), 9: 6, 10: bytes.fromhex("01090a0b1219202729"), 11: 1, 13: 1, 14: {1: _C_14_1, 2: 40, 3: _C_14_3, 4: "wVV]", 6: 12, 7: _C_14_7, 8: client_version or "1.134.15", 9: 6, 10: 2, 11: _C_14_11}, 19: 324, 20: 42, 21: bytes.fromhex("374f521955"), 24: [{1: 3, 2: 360}, {1: 4, 2: 391}, {1: 5, 2: 156}, {1: 29, 2: 204}, {1: 22, 2: 118}, {1: 14, 2: 139}, {1: 21}]}, 19: 324, 20: 42, 21: bytes.fromhex("374f521955")}
    return _br_frame(0x05, reg, _pb(f), key, iv)

def br_join_team_pkt(code, region, client_version, key, iv):
    reg = str(region or "IND").upper()
    field9 = {1: _C_14_1, 2: 40, 3: _C_14_3, 4: "w\\Z]", 6: 12, 7: _C_14_7, 8: client_version or "1.132.13", 9: 6, 10: 2, 11: _C_14_11}
    f = {1: 4, 2: {4: bytes.fromhex("01090a0b121619201d2729"), 5: str(code), 6: 6, 8: 2, 9: field9, 11: _br_idc(reg, (99, 136)), 13: "en", 16: bytes.fromhex("374f521955"), 20: [{1: 3, 2: 360}, {1: 4, 2: 391}, {1: 5, 2: 156}, {1: 29, 2: 204}, {1: 22, 2: 118}, {1: 14, 2: 139}, {1: 21}], 27: {1: 2, 2: 4}}}
    return _br_frame(0x05, reg, _pb(f), key, iv)

def br_start_squad_pkt(uid, region, key, iv):
    reg = str(region or "IND").upper()
    return _br_frame(0x05, reg, _pb({1: 9, 2: {1: int(uid), 7: _br_idc(reg)}}), key, iv)

async def send_op31(group_id, region, key, iv):
    fields = {1: 31, 2: {1: int(group_id)}}
    pkt = f"05{_rbyte(region):02x}"
    return await GeneRaTePk((await CrEaTe_ProTo(fields)).hex(), pkt, key, iv)

async def GeneRaTePk(Pk, N, K, V):
    PkEnc = await EnC_PacKeT(Pk, K, V)
    _ = await DecodE_HeX(int(len(PkEnc) // 2))
    if len(_) == 2: HeadEr = N + "000000"
    elif len(_) == 3: HeadEr = N + "00000"
    elif len(_) == 4: HeadEr = N + "0000"
    elif len(_) == 5: HeadEr = N + "000"
    else: HeadEr = N + "0000"
    return bytes.fromhex(HeadEr + _ + PkEnc)

async def EnC_PacKeT(HeX, K, V): return AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(HeX), 16)).hex()

async def DecodE_HeX(H):
    R = hex(H); F = str(R)[2:]
    if len(F) == 1:
        F = "0" + F; return F
    else: return F

def _decode_frame_payload(payload):
    if not HAS_PARSER: return None
    try:
        parsed = Parser().parse(payload.hex()); decoded = {}
        for r in parsed:
            wt = r.wire_type
            if wt == "length_delimited":
                try:
                    sub = r.data.results; nested = {}
                    for sr in sub:
                        if sr.wire_type == "length_delimited":
                            try:
                                inner = sr.data.results; nested_inner = {}
                                for ir in inner:
                                    if ir.wire_type == "length_delimited": nested_inner[str(ir.field)] = {"data": "nested"}
                                    else: nested_inner[str(ir.field)] = {"data": ir.data}
                                nested[str(sr.field)] = nested_inner
                            except Exception: nested[str(sr.field)] = {"data": str(sr.data)}
                        else: nested[str(sr.field)] = {"data": sr.data}
                    decoded[str(r.field)] = nested
                except Exception: decoded[str(r.field)] = {"data": str(r.data)}
            else: decoded[str(r.field)] = {"data": r.data}
        return decoded
    except Exception: return None

def _extract_team_code(decoded, master_id):
    if not isinstance(decoded, dict): return None
    candidates = []
    r5 = decoded.get("5")
    if isinstance(r5, dict):
        for k in ("1", "2", "3", "4", "5", "6", "11"):
            v = r5.get(k)
            if isinstance(v, dict): v = v.get("data")
            if isinstance(v, (str, int)): candidates.append(str(v))
    for k in ("1", "2", "3"):
        v = decoded.get(k)
        if isinstance(v, dict): v = v.get("data")
        if isinstance(v, (str, int)): candidates.append(str(v))
    for c in candidates:
        if not c or c == str(master_id): continue
        if c.isdigit() and len(c) >= 12 and c != str(master_id): continue
        return c
    for c in candidates:
        if c and c != str(master_id): return c
    return None

def _match_info_from_frame(ptype, cmd, decoded, payload=None):
    is_matchmaking = (ptype == 0x03 and cmd == 5)
    is_reconnect = (ptype == 0x11 and cmd == 3)
    if not (is_matchmaking or is_reconnect): return None

    def _extract(d):
        if not isinstance(d, dict): return None
        r5 = d.get("5") or d.get(5) or {}
        if not isinstance(r5, dict): return None
        ip_port = r5.get("2") or r5.get(2); udp_key = r5.get("3") or r5.get(3); token = r5.get("4") or r5.get(4); mcode = r5.get("42") or r5.get(42)
        if isinstance(ip_port, dict): ip_port = ip_port.get("data")
        if isinstance(udp_key, dict): udp_key = udp_key.get("data")
        if isinstance(token, dict): token = token.get("data")
        if isinstance(mcode, dict): mcode = mcode.get("data")
        if (isinstance(ip_port, str) and ":" in ip_port and isinstance(udp_key, str) and isinstance(token, str) and mcode is not None):
            r5_clean = dict(r5); r5_clean["2"] = ip_port; r5_clean["3"] = udp_key; r5_clean["4"] = token; r5_clean["42"] = str(mcode)
            return r5_clean
        return None

    result = _extract(decoded)
    if result: return result

    if payload is not None:
        try:
            alt = parse_proto(payload); alt_norm = {}
            for k, vals in alt.items():
                for kind, v in vals:
                    if kind == "bytes":
                        try:
                            nested = parse_proto(bytes.fromhex(v))
                            alt_norm[str(k)] = {str(nk): [{"data": nv} for _, nv in nv_list] for nk, nv_list in nested.items()}
                            break
                        except Exception: pass
                    else: alt_norm.setdefault(str(k), []).append({"data": v})
            return _extract(alt_norm)
        except Exception: pass
    return None

def _pput_varint(out, v):
    v = int(v)
    while v >= 0x80:
        out.append((v & 0x7F) | 0x80); v >>= 7
    out.append(v & 0x7F)

def _pput_zig(out, v):
    z = (int(v) << 1) ^ (int(v) >> 63)
    _pput_varint(out, z & 0xFFFFFFFFFFFFFFFF)

def _pput_float(o, f):
    bits = struct.unpack("<I", struct.pack("<f", f))[0]
    _pput_varint(o, bits)

def _prd_varint(b, p):
    v = i = 0
    while True:
        c = b[p + i]; v |= (c & 0x7F) << (7 * i); i += 1
        if not c & 0x80: return v, p + i

def _pzag(v): return (v >> 1) ^ -(v & 1)

def _decode_other_states(body):
    players = {}
    if body is None or len(body) < 4: return players
    try: count = struct.unpack_from(">H", body, 0)[0]
    except struct.error: return players
    if count == 0 or count > 64: return players
    p = 2
    for _ in range(count):
        if p >= len(body): break
        try:
            sid = body[p]; p += 1
            x, p = _prd_varint(body, p); y, p = _prd_varint(body, p); z, p = _prd_varint(body, p)
            vx, p = _prd_varint(body, p); vy, p = _prd_varint(body, p); vz, p = _prd_varint(body, p)
            yr = body[p]; p += 1; ay = body[p]; p += 1; axz = body[p]; p += 1
            ps = body[p]; p += 1; pp = body[p]; p += 1
            plat, p = _prd_varint(body, p); cus = body[p]; p += 1
        except (IndexError, ValueError): break
        pos = (_pzag(x), _pzag(y), _pzag(z))
        if not (1 <= sid <= 64) or any(abs(v) > 4000000 for v in pos): break
        players[sid] = {"pos": pos, "vel": (_pzag(vx), _pzag(vy), _pzag(vz)), "yrot": yr, "aim_y": ay, "aim_xz": axz, "physx_state": ps, "physx_pose": pp, "platform": plat, "custom": cus}
    return players

def _decode_my_state(body):
    if body is None or len(body) < 4: return None
    try:
        if body[:2] == b"\x00\x02": p = 3
        else:
            p = 0; _pid, p = _prd_varint(body, p)
        x, p = _prd_varint(body, p); y, p = _prd_varint(body, p); z, p = _prd_varint(body, p)
    except (IndexError, ValueError): return None
    return (_pzag(x), _pzag(y), _pzag(z))

def _decode_player_join(body):
    if body is None or len(body) < 4: return None
    try:
        p = 0
        uid, p = _prd_varint(body, p); _s, p = _prd_varint(body, p)
        pid, p = _prd_varint(body, p); rl, p = _prd_varint(body, p)
        n = _pzag(rl); name = body[p:p+n].decode("utf-8", "replace")
    except (IndexError, ValueError): return None
    return uid, pid, name

def _decode_quick_chat(body):
    if body is None or len(body) < 3: return None
    try:
        p = 0
        cid, p = _prd_varint(body, p); _iid, p = _prd_varint(body, p); sender, p = _prd_varint(body, p)
    except (IndexError, ValueError): return None
    return cid, sender & 0xFF, sender

def _decode_server_time(body):
    if body is None or len(body) < 1: return None
    try: tick, _ = _prd_varint(body, 0)
    except (IndexError, ValueError): return None
    return tick

def _build_player_state(pid, pos, rot, tdir, vel, aim, ps=0, pp=0, plat=0, ping=0):
    o = bytearray()
    _pput_varint(o, pid)
    _pput_zig(o, pos[0]); _pput_zig(o, pos[1]); _pput_zig(o, pos[2])
    _pput_zig(o, rot[0]); _pput_zig(o, rot[1]); _pput_zig(o, rot[2])
    _pput_zig(o, tdir[0]); _pput_zig(o, tdir[1])
    _pput_zig(o, vel[0]); _pput_zig(o, vel[1]); _pput_zig(o, vel[2])
    o.append(ps & 0xFF); o.append(pp & 0xFF)
    _pput_float(o, aim[0]); _pput_float(o, aim[1]); _pput_float(o, aim[2])
    _pput_varint(o, plat); o.append(0); _pput_varint(o, ping)
    o.append(0); _pput_varint(o, 0); o.append(0)
    return bytes(o)

def _build_c2s_state(pid, pos, rot, tdir, vel, aim, server_time, ps=0, pp=0, ping=0):
    o = bytearray()
    o += _build_player_state(pid, pos, rot, tdir, vel, aim, ps=ps, pp=pp, ping=ping)
    _pput_varint(o, server_time & 0xFFFFFFFF)
    return bytes(o)

async def _send_position(loop, sock, remote, udp_key_b, nr, pid, old_pos, new_pos, server_time, aim_yaw=0.0, speed=390, ping=90, order_id=0, encrypted=True):
    new_pos = (int(new_pos[0]), int(new_pos[1]), int(new_pos[2]))
    old_pos = (int(old_pos[0]), int(old_pos[1]), int(old_pos[2]))
    dx = new_pos[0] - old_pos[0]
    dz = new_pos[2] - old_pos[2]
    dist = math.sqrt(dx * dx + dz * dz)
    
    if dist >= 1:
        ux, uz = dx / dist, dz / dist
        velocity = (int(ux * speed), 0, int(uz * speed))
        heading = math.degrees(math.atan2(ux, uz))
        heading = ((heading + 180.0) % 360.0) - 180.0
        rot_c = int(heading * 100)
        tdir = (int(ux * 100), int(uz * 100))
        aim = (ux, 0.0, uz)
        pose = 2
    else:
        velocity = (0, 0, 0)
        rad = math.radians(aim_yaw)
        fx, fz = math.sin(rad), math.cos(rad)
        heading = ((aim_yaw + 180.0) % 360.0) - 180.0
        rot_c = int(heading * 100)
        tdir = (int(fx * 100), int(fz * 100))
        aim = (fx, 0.0, fz)
        pose = 2
        
    rotation = (rot_c, 0, 0)
    body = _build_c2s_state(pid, new_pos, rotation, tdir, velocity, aim, server_time, ps=0, pp=pose, ping=ping)
    flags = 1 if encrypted else 0
    pkt = await build_packet(0x6A, nr, 0, CMD_PLAYER_STATE_UPLOAD, order_id, flags, body, udp_key_b, encrypted=encrypted)
    try: await loop.sock_sendto(sock, pkt, remote)
    except Exception: pass

class _BotBrain:
    def __init__(self, pid, squad_ids, squad_count):
        self.pid = pid; self.squad_ids = set(squad_ids); self.squad_count = max(1, squad_count)
        self.slot_index = 0; idx = 0
        for sid in sorted(self.squad_ids):
            if sid == pid:
                self.slot_index = idx; break
            idx += 1
        slot_ang = (2 * math.pi / self.squad_count) * self.slot_index
        er = random.uniform(JHUND_SLOT_MIN, JHUND_SLOT_MAX)
        self.enemy_off = (math.cos(slot_ang) * er, math.sin(slot_ang) * er)
        lead_ang = (2 * math.pi / self.squad_count) * self.slot_index + math.pi
        lr = random.uniform(120.0, 260.0)
        self.leader_off = (math.cos(lead_ang) * lr, math.sin(lead_ang) * lr)
        self.my_pos = None; self.server_time_ms = 0; self.server_kts = 0; self.joined_at = time.time(); self.yaw = 0.0
        self.target_short = None; self.target_pos = None; self.target_vel = (0.0, 0.0); self.target_seen = 0.0
        self.teammates = {}; self.enemies = {}; self.my_short = pid & 0xFF; self.my_team = (pid >> 24) & 0xFF
        self.leader_pos = None; self.identity_set = False
        self.zone_center = None; self.zone_radius = 0.0; self.last_zone_at = 0.0; self.zone_reached_at = 0.0
        self.random_goal = None; self.random_until = 0.0
        self.phase = None; self.round_count = 0; self.last_phase = None
        self.active_skill_id = None; self.join_skills = None; self.preset_skills = None
        self.skill_sent_rounds = set(); self.next_skill_at = 0.0; self.skill_last_sent_at = 0.0
        self.skill_last_id = None; self.skill_pending = False; self.skill_ok = False; self.fight_start_at = 0.0
        self.next_emote_at = 0.0
        self.my_bombs = set(); self.drone_pending = None
        self.last_srv_pos = None

    def set_identity(self, full_id):
        self.my_short = full_id & 0xFF; self.my_team = (full_id >> 24) & 0xFF; self.pid = int(full_id); self.identity_set = True

    def is_teammate(self, short_id, roster):
        if short_id == self.my_short: return False
        ent = roster.get(short_id)
        if not ent: return False
        return ((ent[0] >> 24) & 0xFF) == self.my_team

    def update_positions(self, players, roster):
        self.teammates.clear(); self.enemies.clear()
        for sid, info in players.items():
            if sid == self.my_short: continue
            pos = info.get("pos")
            if not pos: continue
            if self.is_teammate(sid, roster): self.teammates[sid] = pos
            else:
                if info.get("physx_pose") != 8: self.enemies[sid] = pos
        if self.teammates:
            sx = sz = sy = 0.0; n = 0
            for p in self.teammates.values(): sx += p[0]; sy += p[1]; sz += p[2]; n += 1
            if self.my_pos is not None: sx += self.my_pos[0]; sy += self.my_pos[1]; sz += self.my_pos[2]; n += 1
            if n > 0: self.leader_pos = (int(sx / n), int(sy / n), int(sz / n))
            else: self.leader_pos = None
        else: self.leader_pos = None

    def set_target(self, short_id):
        if short_id == self.my_short: return
        if short_id != self.target_short: self.target_pos = None; self.target_seen = 0.0; self.target_vel = (0.0, 0.0)
        self.target_short = short_id

    def clear_target(self):
        self.target_short = None; self.target_pos = None; self.target_seen = 0.0; self.target_vel = (0.0, 0.0)

    def update_target_pos(self, info, now):
        prev = self.target_pos; prev_seen = self.target_seen
        self.target_pos = info["pos"]; self.target_seen = now
        if prev is not None and prev_seen > 0:
            dt = now - prev_seen
            if 0.01 < dt < 2.0:
                vx = (info["pos"][0] - prev[0]) / dt; vz = (info["pos"][2] - prev[2]) / dt
                if abs(vx) < 30000 and abs(vz) < 30000: self.target_vel = (vx, vz)

    def nearest_enemy(self):
        if self.my_pos is None or not self.enemies: return None
        my = self.my_pos; best_sid = None; best_d = 1e18
        for sid, pos in self.enemies.items():
            dx = pos[0] - my[0]; dz = pos[2] - my[2]; d = dx * dx + dz * dz
            if d < best_d: best_d = d; best_sid = sid
        return best_sid

    def pick_nearest_enemy_full(self, max_dist=None):
        if max_dist is None: max_dist = 60000.0
        if self.my_pos is None or not self.enemies: return None
        mx, _, mz = self.my_pos; best = None; best_d = None
        for sid, pos in self.enemies.items():
            if pos is None: continue
            dx = pos[0] - mx; dz = pos[2] - mz; d = math.sqrt(dx * dx + dz * dz)
            if d > max_dist: continue
            if best_d is None or d < best_d: best = (sid, pos, d); best_d = d
        return best

    def set_zone(self, center_2d, radius_world):
        if not center_2d or radius_world <= 0: return
        self.zone_center = (int(center_2d[0]), 0, int(center_2d[1])); self.zone_radius = float(radius_world); self.last_zone_at = time.time()

    def set_phase(self, phase, round_no=None):
        prev = self.phase; self.phase = phase
        if round_no is not None: self.round_count = int(round_no)
        elif phase == PHASE_PREPARE and prev != PHASE_PREPARE: self.round_count += 1
        if phase == PHASE_PREPARE and prev != PHASE_PREPARE:
            self.next_emote_at = 0.0; self.enemies.clear(); self.target_short = None
            self.target_pos = None; self.target_seen = 0.0; self.target_vel = (0.0, 0.0)
            self.drone_pending = None; self.zone_reached_at = 0.0
        if phase == PHASE_FIGHT and prev != PHASE_FIGHT:
            self.fight_start_at = time.time(); self.next_skill_at = time.time() + SKILL_AFTER_FIGHT_SEC
        self.last_phase = prev

    def server_time_now(self, now):
        return int((now - self.joined_at) * 1000.0) & 0xFFFFFFFF

    def plan(self, now):
        if self.my_pos is None: return None
        if self.phase is not None and self.phase != PHASE_FIGHT:
            return (self.my_pos[0], self.my_pos[1], self.my_pos[2]), 0.0, False
        my = self.my_pos
        if self.zone_center is not None:
            tx, _ty, tz = self.zone_center
            dx = tx - my[0]; dz = tz - my[2]; dist = math.sqrt(dx * dx + dz * dz)
            if dist < 200:
                if self.zone_reached_at == 0.0: self.zone_reached_at = now
                return (my[0], my[1], my[2]), dist, False
            self.zone_reached_at = 0.0
            step = PUNCH_STEP
            move = step if dist > step else dist
            nx = int(my[0] + dx / dist * move); nz = int(my[2] + dz / dist * move)
            self.yaw = math.degrees(math.atan2(dx, dz))
            return (nx, my[1], nz), dist, True
        if self.leader_pos is not None:
            cx, cy, cz = self.leader_pos; lox, loz = self.leader_off
            tx = cx + lox; tz = cz + loz
            dx = tx - my[0]; dz = tz - my[2]; dist = math.sqrt(dx * dx + dz * dz)
            if dist > LEADER_DEADZONE:
                step = min(PUNCH_STEP, dist)
                nx = int(my[0] + dx / dist * step); nz = int(my[2] + dz / dist * step)
                self.yaw = math.degrees(math.atan2(dx, dz))
                return (nx, my[1], nz), dist, True
            return (my[0], my[1], my[2]), dist, False
        return (my[0], my[1], my[2]), 0.0, False

async def slave_loop(acct, holder, match_infos, stop_evt):
    tag = acct["tag"]; region = acct.get("region", REGION); ip, port = acct["game_server"].split(":")
    key, iv = acct["key"], acct["iv"]; jwt = acct["jwt"]; ingame_id = int(acct["ingame_id"]); ts = acct["ts"]
    auth_online = await build_auth_packet(ingame_id, jwt, ts, key, iv, region, "OnLine")
    ka_bytes = await send_keep_alive(region); remote_version = acct["cfg"].get("remote_version", _PLAY_VERSION)
    while not stop_evt.is_set():
        writer = None; ka_task = None; ka_stop = asyncio.Event()
        try:
            reader, writer = await asyncio.open_connection(ip, int(port)); acct["writer"] = writer
            writer.write(auth_online); await writer.drain(); writer.write(ka_bytes); await writer.drain()
            _log(f"Tcp Connected => {acct.get('name', tag)}")
            async def ka_loop():
                while not ka_stop.is_set():
                    try:
                        await asyncio.sleep(15)
                        if writer.is_closing(): return
                        writer.write(ka_bytes); await writer.drain()
                    except Exception: return
            ka_task = asyncio.create_task(ka_loop())
            try: await asyncio.wait_for(holder["team_code_ready"].wait(), 30)
            except asyncio.TimeoutError:
                _log(f"{tag} timeout waiting for team code (30s)"); continue
            team_code = holder["team_code"]
            if not team_code: await asyncio.sleep(1.0); continue
            j = br_join_team_pkt(team_code, region, remote_version, key, iv)
            writer.write(j); await writer.drain(); _log(f"{tag} JOIN via team code sent code={team_code!r}")
            joined = False; join_sent_at = time.time(); buf = bytearray(); warned_at = 0.0; WARN_AFTER = 10.0
            while not stop_evt.is_set():
                try: chunk = await asyncio.wait_for(reader.read(65536), timeout=1.0)
                except asyncio.TimeoutError:
                    if (not joined and warned_at == 0.0 and time.time() - join_sent_at > WARN_AFTER):
                        warned_at = time.time(); _log(f"{tag} still not in group after {WARN_AFTER:.0f}s (team_code={team_code!r}, roster={sorted(holder['slave_joined'])})")
                    continue
                except Exception as e:
                    _log(f"{tag} read err: {e}"); break
                if not chunk: break
                buf.extend(chunk)
                while len(buf) >= 5:
                    ptype = buf[0]; plen = int.from_bytes(buf[1:5], "big")
                    if plen > 100_000 or len(buf) < 5 + plen: break
                    payload = bytes(buf[5:5 + plen]); del buf[:5 + plen]
                    decoded = _decode_frame_payload(payload); cmd = None
                    if isinstance(decoded, dict):
                        v = decoded.get("4")
                        if isinstance(v, dict): v = v.get("data")
                        if isinstance(v, int): cmd = v
                    _dump_frame_response(tag, ptype, cmd, decoded, payload)
                    if ptype == 0x05 and isinstance(decoded, dict):
                        if cmd == 6:
                            found = set(); collect_all_ints(decoded, found)
                            if ingame_id in found and not joined:
                                joined = True; holder["slave_joined"].add(ingame_id)
                                _log(f"  Bot Joined The Team => {acct.get('name', tag)} (JOIN_NTF id={ingame_id})")
                            elif not joined: _log(f"{tag} JOIN_NTF ints={sorted(found)} (not us yet)")
                        elif cmd == 10:
                            _log(f"{tag} START_NTF received")
                            if not joined:
                                joined = True; holder["slave_joined"].add(ingame_id)
                                _log(f"  Bot Joined The Team => {acct.get('name', tag)} (via START_NTF)")
                        elif cmd == 13:
                            _log(f"{tag} DISMISS_NTF — group destroyed"); stop_evt.set(); break
                        elif cmd == 8:
                            lid, rn = _extract_leave_info(decoded); who = f"id={lid}"
                            if lid == ingame_id: who += " (me)"
                            _log(f"{tag} LEAVE_NTF leaver={who} reason={rn}")
                            if lid == ingame_id: stop_evt.set(); break
                    if ptype == 0x05 and plen >= 200 and not joined:
                        joined = True; holder["slave_joined"].add(ingame_id)
                        _log(f"  Bot Joined The Team => {acct.get('name', tag)} (large frame plen={plen})")
                    minfo = _match_info_from_frame(ptype, cmd, decoded, payload)
                    if minfo is not None and tag not in match_infos:
                        match_infos[tag] = minfo; _log(f"{tag} MATCH info ({describe(ptype, cmd)}) server={minfo['2']}")
                        joined = True; holder["slave_joined"].add(ingame_id)
        except asyncio.CancelledError: raise
        except Exception as e:
            _log(f"{tag} conn err: {e}"); await asyncio.sleep(2.0)
        finally:
            ka_stop.set()
            if ka_task: ka_task.cancel(); await asyncio.gather(ka_task, return_exceptions=True)
            if writer is not None:
                try:
                    if not writer.is_closing(): writer.close(); await writer.wait_closed()
                except Exception: pass
            acct["writer"] = None
        if stop_evt.is_set(): break

async def master_loop(acct, slave_ids, holder, match_infos):
    tag = acct["tag"]; region = acct.get("region", REGION); ip, port = acct["game_server"].split(":")
    key, iv = acct["key"], acct["iv"]; jwt = acct["jwt"]; ingame_id = int(acct["ingame_id"]); ts = acct["ts"]
    slave_set = {int(x) for x in slave_ids}; remote_version = acct["cfg"].get("remote_version", _PLAY_VERSION)
    auth_online = await build_auth_packet(ingame_id, jwt, ts, key, iv, region, "OnLine"); ka_bytes = await send_keep_alive(region)
    writer = None; ka_task = None; ka_stop = asyncio.Event()
    try:
        reader, writer = await asyncio.open_connection(ip, int(port)); acct["writer"] = writer
        writer.write(auth_online); await writer.drain(); writer.write(ka_bytes); await writer.drain()
        _log(f"Tcp Connected => {acct.get('name', tag)}")
        async def ka_loop():
            while not ka_stop.is_set():
                try:
                    await asyncio.sleep(15)
                    if writer.is_closing(): return
                    writer.write(ka_bytes); await writer.drain()
                except Exception: return
        ka_task = asyncio.create_task(ka_loop()); await asyncio.sleep(1.0)
        c = br_create_squad_pkt(region, remote_version, key, iv)
        writer.write(c); await writer.drain(); _log(f"{tag} CREATE SQUAD sent ({len(c)}B)")
        created = False; op31_sent = False; buf = bytearray(); last_start = 0.0; started = False
        while True:
            try: chunk = await asyncio.wait_for(reader.read(65536), timeout=1.0)
            except asyncio.TimeoutError: chunk = None
            except Exception as e:
                _log(f"{tag} read err: {e}"); break
            if chunk:
                if not chunk: break
                buf.extend(chunk)
                while len(buf) >= 5:
                    ptype = buf[0]; plen = int.from_bytes(buf[1:5], "big")
                    if plen > 100_000 or len(buf) < 5 + plen: break
                    payload = bytes(buf[5:5 + plen]); del buf[:5 + plen]
                    decoded = _decode_frame_payload(payload); cmd = None
                    if isinstance(decoded, dict):
                        v = decoded.get("4")
                        if isinstance(v, dict): v = v.get("data")
                        if isinstance(v, int): cmd = v
                    _log(f"{tag}  ↳ {describe(ptype, cmd)}  len={len(payload)}")
                    if ptype == 0x05 and isinstance(decoded, dict):
                        data = decoded.get("5", {})
                        if cmd == 1 and not created and plen >= 100:
                            gid = None
                            if isinstance(data, dict):
                                g = data.get("1")
                                if isinstance(g, dict): g = g.get("data")
                                if isinstance(g, int): gid = g
                            if gid is None: gid = ingame_id
                            created = True; holder["group_id"] = gid; holder["master_id"] = int(ingame_id)
                            _log(f"{tag} CREATE_NTF group_id={gid}")
                        elif cmd == 32 and not holder["team_code"]:
                            tc_val = _extract_team_code(decoded, ingame_id)
                            if tc_val:
                                holder["team_code"] = tc_val; holder["team_code_ready"].set()
                                _log(f"{tag} GETGROUPCODE_NTF team_code={tc_val!r}")
                        elif cmd == 6:
                            found = set()
                            if isinstance(decoded, dict):
                                for v in decoded.values():
                                    if isinstance(v, dict) and isinstance(v.get("data"), int): found.add(v["data"])
                            newj = found & slave_set
                            if newj:
                                for sid in newj: holder["slave_joined"].add(sid)
                                _log(f"{tag} JOIN_NTF seen={sorted(newj)} total={len(holder['slave_joined'])}/{len(slave_set)}")
                        elif cmd == 8:
                            lid = None; rn = "UNKNOWN"; dd = decoded.get("5", {}) if isinstance(decoded, dict) else {}
                            if isinstance(dd, dict):
                                l = dd.get("1"); l = l.get("data") if isinstance(l, dict) else l
                                r = dd.get("2"); r = r.get("data") if isinstance(r, dict) else r
                                lid = l; rn = LEAVE_REASONS.get(r, f"UNKNOWN_{r}") if isinstance(r, int) else "UNKNOWN"
                            _log(f"{tag} LEAVE_NTF  leaver=id={lid}  reason={rn}")
                            if isinstance(lid, int) and lid in slave_set: holder["slave_joined"].discard(lid)
                        elif cmd == 10:
                            _log(f"{tag} START_NTF  ← START accepted by server"); started = True
                        elif cmd == 13:
                            _log(f"{tag} DISMISS_NTF — group destroyed")
                        if created and not op31_sent and holder["group_id"]:
                            op31_sent = True
                            try:
                                p31 = await send_op31(holder["group_id"], region, key, iv)
                                writer.write(p31); await writer.drain(); _log(f"{tag} op31 sent ({len(p31)}B)")
                            except Exception as e: _log(f"{tag} op31 err: {e}")
                    minfo = _match_info_from_frame(ptype, cmd, decoded, payload)
                    if minfo is not None and tag not in match_infos:
                        match_infos[tag] = minfo; _log(f"{tag} MATCH info server={minfo['2']}")
            all_in = holder["slave_joined"] >= slave_set
            if (created and all_in and holder["team_code"] and tag not in match_infos and (time.time() - last_start) > START_REPEAT_INTERVAL):
                try:
                    s = br_start_squad_pkt(ingame_id, region, key, iv)
                    writer.write(s); await writer.drain(); last_start = time.time()
                    _log(f"{tag} START sent ({len(s)}B) slaves={sorted(holder['slave_joined'])}")
                except Exception as e: _log(f"{tag} START WRITE ERR: {e!r}")
            elif not created:
                if int(time.time()) % 5 == 0: _log(f"{tag} waiting: created={created} slaves={len(holder['slave_joined'])}/{len(slave_set)}")
    finally:
        ka_stop.set()
        if ka_task: ka_task.cancel(); await asyncio.gather(ka_task, return_exceptions=True)
        if writer is not None:
            try:
                if not writer.is_closing(): writer.close(); await writer.wait_closed()
            except Exception: pass
        acct["writer"] = None

async def play_game_idle(server_ip_port, prepare_packets, post_packet, udp_key, match_code, account_id, player_region, client_version, tag="[?]", account_jwt="", sleep_ms=0, squad_done=None, name="", squad_ids=None, server_kts=0):
    match_start = time.time()
    ping_task = hello_task = move_task = sock = None
    ping_stop = asyncio.Event()
    brain = _BotBrain(int(account_id), squad_ids or [int(account_id)], len(squad_ids or [int(account_id)]))
    roster = {}
    probe = {"mode": None}

    try:
        ip, port = server_ip_port.split(":"); port = int(port); resolved_ip = socket.gethostbyname(ip)
        loop = asyncio.get_event_loop(); sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        optimize_udp_socket(sock); sock.setblocking(False)
        udp_key_b = bytes.fromhex(udp_key); remote = (resolved_ip, port)
        gap = sleep_ms / 1000.0 if sleep_ms else 0.02

        if account_jwt:
            auth_pkt = await build_auth_datagram(account_jwt, account_id)
            await loop.sock_sendto(sock, auth_pkt, remote)

        hello_hex = await build_hello_packet(f"{account_id}_2585", udp_key_b, match_code)
        hello_bytes = bytes.fromhex(hello_hex)
        await loop.sock_sendto(sock, hello_bytes, remote)

        ack_state = "waiting_for_hello_reply"; startup_sent = False; local_closed = False
        send_lock = asyncio.Lock(); ru, nr = await layouts_from_mask(match_code)
        ack_state_dict = {"last_ack_t": time.time()}; rel_oid = [1]

        async def send_reliable(cmd, content):
            oid = rel_oid[0]; rel_oid[0] = (oid + 1) & 0xFFFF
            mk = random.randint(MSG_KEY_RELIABLE_MIN, MSG_KEY_RELIABLE_MAX)
            pkt = await build_packet(mk, ru, 2, cmd, oid, 1, content, udp_key_b)
            await loop.sock_sendto(sock, pkt, remote)
            return pkt

        async def send_emote(why=""):
            try:
                tick = brain.server_time_now(time.time())
                body = build_emote_body(emotion_id=EMOTE_ID, nickname="", server_tick=tick, create_time=int(time.time()) & 0xFFFFFFFF)
                await send_reliable(CMD_EMOTE, body); _log(f"{tag} → 371 emote tick={tick} {why}")
            except Exception as e: _log(f"{tag} emote err: {e}")

        async def send_skill(enemy_pos, enemy_short, enemy_dist):
            try:
                skill_id = brain.active_skill_id or ACTIVE_SKILL_ID; sb = bytearray()
                _put_varint(sb, int(brain.pid)); _put_varint(sb, int(skill_id))
                for v in enemy_pos: _put_zigvarint(sb, int(v))
                dx = enemy_pos[0] - (brain.my_pos[0] if brain.my_pos else 0); dz = enemy_pos[2] - (brain.my_pos[2] if brain.my_pos else 0)
                if dx or dz: brain.yaw = math.degrees(math.atan2(dz, dx)) % 360.0
                rad = math.radians(brain.yaw); fx, fz = math.cos(rad), math.sin(rad)
                for v in (int(fx * 100), 0, int(fz * 100)): _put_zigvarint(sb, v)
                _put_varint(sb, 0); await send_reliable(CMD_USE_ACTIVE_SKILL, bytes(sb))
                brain.skill_last_sent_at = time.time(); brain.skill_last_id = skill_id; brain.skill_pending = True
                brain.skill_ok = False; brain.skill_sent_rounds.add(brain.round_count)
                _log(f"{tag} → 248 skill round={brain.round_count} id={skill_id} enemy=short{enemy_short} dist={int(enemy_dist)}")
            except Exception as e: _log(f"{tag} skill err: {e}")

        async def send_drone_push(bomb_id, enemy_full_id):
            try:
                if brain.my_pos is None: return
                pb = bytearray(); _put_varint(pb, int(bomb_id)); _put_varint(pb, int(enemy_full_id))
                for v in (int(brain.my_pos[0]), int(brain.my_pos[1]), int(brain.my_pos[2])): _put_zigvarint(pb, v)
                await send_reliable(CMD_PUSH_AUTOFLIGHT_ENEMY, bytes(pb))
                brain.my_bombs.discard(bomb_id); brain.drone_pending = None
                _log(f"{tag} → 543 drone bomb={bomb_id} enemy=0x{enemy_full_id:08X}")
            except Exception as e: _log(f"{tag} drone push err: {e}")

        async def ka_loop():
            pklist = [0x66, 0x6D, 0x69, 0x6C, 0x6B, 0x6E, 0x6F, 0x70]; i = 0
            while not ping_stop.is_set():
                if ack_state != "waiting_for_hello_reply": break
                try: await asyncio.wait_for(ping_stop.wait(), timeout=0.1)
                except asyncio.TimeoutError: pass
            while not ping_stop.is_set():
                pk = pklist[i % len(pklist)]; cnt = int(time.time() * 1000) & 0xFFFFFFFF
                pkt = await build_packet(pk, nr, 0, 3, None, 0, cnt.to_bytes(4, "little") + b"\x00\x00\x00", udp_key_b, encrypted=False)
                try: await loop.sock_sendto(sock, pkt, remote)
                except Exception: pass
                i += 1
                try: await asyncio.wait_for(ping_stop.wait(), timeout=3.0)
                except asyncio.TimeoutError: pass

        async def hello_retry_loop():
            for _ in range(8):
                if ping_stop.is_set() or ack_state != "waiting_for_hello_reply": return
                try: await asyncio.wait_for(ping_stop.wait(), timeout=0.8)
                except asyncio.TimeoutError: pass
                if ping_stop.is_set() or ack_state != "waiting_for_hello_reply": return
                try: await loop.sock_sendto(sock, hello_bytes, remote)
                except Exception: pass

        async def move_loop():
            start_t = time.time(); next_tick = time.time(); ticks = 0; order_id = 0; probe_done = False
            cur_hz = MOVE_HZ; forced_plain = False
            while not ping_stop.is_set():
                try:
                    now = time.time()
            
                    # Set my_pos immediately so we don't stand still
                    if brain.my_pos is None:
                        brain.my_pos = (100000, 0, 100000)

                    if brain.last_srv_pos is not None:
                        if brain.my_pos is None: brain.my_pos = brain.last_srv_pos
                        else:
                            dx = brain.last_srv_pos[0] - brain.my_pos[0]; dz = brain.last_srv_pos[2] - brain.my_pos[2]
                            drift = math.sqrt(dx * dx + dz * dz)
                            if drift > 50000: brain.my_pos = brain.last_srv_pos
                    
                    if brain.phase == PHASE_PREPARE and now >= brain.next_emote_at:
                        brain.next_emote_at = now + EMOTE_EVERY; await send_emote("prep")
                
                    if (brain.phase == PHASE_FIGHT and brain.round_count not in brain.skill_sent_rounds and now >= brain.next_skill_at and brain.active_skill_id):
                        enemy = brain.pick_nearest_enemy_full(SKILL_MAX_DIST)
                        if enemy:
                            sid, epos, edist = enemy
                            await send_skill(epos, sid, edist); brain.next_skill_at = now + SKILL_EVERY
                        else: brain.next_skill_at = now + 1.0
                
                    if brain.drone_pending is not None and brain.my_pos is not None:
                        bid, bx, by, bz, stamp = brain.drone_pending
                        if now - stamp > 2.0: brain.drone_pending = None
                        else:
                            best = None
                            for sid, pos in brain.enemies.items():
                                fid = roster.get(sid, (0, ""))[0]
                                if not fid: continue
                                d = math.hypot(pos[0] - bx, pos[2] - bz)
                                if best is None or d < best[0]: best = (d, fid)
                            if best and best[0] <= DRONE_TARGET_MAX: await send_drone_push(bid, best[1])
                    
                    if time.time() - ack_state_dict["last_ack_t"] > 4.0:
                        order_id = 0; ack_state_dict["last_ack_t"] = time.time()
                
                    interval = 1.0 / cur_hz
                    if now < next_tick:
                        await asyncio.sleep(min(0.02, next_tick - now)); continue
                    next_tick += interval
                    if next_tick < now: next_tick = now + interval

                    planned = brain.plan(now)
                    if planned is None: continue
                    new_pos, _dist, moving = planned
                    old_pos = brain.my_pos or new_pos; brain.my_pos = new_pos
                    speed = PUNCH_VEL if moving else 0
            
                    if not probe_done:
                        probe_done = True
                        await _send_position(loop, sock, remote, udp_key_b, nr, brain.pid, old_pos, new_pos, brain.server_time_now(now), aim_yaw=brain.yaw, speed=speed, ping=90, order_id=order_id, encrypted=True)
                        order_id = (order_id + 1) & 0xFFFF
                        await asyncio.sleep(0.15)
                        await _send_position(loop, sock, remote, udp_key_b, nr, brain.pid, old_pos, new_pos, brain.server_time_now(now), aim_yaw=brain.yaw, speed=speed, ping=90, order_id=order_id, encrypted=False)
                        order_id = (order_id + 1) & 0xFFFF
                        continue
                
                    enc_flag = (probe["mode"] != "plain")
                    await _send_position(loop, sock, remote, udp_key_b, nr, brain.pid, old_pos, new_pos, brain.server_time_now(now), aim_yaw=brain.yaw, speed=speed, ping=90, order_id=order_id, encrypted=enc_flag)
                    order_id = (order_id + 1) & 0xFFFF
            
                    # Send the punch packet (104) right after position sync
                    await send_start_fire_punch()
            
                    ticks += 1
                    if ticks % 25 == 0:
                        _log(f"{tag} [MOVE] pos={brain.my_pos}")
                except Exception as e:
                    await asyncio.sleep(0.5)

        ping_task = asyncio.create_task(ka_loop())
        hello_task = asyncio.create_task(hello_retry_loop())
        move_task = asyncio.create_task(move_loop())
        last_activity = time.time()

        async def send_join_match():
            nonlocal ack_state, startup_sent
            if startup_sent: return
            async with send_lock:
                if startup_sent: return
                for p in prepare_packets:
                    await loop.sock_sendto(sock, bytes.fromhex(p), remote)
                    await asyncio.sleep(gap)
                await asyncio.sleep(gap)
                await loop.sock_sendto(sock, bytes.fromhex(post_packet), remote)
                startup_sent = True; ack_state = "startup_sent"; _log(f"{tag} Match Prepared")

        while not local_closed:
            if time.time() - match_start > 700: break
            try:
                resp, sa = await asyncio.wait_for(loop.sock_recvfrom(sock, 65535), timeout=1.5)
                if resp:
                    last_activity = time.time()
                    frame = await decode_packet(resp, udp_key_b, match_code)
                    if frame:
                        cmd = frame.get('cmd'); oid = frame.get('orderId'); msg_key = frame.get('msgKey', 0); content = frame.get('content')
                        if cmd == 4: local_closed = True
                        if cmd == 2: ack_state_dict["last_ack_t"] = time.time()
                        if msg_key < 100 and oid is not None:
                            da = await build_packet(0x68, nr, 0, 2, None, 1, ((oid + 1) & 0xFFFF).to_bytes(2, "little"), udp_key_b)
                            await loop.sock_sendto(sock, da, sa)
                        if cmd == 1:
                            if ack_state == "waiting_for_hello_reply": ack_state = "ready_to_send_startup"
                        elif cmd == 3:
                            c = content or b""; cnt = c[:4] if len(c) >= 4 else c
                            rp = await build_packet(0x6D, nr, 0, 3, None, 0, cnt + b"\x00\x00\x00", udp_key_b, encrypted=False)
                            await loop.sock_sendto(sock, rp, sa)
                        elif cmd == 101:
                            info = _decode_player_join(content)
                            if info:
                                uid, full_id, pname = info
                                roster[full_id & 0xFF] = (full_id, pname)
                                if uid == int(account_id):
                                    brain.set_identity(full_id); sk = parse_join_skills(content or b""); brain.join_skills = sk
                                    if sk:
                                        act = [k for k in KNOWN_ACTIVE_SKILLS if k in sk]
                                        brain.active_skill_id = act[0] if act else sk[0]
                                    if brain.active_skill_id is None: brain.active_skill_id = HOMER_SKILL_ID
                                    _log(f"{tag} Bot Joined => {pname} (player_id=0x{full_id:08X} skills={brain.join_skills} active={brain.active_skill_id})")
                                else:
                                    _log(f"{tag} Player Join => {pname}")
                        elif cmd == 2001:
                            mp = _decode_my_state(content)
                            if mp is not None:
                                brain.last_srv_pos = mp
                                if brain.my_pos is None: brain.my_pos = mp
                                if probe["mode"] is None: probe["mode"] = "enc"
                        elif cmd == 2012:
                            players = _decode_other_states(content)
                            if players:
                                brain.update_positions(players, roster)
                                if brain.target_short is None:
                                    auto = brain.nearest_enemy()
                                    if auto is not None: brain.set_target(auto)
                                if brain.target_short is not None:
                                    if brain.target_short in players: brain.update_target_pos(players[brain.target_short], time.time())
                                    else: brain.clear_target()
                        elif cmd == 551:
                            qc = _decode_quick_chat(content)
                            if qc:
                                cid, sid, _raw = qc
                                if cid in CHAT_FOLLOW_TRIGGERS: brain.set_target(sid)
                        elif cmd == 117:
                            z = decode_safezone(content or b"")
                            if z:
                                ctr = z.get("inner_center") or z.get("outer_center"); r = z.get("inner_radius") or z.get("outer_radius") or 0
                                if ctr and r > 0:
                                    brain.zone_center = (ctr[0], 0, ctr[1]); brain.zone_radius = float(r) * 1000.0; brain.last_zone_at = time.time()
                                    _log(f"{tag} [ZONE] stage={z.get('stage')} center=({ctr[0]},{ctr[1]}) r={r}")
                        elif cmd == CMD_GRI_SYNC_PHASE:
                            parsed = _get_match_phase(content or b"")
                            if parsed:
                                ph, rno, _s, _e = parsed
                                if ph != brain.phase: _log(f"{tag} phase {brain.phase} → {ph} round={rno}")
                                brain.set_phase(ph, rno)
                        elif cmd == CMD_SYNC_ACTIVE_SKILL_STATE:
                            if brain.skill_pending and brain.skill_last_id:
                                if time.time() - brain.skill_last_sent_at < 5.0:
                                    brain.skill_ok = True; brain.skill_pending = False
                                    _log(f"{tag} ★ skill accepted id={brain.skill_last_id}")
                        elif cmd == CMD_USE_ACTIVE_SKILL_FAIL:
                            brain.skill_pending = False; _log(f"{tag} ✘ skill REJECTED id={brain.skill_last_id}"); brain.skill_sent_rounds.discard(brain.round_count)
                        elif cmd == CMD_AUTOFLIGHTBOMB_CREATE:
                            try:
                                p = 0; bid, p = _rd_varint(content, p); owner, p = _rd_varint(content, p)
                                if brain.pid and owner == brain.pid:
                                    brain.my_bombs.add(bid); _log(f"{tag} ★ drone created bomb={bid}")
                                    if brain.skill_pending: brain.skill_ok = True; brain.skill_pending = False
                            except (IndexError, ValueError): pass
                        elif cmd == CMD_AUTOFLIGHTBOMB_PUSHSTATE:
                            try:
                                p = 0; bid, p = _rd_varint(content, p); st, p = _rd_varint(content, p)
                                bx, p = _rd_varint(content, p); by, p = _rd_varint(content, p); bz, p = _rd_varint(content, p)
                                if bid in brain.my_bombs and st == 2:
                                    brain.drone_pending = (bid, _zag(bx), _zag(by), _zag(bz), time.time()); _log(f"{tag} drone {bid} armed -> 543")
                            except (IndexError, ValueError): pass
                        elif cmd == CMD_SYNC_PRESET_INFO:
                            pairs = parse_preset_skills(content or b"")
                            if pairs:
                                brain.preset_skills = pairs; ids = [sid for sid, _slot in sorted(pairs, key=lambda x: x[1])]
                                act = [k for k in KNOWN_ACTIVE_SKILLS if k in ids]
                                if act: brain.active_skill_id = act[0]
                        elif cmd == 130: _log(f"{tag} Bot In Match")
                        elif cmd == 103: local_closed = True
            except asyncio.TimeoutError: pass
            except Exception: await asyncio.sleep(0.5)
            if ack_state == "ready_to_send_startup" and not startup_sent: await send_join_match()
            elif ack_state == "startup_sent" and (time.time() - last_activity) > 120: break
    except Exception: pass
    finally:
        ping_stop.set()
        for t in (ping_task, hello_task, move_task):
            if t: t.cancel()
        if sock:
            try: sock.close()
            except Exception: pass
        if squad_done is not None:
            squad_done["count"] = squad_done.get("count", 0) + 1
            if squad_done["count"] >= squad_done["total"]: squad_done["event"].set()

def _load_jwt_cache(): return _load_json_dict(JWT_CACHE_FILE)

def _save_jwt_cache(cache):
    with _file_lock:
        with open(JWT_CACHE_FILE, "w", encoding="utf-8") as f: json.dump(cache, f, indent=2, ensure_ascii=False)

def _get_cached_jwt(uid):
    cache = _load_jwt_cache(); entry = cache.get(str(uid))
    if not entry: return None
    if time.time() - float(entry.get("saved_at", 0)) > JWT_TTL: return None
    return entry

def _set_cached_jwt(uid, data):
    cache = _load_jwt_cache()
    cache[str(uid)] = {
        "jwt": data["jwt"],
        "key": data["key"].hex() if isinstance(data["key"], (bytes, bytearray)) else data["key"],
        "iv":  data["iv"].hex()  if isinstance(data["iv"],  (bytes, bytearray)) else data["iv"],
        "ts": data["ts"], "game_server": data.get("game_server", ""), "chat_server": data.get("chat_server", ""),
        "server_url": data.get("server_url", ""), "region": data.get("region", ""), "ingame_id": data.get("ingame_id", 0), "saved_at": time.time(),
    }
    _save_jwt_cache(cache)

async def _try_login_with_region(rec, account_region, tag):
    uid = rec.get("uid"); password = rec.get("pass") or rec.get("password")
    open_id = rec.get("open_id"); access_token = rec.get("access_token"); platform = rec.get("platform")
    cached = _get_cached_jwt(uid)
    if cached and cached.get("region") == account_region:
        cfg_local = build_region_cfg(account_region); server_url = cached.get("server_url") or cfg_local["server_url"]
        return {"tag": tag, "uid": uid, "ingame_id": cached.get("ingame_id", 0), "open_id": open_id, "access_token": access_token, "jwt": cached["jwt"], "key": bytes.fromhex(cached["key"]), "iv": bytes.fromhex(cached["iv"]), "ts": cached["ts"], "game_server": cached.get("game_server", ""), "chat_server": cached.get("chat_server", ""), "server_url": server_url, "name": rec.get("name", "?"), "cfg": cfg_local, "region": account_region}
    if not open_id or not access_token:
        open_id, access_token, platform = await get_guest_token(uid, password)
        rec["open_id"] = open_id; rec["access_token"] = access_token; rec["platform"] = platform
    platform = int(platform or 4)
    cfg_local = build_region_cfg(account_region)
    login = None; last_err = None
    for attempt in range(1, 5):
        try: login = await asyncio.to_thread(major_login, tag, open_id, access_token, cfg_local, platform, account_region); break
        except Exception as e:
            last_err = e; _log(f"{tag} major_login attempt {attempt}/4: {e}"); await asyncio.sleep(min(2.0 * attempt, 10.0))
    if login is None: raise RuntimeError(f"{tag} major_login gave up: {last_err}")
    payload = decode_jwt_payload(login["jwt"]) if login.get("jwt") else {}; lock_reg = (payload.get("lock_region") or "").upper()
    if lock_reg and lock_reg != account_region:
        _log(f"{tag} region override {account_region} → {lock_reg}"); account_region = lock_reg
        cfg_local = build_region_cfg(lock_reg); login = await asyncio.to_thread(major_login, tag, open_id, access_token, cfg_local, platform, lock_reg)
    ld = await asyncio.to_thread(get_login_data, tag, open_id, access_token, cfg_local, platform, login["jwt"])
    server_url = login.get("game_url") or cfg_local["server_url"]
    try:
        await give_newbie_roles(login["jwt"], server_url, login["account_id"])
        await asyncio.sleep(0.6)
        await select_homer_loadout(login["jwt"], server_url, login["account_id"])
        client_url = cfg_local.get("client_url", "https://client.ind.freefiremobile.com/")
        if not client_url.endswith("/"): client_url += "/"
        await update_avatar(login["jwt"], client_url)
    except Exception as e: _log(f"{tag} setup err: {e}")
    result = {"tag": tag, "uid": uid, "ingame_id": login["account_id"], "open_id": open_id, "access_token": access_token, "jwt": login["jwt"], "key": _to_bytes(login.get("aes_key") or b""), "iv": _to_bytes(login.get("aes_iv") or b""), "ts": login.get("server_time", 0), "game_server": ld["game_server"], "chat_server": ld["chat_server"], "server_url": server_url, "name": rec.get("name", "?"), "cfg": cfg_local, "region": account_region}
    _set_cached_jwt(uid, result)
    return result

async def login_account(rec, cfg, tag):
    stored_region = (rec.get("region") or REGION).upper(); cycle_region = (cfg.get("region") or stored_region).upper()
    attempts = [stored_region]
    if cycle_region not in attempts: attempts.append(cycle_region)
    for fallback in ("IND", "BD", "ME", "SG", "ID", "TH", "VN", "PK"):
        if fallback not in attempts: attempts.append(fallback)
    last_err = None
    for reg in attempts:
        try:
            acct = await _try_login_with_region(rec, reg, tag)
            if reg != stored_region: rec["region"] = reg; print(f"  {tag} region override: {stored_region} -> {reg}")
            return acct
        except Exception as e:
            last_err = e; msg = str(e)
            if "HTTP 400" in msg or "implausible result" in msg:
                rec["open_id"] = None; rec["access_token"] = None; rec["platform"] = None; continue
            raise
    raise RuntimeError(f"{tag} login failed for all regions: {last_err}")

async def get_guest_token(uid, password, max_retries=6):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    versions = ['4.0.18P6', '4.0.19P7', '4.0.20P1', '4.1.0P3', '4.1.5P2', '4.2.1P8', '4.2.3P1', '5.0.1B2', '5.0.2P4', '5.1.0P1', '5.2.0B1', '5.2.5P3', '5.3.0B1', '5.3.2P2', '5.4.0P1', '5.4.3B2', '5.5.0P1', '5.5.2P3']
    models = ['SM-A125F', 'SM-A225F', 'SM-A325M', 'SM-A515F', 'SM-A725F', 'SM-M215F', 'SM-M325FV', 'Redmi 9A', 'Redmi 9C', 'POCO M3', 'POCO M4 Pro', 'RMX2185', 'RMX3085', 'moto g(9) play', 'CPH2239', 'V2027', 'OnePlus Nord', 'ASUS_Z01QD']
    android_versions = ['9', '10', '11', '12', '13', '14']
    languages = ['en-US', 'es-MX', 'pt-BR', 'id-ID', 'ru-RU', 'hi-IN']
    countries = ['USA', 'MEX', 'BRA', 'IDN', 'RUS', 'IND']
    ua = (f"GarenaMSDK/{random.choice(versions)}({random.choice(models)};Android {random.choice(android_versions)};{random.choice(languages)};{random.choice(countries)};)")
    headers = {"Host": "100067.connect.garena.com", "User-Agent": ua, "Content-Type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip, deflate, br", "Connection": "close"}
    data = {"uid": _normalize_uid(uid), "password": password, "response_type": "token", "client_type": "2", "client_secret": SECRET, "client_id": "100067"}
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as r:
                    if r.status != 200:
                        last_err = f"HTTP {r.status}"; await asyncio.sleep(min(2.0 * attempt, 10.0)); continue
                    j = await r.json(); oid = j.get("open_id"); tok = j.get("access_token"); plat = j.get("platform", 4)
                    if oid and tok: return oid, tok, int(plat or 4)
                    last_err = f"missing fields: {j}"
        except Exception as e: last_err = str(e)
        await asyncio.sleep(min(2.0 * attempt, 10.0))
    raise RuntimeError(f"guest token grant failed: {last_err}")

async def run_one_squad(batch, region_hint=None):
    if not batch: return
    base_region = (region_hint or batch[0].get("region") or REGION).upper()
    region_idx = (REGION_ROTATION_LIST.index(base_region) if base_region in REGION_ROTATION_LIST else 0)
    cycle = 0
    while True:
        current_region = REGION_ROTATION_LIST[region_idx % len(REGION_ROTATION_LIST)]
        cfg = build_region_cfg(current_region); print(f"  [CYCLE {cycle}] region => {current_region}")
        logged_in = []
        for i, rec in enumerate(batch):
            tag = "[M]" if i == 0 else f"[S{i}]"
            try:
                acct = await login_account(rec, cfg, tag); acct["tag"] = tag; logged_in.append(acct)
            except Exception as e: print(f"  X {tag} login: {e}")
            await asyncio.sleep(1.5)
        if len(logged_in) < 2:
            print(f"  X not enough accounts logged in, retry 20s"); await asyncio.sleep(20.0); cycle += 1; continue
        squad_ids = [int(a["ingame_id"]) for a in logged_in]
        master = logged_in[0]; slaves = logged_in[1:]; slave_ids = [int(s["ingame_id"]) for s in slaves]
        print(f"  Team Leader => {master.get('name', '?')}")
        holder = {"group_id": None, "team_code": None, "team_code_ready": asyncio.Event(), "slave_joined": set(), "expected_ids": set(slave_ids) | {int(master["ingame_id"])}, "master_id": None}
        match_infos = {}; slave_stop = asyncio.Event()
        slave_tasks = [asyncio.create_task(slave_loop(s, holder, match_infos, slave_stop)) for s in slaves]
        await asyncio.sleep(2.0)
        master_task = asyncio.create_task(master_loop(master, slave_ids, holder, match_infos))
        expected_tags = [a["tag"] for a in logged_in]
        deadline = time.time() + 180
        while time.time() < deadline:
            if all(t in match_infos for t in expected_tags): break
            await asyncio.sleep(0.5)
        missing = [t for t in expected_tags if t not in match_infos]
        if missing:
            print(f"  X missing match info: {missing} — retry in 15s")
            slave_stop.set()
            for t in slave_tasks + [master_task]:
                if not t.done(): t.cancel()
            await asyncio.gather(*(slave_tasks + [master_task]), return_exceptions=True)
            for a in logged_in:
                w = a.get("writer")
                if w is not None:
                    try:
                        if not w.is_closing(): w.close(); await w.wait_closed()
                    except Exception: pass
                    a["writer"] = None
            await asyncio.sleep(15.0); region_idx += 1; cycle += 1; continue
        udp_tasks = []
        for a in logged_in:
            r5 = match_infos[a["tag"]]; server_ip_port = r5["2"]; udp_key = r5["3"]; join_token = r5["4"]; match_code = r5["42"]
            def _u(v): return v.get("data") if isinstance(v, dict) else v
            real_match_id = _u(r5.get("1") or 0) or 0; real_map_id = _u(r5.get("6") or 1) or 1
            real_game_mode = _u(r5.get("7") or 15) or 15; real_match_mode = _u(r5.get("8") or 1) or 1; real_sleep_ms = _u(r5.get("5") or 0) or 0
            prepare_packets, post_packet = await build_join_match_startup(join_token, udp_key, match_code, int(a["ingame_id"]), real_match_id, server_ip=server_ip_port, region=a["region"], client_version="1.132.16", client_version_code="2019121229", access_token=a["access_token"], match_id=real_match_id, country=a["region"], map_id=real_map_id, game_mode=real_game_mode, match_mode=real_match_mode)
            udp_tasks.append(asyncio.create_task(play_game_idle(server_ip_port, prepare_packets, post_packet, udp_key, match_code, int(a["ingame_id"]), a["region"], a["cfg"].get("remote_version", _PLAY_VERSION), tag=a["tag"], account_jwt=join_token, sleep_ms=real_sleep_ms, squad_done=None, name=a.get("name", "?"), squad_ids=squad_ids, server_kts=a.get("ts", 0))))
        print(f"  Match dispatched — UDP running in background, TCP held open until match ends")
        try:
            await asyncio.gather(*udp_tasks, return_exceptions=True)
            print(f"  Match finished — closing TCP")
        finally:
            slave_stop.set()
            for t in slave_tasks + [master_task]:
                if not t.done(): t.cancel()
            await asyncio.gather(*(slave_tasks + [master_task]), return_exceptions=True)
            slave_tasks.clear(); master_task = None
            for a in logged_in:
                w = a.get("writer")
                if w is not None:
                    try:
                        if not w.is_closing(): w.close(); await w.wait_closed(); _log(f"TCP closed => {a.get('name', a.get('tag'))}")
                    except Exception: pass
                    a["writer"] = None
                try: a["jwt"] = ""
                except Exception: pass
        await asyncio.sleep(NEW_MATCH_DELAY); cycle += 1
        if cycle % REGION_ROTATE_EVERY_N == 0:
            region_idx += 1; print(f"  [ROTATE] next region => {REGION_ROTATION_LIST[region_idx % len(REGION_ROTATION_LIST)]}")

async def run_squad_game(accounts, region_hint=None):
    try:
        with open(UDP_LOG_FILE, "w", encoding="utf-8") as f: f.write(f"# {datetime.now().isoformat()}\n")
    except Exception: pass
    if not accounts: return
    total = len(accounts); batch_size = SQUAD_PLAYERS; batches = [accounts[i:i + batch_size] for i in range(0, total, batch_size)]
    async def run_batch(idx, batch):
        try: await run_one_squad(batch, region_hint=region_hint)
        except Exception: pass
    await asyncio.gather(*[run_batch(i, b) for i, b in enumerate(batches, 1)], return_exceptions=True)

async def start_match_interactive():
    accounts = load_accounts()
    if len(accounts) < 2:
        print(f"  X Need at least 2 accounts (found {len(accounts)})"); return
    await run_squad_game(accounts)

def main_menu():
    while True:
        print()
        print("                Vai X Glory")
        print()
        print("  1. Gen Accounts")
        print("  2. Join Guild")
        print("  3. Add Friend (via jwt.json)")
        print("  4. Start Match")
        print()
        try: choice = input("  > ").strip()
        except (EOFError, KeyboardInterrupt): break
        if choice == "1":
            try: generate_accounts_interactive()
            except Exception as e: print(f"  X {e}")
        elif choice == "2":
            try: asyncio.run(join_clan_interactive())
            except Exception as e: print(f"  X {e}")
        elif choice == "3":
            try: asyncio.run(add_friend_interactive())
            except Exception as e: print(f"  X {e}")
        elif choice == "4":
            try: asyncio.run(start_match_interactive())
            except Exception as e: print(f"  X {e}")
        else: print(f"  ! Invalid choice")
        print()
        try: input("  Press Enter to continue...")
        except (EOFError, KeyboardInterrupt): break

if __name__ == "__main__":
    try: main_menu()
    except KeyboardInterrupt: print("\n  interrupted")
