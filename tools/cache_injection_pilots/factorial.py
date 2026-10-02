# Paired YaRN/context-extension pilot. No complete KV cache is saved to disk.
import argparse
import json
import time

from common import ROOT, clear, digest, distributions, load, np, prefill, rotate, sync, torch, write


def select_cases():
    report = json.loads((ROOT / 'records/report.json').read_text())
    cases = []
    for path in sorted((ROOT / 'records/align').glob('*.json')):
        meta = json.loads(path.read_text())
        if 'handoff_id' not in meta:
            continue
        if not meta['excluded'] and meta['handoff_id'] in report['scores']:
            cases.append((meta, path.with_suffix('.npz')))
    cases.sort(key=lambda c: (c[0]['n_sender'], c[0]['handoff_id']))
    assert len(cases) >= 4
    out = []
    for meta, path in cases[:4]:
        with np.load(path) as data:
            sender, receiver, pairs = (data[k] for k in ('sender', 'receiver', 'pairs'))
        assert (len(sender), len(receiver), len(pairs)) == tuple(meta[k] for k in ('n_sender', 'n_receiver', 'n_matched'))
        assert len(pairs) >= 512
        selected = np.linspace(0, len(pairs) - 1, 512, dtype=np.int64)
        pairs = pairs[selected]
        assert len(np.unique(selected)) == 512
        assert np.array_equal(sender[pairs[:, 0]], receiver[pairs[:, 1]])
        assert max(len(sender), len(receiver)) + 4096 < 32768
        out.append({'meta': meta, 'path': path, 'sender': sender, 'receiver': receiver,
                    'pairs': pairs, 'pair_indices': selected})
    return out


def selected_prefill(model, ids, positions, chunk):
    # Keep only matched positions; invert the rotary transform actually used by this model.
    sync()
    start = time.perf_counter()
    cache, logits = prefill(model, ids, chunk=chunk)
    sync()
    elapsed = time.perf_counter() - start
    logits = logits.detach().float().cpu()
    emb = model.model.rotary_emb
    freq, amplitude = emb.inv_freq.detach().float().cpu(), float(emb.attention_scaling)
    index = torch.as_tensor(positions, dtype=torch.long, device=model.device)
    selected = []
    for layer in cache.layers:
        key = layer.keys.index_select(-2, index).detach().float().cpu()
        value = layer.values.index_select(-2, index).detach().float().cpu()
        # rotate receives fp32, so its dtype-preserving return does not round back to fp16.
        key = rotate(key, -np.asarray(positions), freq, scale=1.0 / amplitude)
        if not torch.isfinite(key).all() or not torch.isfinite(value).all():
            raise ValueError('Nonfinite selected KV')
        selected.append((key, value))
    if not torch.isfinite(logits).all():
        raise ValueError('Nonfinite logits')
    del cache, index, layer, key, value
    clear()
    return selected, logits, elapsed, {'inv_freq': freq.tolist(), 'attention_scaling': amplitude}


def variance(reference, kind):
    # Per layer/head E_token ||KV - E_token KV||², matching the centered metric's units.
    out = []
    for kv in reference:
        x = kv[kind][0].numpy().astype(np.float64)  # [head, token, dimension]
        out.append(np.square(x - x.mean(1, keepdims=True)).sum(-1).mean(-1))
    var = np.stack(out)
    if not np.isfinite(var).all() or np.any(var <= 0):
        raise ValueError('Degenerate reference variance')
    return var


def squares(source, receiver, kind):
    # Squared vector errors [token, layer, head], evaluated in fp64 on CPU.
    out = []
    max_abs = 0.0
    for skv, rkv in zip(source, receiver, strict=True):
        diff = skv[kind][0].numpy().astype(np.float64) - rkv[kind][0].numpy()
        out.append(np.square(diff).sum(-1))
        max_abs = max(max_abs, float(np.abs(diff).max()))
    return np.stack(out).transpose(2, 0, 1), max_abs


def measure(source, receiver, fixed_var):
    stats, arrays = {}, {}
    head_dim = source[0][0].shape[-1]
    for kind, label in enumerate(('K', 'V')):
        sq, max_abs = squares(source, receiver, kind)
        cell_var = variance(receiver, kind)
        normalized = sq / fixed_var[label][None]
        values = {'mean_fixed_normalized_error': float(normalized.mean()),
                  'mean_cell_normalized_error': float((sq / cell_var[None]).mean()),
                  'raw_mean_squared_coordinate_error': float(sq.mean() / head_dim),
                  'max_absolute_coordinate_error': max_abs,
                  'max_token_fixed_normalized_error': float(normalized.mean((1, 2)).max())}
        if not np.isfinite(list(values.values())).all():
            raise ValueError('Nonfinite measurement')
        stats[label] = values
        arrays.update({f'{label}_squared_vector_error': sq,
                       f'{label}_fixed_variance': fixed_var[label],
                       f'{label}_cell_variance': cell_var})
    return stats, arrays


def contrasts(cells):
    out = {}
    for kind in ('K', 'V'):
        out[kind] = {}
        for metric in ('mean_fixed_normalized_error', 'raw_mean_squared_coordinate_error'):
            ns, nl, ys, yl = (cells[c][kind][metric] for c in
                              ('native_original', 'native_extended', 'yarn_original', 'yarn_extended'))
            out[kind][metric] = {'scaling_original': ys - ns, 'scaling_extended': yl - nl,
                                'extension_native': nl - ns, 'extension_yarn': yl - ys,
                                'interaction': (yl - ys) - (nl - ns)}
    return out


def arithmetic_check():
    # A non-unit rotary amplitude would fail this check if stripping forgot to divide by m.
    g = torch.Generator().manual_seed(230923)
    x = torch.randn((1, 2, 7, 16), generator=g)
    freq = 1.0 / (10000 ** (torch.arange(0, 16, 2).float() / 16))
    positions = np.arange(7) * 311
    transformed = rotate(x, positions, freq, 1.13)
    restored = rotate(transformed, -positions, freq, 1 / 1.13)
    err = float((restored - x).abs().max())
    assert err < 2e-6, err
    ref = [(x, x * 2)]
    v = {'K': variance(ref, 0), 'V': variance(ref, 1)}
    same, _ = measure(ref, ref, v)
    assert same['K']['mean_fixed_normalized_error'] == 0
    changed = [(x + 0.125, x * 2 + 0.25)]
    measured, _ = measure(changed, ref, v)
    expected = float((16 * 0.125 ** 2 / v['K']).mean())
    assert abs(measured['K']['mean_fixed_normalized_error'] - expected) < 1e-7
    assert abs(measured['V']['mean_fixed_normalized_error'] - expected) < 1e-7
    return {'rotary_inverse_max_error': err, 'known_offset_normalized_error': expected}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--device', default='mps')
    ap.add_argument('--dtype', default='float16')
    ap.add_argument('--chunk', type=int, default=256)
    ap.add_argument('--check-only', action='store_true')
    args = ap.parse_args()
    cases = select_cases()
    extension = cases[0]['sender'][:4096]
    checked = arithmetic_check()
    selected_meta = [{**c['meta'], 'alignment_sha256': digest(c['path'])} for c in cases]
    if args.check_only:
        print(json.dumps({'arithmetic': checked, 'selected': selected_meta}, indent=2), flush=True)
        return
    records = ROOT / 'factorial-records'
    records.mkdir(exist_ok=True)
    np.save(records / 'extension.npy', extension)
    source_record = json.loads((ROOT / 'records/source.json').read_text())
    state = {'protocol_sha256': digest(ROOT / 'docs/protocols.html'), 'script_sha256': digest(__file__),
             'common_sha256': digest(ROOT / 'common.py'), 'device': args.device, 'dtype': args.dtype,
             'chunk': args.chunk, 'torch': torch.__version__, 'arithmetic_checks': checked,
             'dataset': {k: source_record[k] for k in ('repo', 'revision')},
             'model_revision': (ROOT / 'models/qwen/.ready').read_text().strip(),
             'extension_tokens': len(extension), 'extension_sha256': digest(records / 'extension.npy'),
             'sample_size': 512, 'complete': False, 'cases': []}
    logits_by_case = [{} for _ in cases]
    fixed_by_case = {}
    for i, case in enumerate(cases):
        np.savez(records / f'case{i}_selection.npz', pairs=case['pairs'], pair_indices=case['pair_indices'])
        state['cases'].append({**selected_meta[i], 'cells': {}})
    for scaled in (False, True):
        config_name = 'yarn' if scaled else 'native'
        model, tokenizer = load('qwen', device=args.device, dtype=args.dtype, yarn=scaled)
        del tokenizer
        for i, case in enumerate(cases):
            row = state['cases'][i]
            for extended in (False, True):
                cell = config_name + ('_extended' if extended else '_original')
                prefix = extension if extended else np.empty(0, dtype=np.int64)
                offset = len(prefix)
                sender = np.concatenate((prefix, case['sender']))
                receiver = np.concatenate((prefix, case['receiver']))
                source_kv, _, source_s, rope = selected_prefill(model, sender, case['pairs'][:, 0] + offset, args.chunk)
                target_kv, target_logits, target_s, target_rope = selected_prefill(model, receiver, case['pairs'][:, 1] + offset, args.chunk)
                assert rope == target_rope  # Static native/YaRN spec must not change with sequence length.
                if cell == 'native_original':
                    fixed_by_case[i] = {kind: variance(target_kv, j) for j, kind in enumerate(('K', 'V'))}
                metrics, audit = measure(source_kv, target_kv, fixed_by_case[i])
                audit_path = records / f'case{i}_{cell}.npz'
                np.savez_compressed(audit_path, **audit, receiver_next_logits=target_logits.numpy())
                row['cells'][cell] = {**metrics, 'sender_tokens': len(sender), 'receiver_tokens': len(receiver),
                                      'sender_prefill_seconds': source_s, 'receiver_prefill_seconds': target_s,
                                      'rope': rope, 'audit_file': audit_path.name, 'audit_sha256': digest(audit_path)}
                logits_by_case[i][cell] = target_logits
                if i == 0 and cell == 'native_original':
                    repeat_kv, repeat_logits, repeat_s, _ = selected_prefill(model, receiver, case['pairs'][:, 1], args.chunk)
                    control, control_audit = measure(repeat_kv, target_kv, fixed_by_case[i])
                    row['repeat_prefill_control'] = {**control, 'seconds': repeat_s,
                                                     'next_token_distribution': distributions(target_logits, repeat_logits)}
                    np.savez_compressed(records / 'repeat_control.npz', **control_audit)
                    del repeat_kv, repeat_logits, control_audit
                del source_kv, target_kv, audit
                clear()
                write(ROOT / 'factorial-results.json', state)
                print(json.dumps({'case': i, 'cell': cell, 'handoff_id': row['handoff_id'],
                                  'K': metrics['K'], 'V': metrics['V'],
                                  'prefill_seconds': source_s + target_s}), flush=True)
        del model
        clear()
    for i, row in enumerate(state['cases']):
        row['contrasts'] = contrasts(row['cells'])
        logits = logits_by_case[i]
        row['next_token_contrasts'] = {
            name: distributions(logits[a], logits[b]) for name, a, b in (
                ('scaling_original', 'native_original', 'yarn_original'),
                ('scaling_extended', 'native_extended', 'yarn_extended'),
                ('extension_native', 'native_original', 'native_extended'),
                ('extension_yarn', 'yarn_original', 'yarn_extended'))}
    state['complete'] = True
    write(ROOT / 'factorial-results.json', state)
    print('COMPLETE factorial-results.json', flush=True)


if __name__ == '__main__':
    main()
