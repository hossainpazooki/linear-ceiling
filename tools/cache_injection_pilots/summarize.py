import json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).parent

def paired(rows,complete_only=False):
    f=np.array([r['fresh']['correct'] and (not complete_only or not r['fresh']['truncated']) for r in rows])
    s=np.array([r['stale']['correct'] and (not complete_only or not r['stale']['truncated']) for r in rows])
    n=len(rows);h=int((f&~s).sum());e=int((~f&s).sum())
    counts=np.array([int((f&s).sum()),h,e,int((~f&~s).sum())])
    draws=np.random.default_rng(230923).multinomial(n,counts/n,100000)
    lo,hi=np.quantile((draws[:,2]-draws[:,1])/n,[.025,.975])
    l,u=h/n,1.0
    if h<n:
        for _ in range(80):
            p=(l+u)/2
            cdf=sum(math.comb(n,k)*p**k*(1-p)**(n-k) for k in range(h+1))
            if cdf>.05:l=p
            else:u=p
    return {'n':n,'fresh_correct':int(f.sum()),'stale_correct':int(s.sum()),'both_correct':int(counts[0]),
            'harmed':h,'helped':e,'both_wrong':int(counts[3]),'delta_pp':float((s.mean()-f.mean())*100),
            'paired_bootstrap_95_pp':[float(lo*100),float(hi*100)],'harm_one_sided_95_upper':u}

out={}
if (ROOT/'math/results.json').exists():
    rows=json.loads((ROOT/'math/results.json').read_text())
    out['math']={'scored':paired(rows),'complete_only':paired(rows,True),
        'truncated':{a:sum(r[a]['truncated'] for r in rows) for a in ['fresh','stale']},
        'no_marker':{a:sum(not r[a]['has_marker'] for r in rows) for a in ['fresh','stale']},
        'max_fstar03':max(r['tensor']['fstar']['0.03'] for r in rows),
        'mean_tensor_error_range':[min(r['tensor']['mean'] for r in rows),max(r['tensor']['mean'] for r in rows)],
        'same_first_token':sum(r['next_token']['top_same'] for r in rows),
        'changed_continuation':sum(r['fresh']['ids']!=r['stale']['ids'] for r in rows),
        'changed_numeric_answer':sum(r['fresh']['answer']!=r['stale']['answer'] for r in rows),
        'first_token_tv_range':[min(r['next_token']['tv'] for r in rows),max(r['next_token']['tv'] for r in rows)],
        'zero_lag_controls':[r['zero_lag_exact'] for r in rows if 'zero_lag_exact' in r],
        'scrambled_correct':sum(r['scrambled']['correct'] for r in rows if 'scrambled' in r),
        'scrambled_n':sum('scrambled' in r for r in rows),
        'flips':[{'i':r['i'],'id':r['id'],'gold':r['gold'],'fresh':r['fresh']['answer'],
                  'stale':r['stale']['answer'],'fresh_correct':r['fresh']['correct'],'stale_correct':r['stale']['correct']} for r in rows if r['fresh']['correct']!=r['stale']['correct']]}
if (ROOT/'math/fp32-results.json').exists():out['fp32']=json.loads((ROOT/'math/fp32-results.json').read_text())
if (ROOT/'factorial-results.json').exists():
    data=json.loads((ROOT/'factorial-results.json').read_text())
    out['factorial']={'complete':data['complete'],'cases':[]}
    for c in data['cases']:
        row={'id':c['handoff_id'],'cells':{name:{k:v[k]['mean_fixed_normalized_error'] for k in ['K','V']} for name,v in c['cells'].items()}}
        if 'contrasts' in c:
            row['contrasts']=c['contrasts']
            row['next_token']=c['next_token_contrasts']
        out['factorial']['cases'].append(row)
if (ROOT/'archive-audit.json').exists():
    out['archive_audit']=json.loads((ROOT/'archive-audit.json').read_text())['summary']
if (ROOT/'practical-results.json').exists():
    cases=json.loads((ROOT/'practical-results.json').read_text());out['practical']=[]
    for c in cases:
        row={k:c[k] for k in ['id','original_sender_tokens','original_receiver_tokens','source_prefill_s','controls']}
        for mode in ['fresh','prefix','block']:
            rs=[r for r in c['runs'] if r['mode']==mode]
            q=[q for r in rs for q in r['answers']]
            row[mode]={'prefill_median_s':float(np.median([r['seconds'] for r in rs])),
                'alignment_median_s':float(np.median([r['alignment_seconds'] for r in rs])),
                'prefill_range_s':[min(r['seconds'] for r in rs),max(r['seconds'] for r in rs)],
                'one_question_total_median_s':float(np.median([r['seconds']+q['seconds'] for r in rs for q in r['answers']])),
                'copied':rs[0]['copied'],'recomputed':rs[0]['recomputed'],'blocks':rs[0]['blocks'],
                'unique_questions':len(rs[0]['answers']),'correct_per_rep':[sum(q['correct'] for q in r['answers']) for r in rs],
                'tv':rs[0]['next_token']['tv'],'top_same':rs[0]['next_token']['top_same'],
                'truncated':sum(x['truncated'] for x in q)}
        row['block_prefill_speedup']=row['fresh']['prefill_median_s']/row['block']['prefill_median_s']
        row['block_total_speedup']=row['fresh']['one_question_total_median_s']/row['block']['one_question_total_median_s']
        row['scrambled_correct']=sum(q['correct'] for q in c['scrambled']['answers'])
        out['practical'].append(row)
(ROOT/'summary.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='fp32'},indent=2))
