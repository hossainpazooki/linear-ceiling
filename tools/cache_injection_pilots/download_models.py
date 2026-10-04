from pathlib import Path
import os
os.environ['HF_HOME'] = str(Path(__file__).parent / 'hf')
from huggingface_hub import snapshot_download

models = [('Qwen/Qwen3-1.7B', '70d244cc86ccca08cf5af4e1e306ecf908b1ad5e', 'qwen'),
          ('allenai/OLMo-2-0425-1B-RLVR1', 'b85a22f7df1c1f4616fa569521236642c78863d8', 'olmo200'),
          ('allenai/OLMo-2-0425-1B-RLVR1', '9f0904d82d97214fded1d537dd7a4aeadb976461', 'olmo1200'),
          ('allenai/OLMo-2-0425-1B-RLVR1', 'bf37756016867cfaf3d54319ba613aedc9b56f3c', 'olmo2600')]
for repo, rev, name in models:
    path = snapshot_download(repo, revision=rev, local_dir=Path(__file__).parent/'models'/name,
                             allow_patterns=['*.json', '*.safetensors', '*.txt', '*.model'], max_workers=3)
    (Path(path)/'.ready').write_text(rev)
    print('READY', name, rev, flush=True)
