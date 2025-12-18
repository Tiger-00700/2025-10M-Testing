#!/usr/bin/env python3
from pathlib import Path
import re
from difflib import unified_diff
ROOT = Path(__file__).resolve().parent.parent
fr = (ROOT / 'framework' / '第7篇-专家篇-趋势与平台化.md').read_text(encoding='utf-8')
bk = (ROOT / 'book' / '1208.2025.newbook.update.md').read_text(encoding='utf-8')
bm = re.compile(r"<!--\s*BEGIN\s*第7篇\s*-->")
em = re.compile(r"<!--\s*END\s*第7篇\s*-->")
mb = bm.search(bk)
me = em.search(bk)
if not mb or not me:
    print('Markers not found')
    raise SystemExit(1)
block = bk[mb.end():me.start()]
ndiff = list(unified_diff(fr.splitlines(), block.splitlines(), lineterm=''))
print('\n'.join(ndiff))
print('\nDiff lines count:', len(ndiff))
