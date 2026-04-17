"""
MAMPA — Omeka S to Graph JSON
Transforma el export de ítems de Omeka S en un grafo multipartito.

Uso:
    python omeka_to_graph.py [input.xlsx]

Genera: data/graph.json  (relativo al directorio del proyecto)
"""
import pandas as pd
import json
import hashlib
import sys
import os
from collections import Counter

# --- Configuración ---
SUBJECT_MIN_FREQ = 3
ITEM_COLOR = '#7a8b6e'
GRAPH_DIMENSIONS = {
    'creator':  {'col': 'dcterms:creator',  'rel': 'authored_by',     'color': '#7b68ae'},
    'subject':  {'col': 'dcterms:subject',  'rel': 'tagged_with',     'color': '#c4973b'},
    'coverage': {'col': 'dcterms:coverage', 'rel': 'belongs_to_area', 'color': '#b5634b'},
    'type':     {'col': 'dcterms:type',     'rel': 'is_type',         'color': '#c27a8e'},
}

def parse_multival(val):
    if pd.isna(val):
        return []
    return [v.strip() for v in str(val).split('|') if v.strip()]

def make_id(node_type, label):
    slug = hashlib.md5(f"{node_type}:{label}".encode()).hexdigest()[:8]
    return f"{node_type}_{slug}"

def main(input_file):
    df = pd.read_excel(input_file)
    print(f"Ítems cargados: {len(df)}")

    # Frecuencias de subjects
    subject_freq = Counter()
    for val in df['dcterms:subject'].dropna():
        for s in parse_multival(val):
            subject_freq[s] += 1
    valid_subjects = {s for s, f in subject_freq.items() if f >= SUBJECT_MIN_FREQ}
    print(f"Subjects: {len(subject_freq)} → {len(valid_subjects)} (freq≥{SUBJECT_MIN_FREQ})")

    nodes = {}
    edges = []

    # Nodos item — campos abreviados para coincidir con el mapeo del HTML
    for _, row in df.iterrows():
        item_id = f"item_{row['o:id']}"
        title = str(row.get('dcterms:title', '')).strip()
        abstract = str(row.get('dcterms:abstract', '')).strip()
        if abstract == 'nan': abstract = ''
        if len(abstract) > 300: abstract = abstract[:297] + '...'

        nodes[item_id] = {
            'id': item_id,
            'l':  title if len(title) <= 80 else title[:77] + '...',   # label
            'ft': title,                                                  # full_title
            't':  'item',                                                 # type
            'c':  ITEM_COLOR,                                             # color
            'url': str(row.get('url', '')),
            'abs': abstract,
            'pub': str(row.get('dcterms:publisher', '')).replace('nan', ''),
            'dt':  str(row.get('dcterms:issued', '')).replace('nan', ''),
            'el':  parse_multival(row.get('dcterms:educationLevel')),
        }

    # Nodos atributo + aristas — campos abreviados
    for _, row in df.iterrows():
        item_id = f"item_{row['o:id']}"
        for dim_type, cfg in GRAPH_DIMENSIONS.items():
            values = parse_multival(row.get(cfg['col']))
            if dim_type == 'subject':
                values = [v for v in values if v in valid_subjects]
            for val in values:
                attr_id = make_id(dim_type, val)
                if attr_id not in nodes:
                    nodes[attr_id] = {
                        'id': attr_id,
                        'l':  val,           # label
                        't':  dim_type,      # type
                        'c':  cfg['color'],  # color
                        'd':  0,             # degree
                    }
                nodes[attr_id]['d'] += 1
                edges.append({'s': item_id, 't': attr_id, 'r': cfg['rel']})

    node_list = list(nodes.values())
    graph = {
        'meta': {
            'source': 'MAMPA - Omeka S Export',
            'items_count': len(df),
            'subject_min_freq': SUBJECT_MIN_FREQ,
            'dimensions': {
                k: {'relation': v['rel'], 'color': v['color']}
                for k, v in GRAPH_DIMENSIONS.items()
            },
        },
        'nodes': node_list,
        'edges': edges,
    }

    # Salida en data/ relativo al proyecto (un nivel arriba de scripts/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, '..', 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'graph.json')

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(graph, f, ensure_ascii=False, separators=(',', ':'))

    type_counts = Counter(n['t'] for n in node_list)
    rel_counts = Counter(e['r'] for e in edges)
    print(f"\nGrafo generado: {len(node_list)} nodos, {len(edges)} aristas")
    for t, c in sorted(type_counts.items()): print(f"  {t}: {c}")
    for r, c in sorted(rel_counts.items()): print(f"  {r}: {c}")
    print(f"\n→ {out_path}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_input = os.path.join(script_dir, '..', 'data', 'export-Omeka-Mampa-ITEMS.xlsx')
    input_file = sys.argv[1] if len(sys.argv) > 1 else default_input
    main(input_file)
