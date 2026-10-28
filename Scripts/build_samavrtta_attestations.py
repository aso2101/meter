#!/usr/bin/env python3
"""Turn Velankar's Appendix I (Jayadāman/appendix-I.tsv) into Data/samavrtta-attestations.tsv.

One output row per (meter, name, source).  Columns:
  n, serial, pattern, name, text, locus, edition, yati, source_yati, variant, note, via, raw
n/serial/pattern follow Pratyaya/pratyaya.py; edition is a parenthesised edition mark such as (Nsp) after a locus; yati is Velankar's row-level yati; source_yati a
yati given for one source only, e.g. "(6, 5) Mm. 9. 11" (a number in parentheses before a source
belongs to the source that follows, one after a locus to the source it follows); variant holds
variant readings, "v. l. X" or the letters (a)(b)(c) of Vr. loci; via names the Velankar row
(section.serial); raw is the source fragment as printed, so every normalisation can be checked.
Abbreviations are checked against the table in Texts/OVERVIEW.md.
Problems are printed to stdout and written to Data/samavrtta-problems.txt.
Usage: build_samavrtta_attestations.py [APPENDIX_I.tsv OUT.tsv]
"""
import os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, '..', 'Pratyaya'))
from pratyaya import uddista, GANA

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', 'Jayadāman', 'appendix-I.tsv')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, '..', 'Data', 'samavrtta-attestations.tsv')
PROB = os.path.join(os.path.dirname(OUT), 'samavrtta-problems.txt')
OVERVIEW = os.path.join(here, '..', 'Texts', 'OVERVIEW.md')

ALIAS = {'Vr': 'Vr.', 'vr': 'Vr.', 'Jk': 'Jk.', 'Pp': 'Pp.', 'P': 'P.', 'Rm': 'Rm.', 'Jd': 'Jd.', 'Bh': 'Bh.',
         'Vjs': 'Vjs.', 'Sb': 'Sb.', 'H': 'H.', 'Mm': 'Mm.', 'Ckau': 'Ckau.', 'Cku': 'Ckau.', 'Chm': 'Chm.'}
LETTERS = re.compile(r'ma|ya|ra|sa|ta|ja|bha|na|la|ga')
problems = []
SIGLA, EDITIONS = set(), set()
for l in open(OVERVIEW, encoding='utf8'):
    m = re.match(r'^\|\s*([A-Za-z]+)\s*\|', l)
    if m:
        SIGLA.add(m.group(1))
    m = re.match(r'^\|\s*[A-Za-z]+\s*\(([^)]+)\)\s*\|', l)     # "| Bh (Nsp) | ... edition ..."
    if m:
        EDITIONS.add(re.sub(r'\.?(?: ed\.?)?$', '', m.group(1)))


def pattern_of(defn):
    out = ''
    for tok in defn.split('+'):
        m = re.fullmatch(r'(\d+)\s*(\w+)', tok)       # "10la", "12 na": a count times a gaṇa
        if m:
            out += pattern_of(m.group(2)) * int(m.group(1)); continue
        if ''.join(LETTERS.findall(tok)) != tok:
            raise ValueError(defn)
        out += ''.join(GANA[x] for x in LETTERS.findall(tok))
    return out


def name_text(t):
    return re.sub(r'</?name>', '', t)


NAME = r'<name>[^<]*</name>°?'
# a name group: names (or parenthesised variants containing names) joined by "or" or commas
ITEM = r'(?:%s|\((?:or\s+)?%s(?:[^()<]|%s)*\))' % (NAME, NAME, NAME)
GROUP = re.compile(r'%s(?:\s*(?:,|or)?\s*%s)*' % (ITEM, ITEM))


def split_row(s, via):
    """-> list of (names, group_as_printed, source_string)"""
    s = s.strip()
    # "(v. l. <name>X</name>; ...)": variant readings, not names in their own right
    s = re.sub(r'\([vV]\. l\.[^()]*\)', lambda m: re.sub(r'</?name>', '', m.group(0)).replace(';', ','), s)
    # a name in parentheses straight after a locus: a variant in that source
    s = re.sub(r'(?<=[\d.]) \(<name>([^<]*)</name>\)', r' (var. \1)', s)
    ms = list(GROUP.finditer(s))
    if not ms:
        return [([], '', s)]
    lead = s[:ms[0].start()].strip()
    if lead:
        problems.append('%s: text before first name: %r' % (via, lead))
    out = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(s)
        out.append((re.findall(r'<name>([^<]*)</name>', m.group(0)), m.group(0), s[m.end():end].strip()))
    return out


def letters(c):
    return ','.join(re.findall(r'[a-c]', c))


def classify(c):
    """-> (field, value) for the content of a parenthesis in a source"""
    c = c.strip()
    if re.fullmatch(r'\d+(?:\s*,\s*\d+)*', c):
        return 'source_yati', re.sub(r'\s*,\s*', ',', c)
    if re.fullmatch(r'(?i)no yati', c):
        return 'source_yati', 'none'
    if re.fullmatch(r'Nsp\.?', c):
        return 'edition', 'Nsp'
    if re.fullmatch(r'Gaek\.? ed\.?', c):
        return 'edition', 'Gaek'
    if re.match(r'[vV]\. l\.', c):
        return 'variant', 'v. l.' + c[5:].rstrip()
    if c.startswith('var. '):
        return 'variant', c[5:]
    if re.fullmatch(r'[a-c](?:[\s,.]*[a-c])*[\s.]*', c):
        return 'variant', letters(c)
    return 'note', c


def parse_sources(src, via):
    """-> list of dicts: text, locus, source_yati, variant, note, raw, titled"""
    src = re.sub(r'[;,\s]*\bor\s*$', '', src.strip()).rstrip(';').strip()
    if not src.strip('.;, '):
        return []
    lead = {}
    m = re.match(r'^(\(([^()]*)\)|\?)\s*', src)             # "(6, 5) Mm. 9. 11", "? Haravijaya"
    if m:
        if m.group(1) == '?':
            lead = {'note': 'printed ?'}
        else:
            k, v = classify(m.group(2)); lead = {k: v}
        src = src[m.end():]
    if not src:
        return [dict(text='', locus='', source_yati='', variant='', edition='', note=lead.get('note', ''), raw='', titled=False)] if lead else []
    res, prev, prev_titled = [], None, False
    pieces = [p.strip() for p in re.split(r';|(?<=\d)\.\s+(?=[A-Z])', src) if p.strip()]
    for pc in pieces:
        raw = pc
        titled = '<title>' in pc
        pc = re.sub(r'</?(?:title|name)>', '', pc)
        f = {'source_yati': '', 'variant': '', 'note': '', 'edition': ''}
        for c in re.findall(r'\(([^()]*)\)', pc):
            k, v = classify(c)
            f[k] = (f[k] + '; ' + v) if f[k] else v
        if lead and not res:
            for k, v in lead.items():
                f[k] = (f[k] + '; ' + v) if f[k] else v
        pc = re.sub(r'^Utpala, v\.', 'Utpala v.', pc)
        core = re.sub(r'\([^()]*\)', ' ', pc).replace('--', '-').replace(' - ', '-')
        m = re.match(r'^((?:[A-Za-zŪūṛr̥āīēōṃṅñḥśṣṭḍṇ̀-ͯ]+\.?,?\s*)+?)\s*(?=\d|$)', core)
        text, rest = (m.group(1), core[m.end():]) if m else ('', core)
        text = re.sub(r'[.,\s]+$', '', text.strip())
        text = re.sub(r'[.,\s]+pp?$', '', text)             # "Indische Studien VIII. p. 370"
        rest = re.sub(r'\bpp?\.', '', rest)
        if text in ('v', 'v. l', 'p'):
            text = ''
        if text.startswith('Utpala'):
            text, rest = 'Utpala', 'v. ' + rest
        if re.fullmatch(r'[A-Za-z]{1,5}', text) and not (text.isupper() and len(text) > 1):
            text = text[0].upper() + text[1:] + '.'
        text = ALIAS.get(text, text)
        if not text and prev:
            text, titled = prev, prev_titled
        elif not text:
            problems.append('%s: no text for %r' % (via, pc))
        if text:
            prev, prev_titled = text, titled
        nums = re.findall(r'\d+(?:-\d+)?', rest)
        locus = ('v. ' if rest.startswith('v. ') else '') + '. '.join(nums)
        extra = re.sub(r'^v\.', '', rest.strip())
        extra = re.sub(r'[\d\s.,;-]+', '', extra)
        if extra:
            problems.append('%s: unparsed %r in %r' % (via, extra, pc))
        res.append(dict(text=text, locus=locus, raw=raw, titled=titled, **f))
    return res


rows = []
dupes = []
seen = {}
markup = []
COLS = 'n serial pattern name text locus edition yati source_yati variant note via raw titled'.split()
for ln, line in enumerate(open(SRC, encoding='utf8').read().split('\n'), 1):
    if not line:
        continue
    sec, ser, dfn, yati, names, *rest = line.split('\t')
    rownote = ('Appendix I note: ' + rest[0]) if rest and rest[0] else ''
    via = 'Velankar I %s.%s' % (sec, ser)
    for tag in ('name', 'title'):
        if len(re.findall('<%s>' % tag, names)) != len(re.findall('</%s>' % tag, names)) or \
           re.search(r'<%s>[^<]*</(?!%s)' % (tag, tag), names):
            markup.append('%s: unbalanced <%s> in %r' % (via, tag, names))
    try:
        pat = pattern_of(dfn)
    except ValueError:
        problems.append('%s: cannot read definition %r' % (via, dfn)); continue
    if len(pat) != int(sec):
        problems.append('%s: %d syllables, section %s (%s)' % (via, len(pat), sec, dfn))
    key = (len(pat), uddista(pat))
    if key in seen:
        dupes.append('%s: same pattern as %s (different row, e.g. different yati)' % (via, seen[key]))
    seen[key] = via
    n, serial = key
    for nms, grp, src in split_row(names, via):
        gnote = '' if len(nms) < 2 else 'alternatives: ' + ' / '.join(nms)
        if re.search(r'°|[()-]', grp):
            gnote = (gnote + '; ' if gnote else '') + 'as printed: ' + name_text(grp)
        srcs = parse_sources(src, via) or [dict(text='', locus='', source_yati='', variant='', edition='', note='', raw='', titled=False)]
        for nm in nms or ['']:
            for d in srcs:
                note = '; '.join(x for x in (d['note'], gnote, rownote) if x)
                rows.append(dict(n=n, serial=serial, pattern=pat, name=nm, text=d['text'], locus=d['locus'], edition=d['edition'], yati=yati,
                                 source_yati=d['source_yati'], variant=d['variant'], note=note, via=via, raw=d['raw'],
                                 titled=d['titled']))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf8') as o:
    o.write('\t'.join(COLS[:-1]) + '\n')
    for r in rows:
        o.write('\t'.join(str(r[c]) for c in COLS[:-1]) + '\n')

# ---- problems file
V = lambda r: r['via'].replace('Velankar I ', '')
out = ['REMAINING PROBLEMS in Data/samavrtta-attestations.tsv (written by build_samavrtta_attestations.py)',
       'Row ids are Velankar Appendix I section.serial.', '']
out.append('1. MALFORMED MARKUP in Jayadāman/appendix-I.tsv')
out += ['   ' + m for m in markup] or ['   none']
out += ['', '2. ABBREVIATIONS NOT IDENTIFIED (not in the table in Texts/OVERVIEW.md, and not given as <title>)']
unk = {}
for r in rows:
    if r['text'] and not r['titled'] and r['text'].rstrip('.') not in SIGLA:
        unk.setdefault(r['text'], []).append('%s %s %s' % (V(r), r['name'] or '(unnamed)', r['locus']))
for k, v in sorted(unk.items()):
    out.append('   %s (%d): %s' % (k, len(v), '; '.join(v)))
if not unk:
    out.append('   none')
eds = {}
for r in rows:
    if r['edition'] and r['edition'] not in EDITIONS:
        eds.setdefault(r['edition'], []).append('%s %s %s %s' % (V(r), r['name'], r['text'], r['locus']))
out += ['', '2b. EDITIONS NOT IDENTIFIED (not given as "| Bh (X) |" in Texts/OVERVIEW.md)']
for k, v in sorted(eds.items()):
    out.append('   %s (%d): %s' % (k, len(v), '; '.join(v)))
if not eds:
    out.append('   none')
out += ['', '3. NAMES WITH A SOURCE ABBREVIATION BUT NO LOCUS, OR NO SOURCE AT ALL']
for r in rows:
    if r['name'] and (not r['text'] or not r['locus']):
        out.append('   %s %s: %r (%s)' % (V(r), r['name'], r['raw'], r['variant'] or r['note'] or 'nothing else printed'))
out += ['', '4. FRAGMENTS THE PARSER COULD NOT READ']
out += ['   ' + p for p in problems] or ['   none']
out += ['', '5. UNNAMED ATTESTATIONS (pattern cited from a text, no name printed)']
for r in rows:
    if not r['name']:
        out.append('   %s %s %s%s' % (V(r), r['text'], r['locus'], '  [' + r['note'] + ']' if r['note'] else ''))
out += ['', '6. TO CHECK AGAINST THE TEXTS',
        '   a. Letters (a)(b)(c) on Vr. loci, stored in column "variant" as printed (assumed variant readings of Vr.):']
for r in rows:
    if re.fullmatch(r'[a-c](,[a-c])*', r['variant']):
        out.append('      %s %s Vr. %s (%s)' % (V(r), r['name'], r['locus'], r['variant']))
out.append('   b. Variant readings "v. l." or names in parentheses after a locus (column "variant"):')
for r in rows:
    if r['variant'] and not re.fullmatch(r'[a-c](,[a-c])*', r['variant']):
        out.append('      %s %s %s %s: %s' % (V(r), r['name'], r['text'], r['locus'], r['variant']))
out.append('   c. Yati given for one source only (column "source_yati"); a number in parentheses before a source was assigned to the')
out.append('      source that follows, one after a locus to the source it follows;')
out.append('      the last word says where the number was printed:')
for r in rows:
    if r['source_yati']:
        out.append('      %s %s %s %s: %s   (%s the source)' % (V(r), r['name'], r['text'], r['locus'], r['source_yati'], 'after' if re.search(r'\((?:\d|No)', r['raw']) else 'before'))
out.append('   d. Names given as alternatives ("X or Y Src.", "X (or Y) Src."): both get the source; check the source uses both.')
open(PROB, 'w', encoding='utf8').write('\n'.join(out) + '\n')

counts = {}
for k in seen:
    counts[k[0]] = counts.get(k[0], 0) + 1
print('%d velankar rows, %d attestation rows' % (len(seen), len(rows)))
print('sections complete (all 2^n patterns present):', [n for n in sorted(counts) if counts[n] == 2 ** n])
print(len(dupes), 'patterns listed in more than one Velankar row (merged by key)')
print('problems ->', PROB)
