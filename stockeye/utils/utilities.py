def safe_get(data, key, default=None):
    if data is None: return default
    try: return data.get(key, default)
    except: return default

def safe_float(value, default=0.0):
    try: return float(value)
    except: return default

def safe_int(value, default=0):
    try: return int(value)
    except: return default
