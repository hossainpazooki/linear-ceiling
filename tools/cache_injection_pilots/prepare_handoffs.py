from common import *
import re
report=json.loads((ROOT/'records/report.json').read_text());candidates=[]
for hid,rec in report['scores'].items():
    path=ROOT/'records/align'/rec['score_file'];meta=json.loads(path.read_text())
    candidates.append((meta['n_sender'],hid,path.with_suffix('.npz')))
tok=AutoTokenizer.from_pretrained(ROOT/'models/qwen',local_files_only=True)
rows=[]
for n,hid,path in sorted(candidates)[:4]:
    z=np.load(path);r=z['receiver'];text=tok.decode(r,skip_special_tokens=False)
    funcs=re.findall(r'\bdef\s+([A-Za-z_]\w*)\s*\(',text)
    classes=re.findall(r'\bclass\s+([A-Za-z_]\w*)\s*[:(]',text)
    repo=re.search(r'repository\s+([\w.-]+/[\w.-]+)\s+cloned',text)
    print(hid,'S/R/M',len(z['sender']),len(r),len(z['pairs']),flush=True)
    print('repository',repo.group(1) if repo else None,'functions',funcs[:6],'classes',classes[:6],flush=True)
    qs=[]
    if repo:qs.append({'question':'Which repository does the initial HumanMessage say is cloned in the workspace? Reply with only owner/repository.','gold':repo.group(1),'kind':'repository'})
    if funcs:qs.append({'question':'What is the name of the FIRST Python function defined with the keyword def anywhere in the history? Reply with only the function name, without parentheses.','gold':funcs[0],'kind':'function'})
    if classes:qs.append({'question':'What is the name of the FIRST Python class defined with the keyword class anywhere in the history? Reply with only the class name.','gold':classes[0],'kind':'class'})
    assert len(qs)>=2,hid
    rows.append({'id':hid,'path':str(path.relative_to(ROOT)),'questions':qs,'n_sender':len(z['sender']),'n_receiver':len(r)})
write(ROOT/'handoffs.json',rows)
print('FROZEN',digest(ROOT/'handoffs.json'),flush=True)
