#!/usr/bin/env python3
import json, subprocess, hashlib, os
from pathlib import Path
from runtime_registry import load_context

PREFERRED=['/generate','/chat','/predict','/respond','/infer','/run']


def run(cmd, timeout=240):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def build_payload(spec, prompt):
    payload={}
    prompt_set=False
    for p in spec.get('parameters',[]):
        name=p.get('name','')
        lname=name.lower()
        required=bool(p.get('required',False))
        default=p.get('default',None)
        typ=(p.get('type') or {}).get('type')
        if lname in {'message','prompt','text','query','input','instruction','user_message'}:
            payload[name]=prompt
            prompt_set=True
        elif lname in {'chat_history','history','messages'}:
            payload[name]=[]
        elif lname in {'max_new_tokens','max_tokens','maximum_new_tokens'}:
            payload[name]=600
        elif lname=='temperature':
            payload[name]=0.15
        elif lname=='top_p':
            payload[name]=0.9
        elif lname=='top_k':
            payload[name]=40
        elif lname in {'system','system_prompt'}:
            payload[name]='You are a rigorous adversarial research agent. CLAIM<=EVIDENCE. Distinguish actual counterexamples from hypothetical ones.'
        elif required and default is None:
            if typ=='string' and not prompt_set:
                payload[name]=prompt
                prompt_set=True
            else:
                return None
    return payload if prompt_set else None


def extract_text(raw):
    raw=(raw or '').strip()
    try:
        obj=json.loads(raw)
        if isinstance(obj,dict):
            for k in ('Response','response','text','output','message'):
                if isinstance(obj.get(k),str):
                    return obj[k].strip()
    except Exception:
        pass
    return raw


def invoke(space, prompt):
    info=run(['hf-gradio','info',space],120)
    if info.returncode!=0:
        return False,'',{'stage':'info','error':(info.stderr or info.stdout)[-1200:]}
    try:
        api=json.loads(info.stdout)
    except Exception as e:
        return False,'',{'stage':'decode','error':repr(e)}
    endpoints=list(api.items())
    endpoints.sort(key=lambda kv:(PREFERRED.index(kv[0]) if kv[0] in PREFERRED else 99,kv[0]))
    errors=[]
    for endpoint,spec in endpoints:
        payload=build_payload(spec,prompt)
        if payload is None:
            continue
        pred=run(['hf-gradio','predict',space,endpoint,json.dumps(payload,ensure_ascii=False)],240)
        if pred.returncode==0 and (pred.stdout or '').strip():
            text=extract_text(pred.stdout)
            if text:
                return True,text,{'stage':'predict','endpoint':endpoint,'sha256':hashlib.sha256(text.encode()).hexdigest()}
        errors.append((pred.stderr or pred.stdout)[-900:])
    return False,'',{'stage':'predict','error':' | '.join(errors[-3:]) or 'No compatible endpoint'}


role=os.environ['ROLE']
space=os.environ['MODEL']
focus=os.environ.get('FOCUS','counterexample and red-team analysis')
mission=Path('MISSION.md').read_text(encoding='utf-8')
registry_context,registry_meta=load_context(['constitution','macrograins','disciplines','keys'])
prompt=f'''You are {role} in CEREBRON Omega Farm 33 Counterexample / Red Team.\nFocus: {focus}.\n\n{mission}\n\nCEREBRON RUNTIME CONTEXT (shared registry; use as guidance, not as truth):\n{registry_context}\n\nAttack one representative claim or model in your focus domain. Produce a concise adversarial report with: target claim, domain, explicit assumptions, hidden assumptions, minimal counterexample candidate, whether it is actual or hypothetical, reproducibility conditions, falsification mechanism, edge cases, regime changes, contradictions, evidence gaps, and a bounded verdict. Never fabricate a counterexample or source.'''

ok,text,meta=invoke(space,prompt)
record={
    'farm':33,
    'role':role,
    'model':space,
    'focus':focus,
    'provider':'huggingface-space-zerogpu',
    'inference_success':ok,
    'status':'UNREVIEWED_EXTERNAL_AGENT_OUTPUT' if ok else 'EXTERNAL_INFERENCE_FAILED',
    'response':text if ok else None,
    'registry_runtime':registry_meta,
    'meta':meta,
}
Path('results').mkdir(exist_ok=True)
Path(f'results/{role}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'role':role,'status':record['status'],'inference_success':ok,'registry_runtime':registry_meta,'meta':meta},ensure_ascii=False))
