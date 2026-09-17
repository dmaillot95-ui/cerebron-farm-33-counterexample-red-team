import json, urllib.request
from pathlib import Path

RAW_BASE='https://raw.githubusercontent.com/dmaillot95-ui/cerebron-omega-encyclopedia/main/'

def _get(url, timeout=20):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read().decode('utf-8')

def load_context(categories, max_chars=12000):
    meta={'loaded':False,'categories':[],'errors':[],'registry_version':None}
    try:
        local=json.loads(Path('CEREBRON_REGISTRY.json').read_text(encoding='utf-8'))
        manifest=json.loads(_get(local['registry']))
        meta['registry_version']=manifest.get('version')
        chunks=[]
        for c in categories:
            p=(manifest.get('paths') or {}).get(c)
            if not p: continue
            try:
                text=_get(RAW_BASE+p)
                chunks.append(f'### {c.upper()}\n{text}')
                meta['categories'].append(c)
            except Exception as e:
                meta['errors'].append(f'{c}:{type(e).__name__}:{e}')
        joined='\n\n'.join(chunks)
        if len(joined)>max_chars: joined=joined[:max_chars]+'\n[TRUNCATED_RUNTIME_CONTEXT]'
        meta['loaded']=bool(chunks)
        return joined,meta
    except Exception as e:
        meta['errors'].append(f'manifest:{type(e).__name__}:{e}')
        return '',meta
