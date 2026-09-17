#!/usr/bin/env python3
import json, subprocess, hashlib
PREFERRED=['/generate','/chat','/predict','/respond','/infer','/run']
def run(cmd,timeout=240): return subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
def build_payload(spec,prompt):
    payload={}; prompt_set=False
    for p in spec.get('parameters',[]):
        name=p.get('name',''); lname=name.lower(); required=bool(p.get('required',False)); default=p.get('default',None); typ=(p.get('type') or {}).get('type')
        if lname in {'message','prompt','text','query','input','instruction','user_message'}: payload[name]=prompt; prompt_set=True
        elif lname in {'chat_history','history','messages'}: payload[name]=[]
        elif lname in {'max_new_tokens','max_tokens','maximum_new_tokens'}: payload[name]=900
        elif lname=='temperature': payload[name]=0.1
        elif lname=='top_p': payload[name]=0.9
        elif lname=='top_k': payload[name]=40
        elif lname in {'system','system_prompt'}: payload[name]='You are a rigorous research agent. CLAIM<=EVIDENCE.'
        elif required and default is None:
            if typ=='string' and not prompt_set: payload[name]=prompt; prompt_set=True
            else: return None
    return payload if prompt_set else None
def extract_text(raw):
    raw=raw.strip()
    try:
        obj=json.loads(raw)
        if isinstance(obj,dict):
            for k in ('Response','response','text','output','message'):
                if isinstance(obj.get(k),str): return obj[k].strip()
    except Exception: pass
    return raw
def invoke(space,prompt):
    info=run(['hf-gradio','info',space],120)
    if info.returncode!=0: return False,'',{'stage':'info','error':(info.stderr or info.stdout)[-1200:]}
    try: api=json.loads(info.stdout)
    except Exception as e: return False,'',{'stage':'decode','error':repr(e)}
    endpoints=list(api.items()); endpoints.sort(key=lambda kv:(PREFERRED.index(kv[0]) if kv[0] in PREFERRED else 99,kv[0]))
    errors=[]
    for endpoint,spec in endpoints:
        payload=build_payload(spec,prompt)
        if payload is None: continue
        pred=run(['hf-gradio','predict',space,endpoint,json.dumps(payload,ensure_ascii=False)],240)
        if pred.returncode==0 and (pred.stdout or '').strip():
            text=extract_text(pred.stdout); return True,text,{'stage':'predict','endpoint':endpoint,'sha256':hashlib.sha256(text.encode()).hexdigest()}
        errors.append((pred.stderr or pred.stdout)[-700:])
    return False,'',{'stage':'predict','error':' | '.join(errors[-3:]) or 'No compatible endpoint'}
