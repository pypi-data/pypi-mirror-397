import datetime
import enum
import json
import random
import string
import time
import urllib
import hashlib
import base64
import uuid
import hmac
from .config import USER_AGENT_BASE

import json
import os
from typing import Dict, Any, Iterator


class PersistentDict:
    """A dictionary-like class that automatically persists changes to a JSON file."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self._data: Dict[str, str] = {}
        self._load()
    
    def _load(self):
        """Load data from the JSON file if it exists."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure all values are strings
                    self._data = {k: str(v) for k, v in data.items()}
            except (json.JSONDecodeError, FileNotFoundError):
                self._data = {}
        else:
            self._data = {}
    
    def _save(self):
        """Save current data to the JSON file."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
    
    def __getitem__(self, key: str) -> str:
        return self._data[key]
    
    def __setitem__(self, key: str, value: str):
        self._data[key] = str(value)
        self._save()
    
    def __delitem__(self, key: str):
        del self._data[key]
        self._save()
    
    def __contains__(self, key: str) -> bool:
        return key in self._data
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __iter__(self) -> Iterator[str]:
        return iter(self._data)
    
    def get(self, key: str, default: str = None) -> str:
        return self._data.get(key, default)
    
    def keys(self):
        return self._data.keys()
    
    def values(self):
        return self._data.values()
    
    def items(self):
        return self._data.items()
    
    def update(self, other: Dict[str, str]):
        """Update the dictionary with key-value pairs from another dict."""
        for key, value in other.items():
            self._data[key] = str(value)
        self._save()
    
    def clear(self):
        """Clear all data from the dictionary."""
        self._data.clear()
        self._save()
    
    def pop(self, key: str, default: str = None) -> str:
        """Remove and return the value for key, or default if not found."""
        value = self._data.pop(key, default)
        self._save()
        return value



class InstagramIdCodec:
    ENCODING_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

    @staticmethod
    def encode(num, alphabet=ENCODING_CHARS):
        """Covert a numeric value to a shortcode."""
        num = int(num)
        if num == 0:
            return alphabet[0]
        arr = []
        base = len(alphabet)
        while num:
            rem = num % base
            num //= base
            arr.append(alphabet[rem])
        arr.reverse()
        return "".join(arr)

    @staticmethod
    def decode(shortcode, alphabet=ENCODING_CHARS):
        """Covert a shortcode to a numeric value."""
        base = len(alphabet)
        strlen = len(shortcode)
        num = 0
        idx = 0
        for char in shortcode:
            power = strlen - (idx + 1)
            num += alphabet.index(char) * (base**power)
            idx += 1
        return num


class InstagrapiJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        elif isinstance(obj, datetime.time):
            return obj.strftime("%H:%M")
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return int(obj.strftime("%s"))
        elif isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def generate_signature(data):
    """Generate signature of POST data for Private API

    Returns
    -------
    str
        e.g. "signed_body=SIGNATURE.test"
    """
    return "signed_body=SIGNATURE.{data}".format(data=urllib.parse.quote_plus(data))


def json_value(data, *args, default=None):
    cur = data
    for a in args:
        try:
            if isinstance(a, int):
                cur = cur[a]
            else:
                cur = cur.get(a)
        except (IndexError, KeyError, TypeError, AttributeError):
            return default
    return cur


def gen_token(size=10, symbols=False):
    """Gen CSRF or something else token"""
    chars = string.ascii_letters + string.digits
    if symbols:
        chars += string.punctuation
    return "".join(random.choice(chars) for _ in range(size))


def gen_password(size=10):
    """Gen password"""
    return gen_token(size)


def dumps(data):
    """Json dumps format as required Instagram"""
    return InstagrapiJSONEncoder(separators=(",", ":")).encode(data)


def generate_jazoest(symbols: str) -> str:
    amount = sum(ord(s) for s in symbols)
    return f"2{amount}"


def date_time_original(localtime):
    # return time.strftime("%Y:%m:%d+%H:%M:%S", localtime)
    return time.strftime("%Y%m%dT%H%M%S.000Z", localtime)


def random_delay(delay_range: list):
    """Trigger sleep of a random floating number in range min_sleep to max_sleep"""
    return time.sleep(random.uniform(delay_range[0], delay_range[1]))


def generate_android_device_id():
        """
        Helper to generate Android Device ID
        """
        return "android-%s" % hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

def generate_uuid(prefix: str = "", suffix: str = ""):
        """
        Helper to generate uuids
        """
        return f"{prefix}{uuid.uuid4()}{suffix}"

def generate_mutation_token() -> str:
        """Token used when DM sending and upload media"""
        return str(random.randint(6800011111111111111, 6800099999999999999))

def generate_user_agent(data):
    return USER_AGENT_BASE.format(**data)


def gen_user_breadcrumb(size: int) -> str:
        """
        Helper to generate user breadcrumbs

        Parameters
        ----------
        size: int
            Integer value

        Returns
        -------
        Str
            A string
        """
        key = "iN4$aGr0m"
        dt = int(time.time() * 1000)
        time_elapsed = random.randint(500, 1500) + size * random.randint(500, 1500)
        text_change_event_count = max(1, size / random.randint(3, 5))
        data = "{size!s} {elapsed!s} {count!s} {dt!s}".format(
            **{
                "size": size,
                "elapsed": time_elapsed,
                "count": text_change_event_count,
                "dt": dt,
            }
        )
        return "{!s}\n{!s}\n".format(
            base64.b64encode(
                hmac.new(
                    key.encode("ascii"), data.encode("ascii"), digestmod=hashlib.sha256
                ).digest()
            ),
            base64.b64encode(data.encode("ascii")),
        )