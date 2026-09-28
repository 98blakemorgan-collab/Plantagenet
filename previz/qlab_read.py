"""Decode a QLab 5 workspace (NSKeyedArchiver plist) into plain Python objects."""
import plistlib

def load(path):
    return loads(open(path, 'rb').read())


def loads(raw):
    d = plistlib.loads(raw)
    objs = d['$objects']
    memo = {}

    def res(v):
        if isinstance(v, plistlib.UID):
            i = v.data
            if i in memo:
                return memo[i]
            o = objs[i]
            if o == '$null':
                memo[i] = None
                return None
            if isinstance(o, dict):
                cls = objs[o['$class'].data]['$classname'] if '$class' in o else None
                if 'NS.keys' in o:
                    out = {}
                    memo[i] = out
                    for k, val in zip(o['NS.keys'], o['NS.objects']):
                        out[res(k)] = res(val)
                    return out
                if 'NS.objects' in o:
                    out = []
                    memo[i] = out
                    out.extend(res(x) for x in o['NS.objects'])
                    return out
                if 'NS.string' in o:
                    memo[i] = o['NS.string']; return o['NS.string']
                if 'NS.data' in o:
                    raw = o['NS.data']
                    val = loads(raw) if raw[:6] == b'bplist' else raw
                    memo[i] = val; return val
                if 'NS.time' in o:
                    memo[i] = o['NS.time']; return o['NS.time']
                out = {'__class__': cls}
                memo[i] = out
                for k, val in o.items():
                    if k != '$class':
                        out[k] = res(val)
                return out
            memo[i] = o
            return o
        if isinstance(v, list):
            return [res(x) for x in v]
        if isinstance(v, dict):
            return {k: res(x) for k, x in v.items()}
        return v

    return res(d['$top']['root'] if 'root' in d['$top'] else list(d['$top'].values())[0])
