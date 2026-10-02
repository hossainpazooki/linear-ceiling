from common import *
primary=json.loads((ROOT/'math/results.json').read_text());assert len(primary)==64
inputs=json.loads((ROOT/'math-inputs.json').read_text())['items']
flips=[r['i'] for r in primary if r['fresh']['correct']!=r['stale']['correct']]
write(ROOT/'math/fp32-selection.json',flips)
if not flips:
    write(ROOT/'math/fp32-results.json',[]);print('NO FLIPS',flush=True);raise SystemExit()
model,tok=load('olmo200','mps','float32')
for i in flips:
    c,_=prefill(model,inputs[i]['ids'][:-1]);torch.save(kvs(c,cpu=True),ROOT/'math'/f'fp32-old-{i}.pt');del c;clear()
del model,tok;clear()
model,tok=load('olmo2600','mps','float32')
eos=model.generation_config.eos_token_id;eos=set(eos if isinstance(eos,list) else [eos]);rows=[]
for i in flips:
    item=inputs[i];row={'i':i,'id':item['id'],'gold':primary[i]['gold']}
    for arm in ['fresh','stale']:
        if arm=='fresh':c,_=prefill(model,item['ids'][:-1])
        else:
            old=torch.load(ROOT/'math'/f'fp32-old-{i}.pt',weights_only=True,mmap=True);c=cache_from(old,'mps')
        ids,_=decode(model,c,item['ids'][-1:],384,eos)
        text=tok.decode(ids,skip_special_tokens=True);pred,marked=answer(text)
        row[arm]={'answer':pred,'correct':pred==row['gold'],'text':text,'n_tokens':len(ids),
                  'truncated':len(ids)==384 and ids[-1] not in eos,'has_marker':marked}
        del c;clear()
    row['primary']={arm:primary[i][arm]['correct'] for arm in ['fresh','stale']}
    rows.append(row);write(ROOT/'math/fp32-results.json',rows)
    print(json.dumps({k:v for k,v in row.items() if k not in ['fresh','stale']}|{arm:row[arm]['correct'] for arm in ['fresh','stale']}),flush=True)
print('COMPLETE',len(rows),flush=True)
