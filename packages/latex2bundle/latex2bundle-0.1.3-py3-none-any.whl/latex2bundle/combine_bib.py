import logging
import argparse
from pathlib import Path
import re
from typing import Set, Dict, List, Tuple


# Note: logging configuration is done in `main()` so callers can control level


class BibEntry:
    def __init__(self, key: str, entry_text: str, source_path: Path):
        self.key = key
        self.entry_text = entry_text
        self.source_path = source_path

        self.title = self.parse_field('title')

        self.cleaned_title = self.sanitize_field(self.title)
        self.authors = self.parse_field('author')

    # Function to compare by title
    def __lt__(self, other):
        return self.cleaned_title < other.cleaned_title
    
    
    def get_key(self) -> str:
        return self.key
    
    def get_title(self) -> str:
        return self.title
    
    def get_cleaned_title(self) -> str:
        return self.cleaned_title
    
    def parse_field(self, field_name: str) -> str:
        # Robust extraction that supports nested braces and multiline fields
        text = self.entry_text
        # case-insensitive search for the field name followed by '='
        pat = re.compile(rf'(?i){re.escape(field_name)}\s*=')
        m = pat.search(text)
        if not m:
            logging.debug('Field %s not found in entry %s', field_name, self.key)
            return ''
        idx = m.end()
        # skip whitespace
        while idx < len(text) and text[idx].isspace():
            idx += 1
        if idx >= len(text):
            return ''
        ch = text[idx]
        if ch == '{':
            # parse balanced braces
            i = idx + 1
            depth = 1
            start = i
            while i < len(text):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        val = text[start:i].strip()
                        logging.debug('Parsed braced field %s for key %s -> %s', field_name, self.key, (val[:80] + '...' if len(val) > 80 else val))
                        return val
                i += 1
            # fallback: return remainder
            return text[start:].strip()
        elif ch == '"':
            # parse quoted string
            i = idx + 1
            start = i
            while i < len(text):
                if text[i] == '"' and text[i-1] != '\\':
                    val = text[start:i].strip()
                    logging.debug('Parsed quoted field %s for key %s -> %s', field_name, self.key, (val[:80] + '...' if len(val) > 80 else val))
                    return val
                i += 1
            return text[start:].strip()
        else:
            # unbraced value until comma or newline
            m2 = re.match(r'([^,\n]+)', text[idx:])
            val = m2.group(1).strip() if m2 else ''
            logging.debug('Parsed unbraced field %s for key %s -> %s', field_name, self.key, val)
            return val
    
    def sanitize_field(self, content: str) -> str:
        # Remove any curly braces and extra spaces, and line breaks
        content = re.sub(r'[\{\}]', '', content)
        content = re.sub(r'\s+', ' ', content)
        return content.strip().lower()
    
    def get_authors(self) -> str:
        return self.parse_field('author')


def replace_comments(lines: List[str]) -> List[str]:
    return [remove_after_comment(line) for line in lines]

def remove_after_comment(line: str) -> str:
    # Remove comments from a line and replace with '% comment removed'
    comment_index = line.find('%')
    if comment_index != -1:
        return line[:comment_index] + '% comment removed'
    return line


def find_inputs_and_citations(tex_path: Path, visited: Set[Path] = None) -> Tuple[Set[Path], Set[str]]:
    """Recursively scan a tex file for \input/\include commands and citation keys.

    Returns a tuple (set_of_bib_paths, set_of_citation_keys).
    """
    if visited is None:
        visited = set()
    bibs: Set[Path] = set()
    cites: Set[str] = set()

    try:
        tex_path = Path(tex_path).resolve()
    except Exception:
        tex_path = Path(tex_path)

    if tex_path in visited:
        return bibs, cites
    visited.add(tex_path)

    if not tex_path.exists():
        logging.warning(f'Tex file not found: {tex_path}')
        return bibs, cites

    try:
        text = tex_path.read_text()
        logging.debug('Read tex file: %s (%d bytes)', tex_path, len(text))
    except Exception as e:
        logging.warning('Unable to read %s: %s', tex_path, e)
        return bibs, cites

    # remove comments to avoid false positives
    lines = text.splitlines()
    lines = replace_comments(lines)
    text = '\n'.join(lines)

    # find \input{file} and \include{file}
    for m in re.finditer(r'\\(?:input|include)\{([^}]+)\}', text):
        ref = m.group(1).strip()
        ref_path = Path(ref)
        if not ref_path.suffix:
            ref_path = ref_path.with_suffix('.tex')
        candidate = (tex_path.parent / ref_path).resolve()
        if candidate.exists():
            logging.debug('Found included file: %s', candidate)
            sub_bibs, sub_cites = find_inputs_and_citations(candidate, visited)
            bibs.update(sub_bibs)
            cites.update(sub_cites)
        else:
            logging.debug('Included file not found: %s', candidate)

    # find \bibliography{file1,file2}
    for m in re.finditer(r'\\bibliography\{([^}]+)\}', text):
        for part in m.group(1).split(','):
            p = part.strip()
            if not p.endswith('.bib'):
                p = p + '.bib'
            bib_path = (tex_path.parent / p).resolve()
            logging.debug('Found bibliography reference: %s', bib_path)
            bibs.add(bib_path)

    # find \addbibresource[...]{file}
    for m in re.finditer(r'\\addbibresource(?:\[[^\]]*\])?\{([^}]+)\}', text):
        p = m.group(1).strip()
        bib_path = (tex_path.parent / p).resolve()
        logging.debug('Found addbibresource reference: %s', bib_path)
        bibs.add(bib_path)

    # find citation keys \cite{key1,key2}
    for m in re.finditer(r'\\cite[a-zA-Z*]*\{([^}]+)\}', text):
        for key in m.group(1).split(','):
            k = key.strip()
            if k:
                cites.add(k)
                logging.debug('Found citation key in %s: %s', tex_path, k)

    return bibs, cites


def main(argv=None):
    parser = argparse.ArgumentParser(description='Combine multiple .bib files referenced by tex files into one.')
    parser.add_argument('--log-level', '-L', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help='Logging level (default: INFO)')
    parser.add_argument('input_files', nargs='+', help='Input tex files to scan (recursively follows \input and \include)')
    parser.add_argument('-o', '--output', required=False, help='Output .bib file path', default='combined.bib')
    parser.add_argument('--print-conflicts', action='store_true', help='Print detected bib key conflicts')
    parser.add_argument('--print-sorted', choices=['title', 'author', 'key'], help='Print all bib entries sorted by the chosen field')
    args = parser.parse_args(argv)

    # Configure logging according to CLI option so this module can be used in production
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=getattr(logging, args.log_level))

    tex_files = [Path(f).resolve() for f in args.input_files]
    all_bibs: Set[Path] = set()
    all_cites: Set[str] = set()
    for tf in tex_files:
        b, c = find_inputs_and_citations(tf)
        all_bibs.update(b)
        all_cites.update(c)

    logging.info(f'Found {len(all_bibs)} bibliography files and {len(all_cites)} citation keys.')

    bib_entries: Dict[str, BibEntry] = {}
    conflicts: Dict[str, List[BibEntry]] = {}   

    # Read all bib files and parse entries
    for bib_path in all_bibs:
        if not bib_path.exists():
            logging.warning(f'Bibliography file not found: {bib_path}')
            continue
        try:
            text = bib_path.read_text()
            logging.debug('Read bib file: %s (%d bytes)', bib_path, len(text))
        except Exception as e:
            logging.warning(f'Unable to read {bib_path}: {e}')
            continue

        entries = re.split(r'@(?=\w+\s*\{)', text)
        logging.debug('Found %d raw bib entry chunks in %s', len(entries), bib_path)
        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            m = re.match(r'(\w+)\s*\{\s*([^,]+),', entry, flags=re.DOTALL)
            if not m:
                continue
            entry_type = m.group(1)
            entry_key = m.group(2).strip()
            full_entry_text = f'@{entry_type}{{{entry}}}'

            bib_entry = BibEntry(entry_key, full_entry_text, bib_path)
            logging.debug('Parsed bib entry: key=%s source=%s', entry_key, bib_path)
            if entry_key in bib_entries:
                if entry_key not in conflicts:
                    conflicts[entry_key] = [bib_entries[entry_key]]
                conflicts[entry_key].append(bib_entry)
            else:
                bib_entries[entry_key] = bib_entry
    # Handle conflicts
    if args.print_conflicts and conflicts:
        logging.info('Detected bibliography key conflicts:')
        for key, entries in conflicts.items():
            logging.info(f'Key: {key}')
            for e in entries:
                logging.info(f'  From: {e.source_path}')
                logging.info(f'  Title: {e.get_title()}')
                logging.info(f'  Authors: {e.get_authors()}')
            logging.info('')
    

    for entry in bib_entries.values():
        logging.info(f'Including entry: {entry.get_key()} title: "{entry.get_title()}"')

    # Sort entries
    sorted_entries: List[BibEntry] = list(bib_entries.values())
    sorted_entries.sort(key=lambda e: e.cleaned_title)
    for sentry in sorted_entries:
        logging.debug(f'Sorted entry: {sentry.get_key()} title: "{sentry.get_cleaned_title()}"')

    # Deduplicate entries that have the same cleaned title.
    def deduplicate_by_title(entries: Dict[str, BibEntry]) -> Dict[str, str]:
        """Find entries with identical cleaned titles.

        Remove duplicate entries from `entries` (keeps one per title) and return a
        mapping of removed_key -> kept_key.
        """
        title_map: Dict[str, List[str]] = {}
        for key, be in entries.items():
            title = be.get_cleaned_title() or ''
            title_map.setdefault(title, []).append(key)

        replacements: Dict[str, str] = {}
        for title, keys in title_map.items():
            if len(keys) <= 1:
                continue
            # choose a canonical key to keep: prefer lexicographically smallest key
            keys_sorted = sorted(keys)
            keep = keys_sorted[0]
            for k in keys_sorted[1:]:
                replacements[k] = keep
                # remove the duplicate entry
                if k in entries:
                    del entries[k]
        return replacements

    replacements = deduplicate_by_title(bib_entries)
    if replacements:
        logging.info(f'Deduplicated {len(replacements)} entries by title')
        for old, new in replacements.items():
            logging.info(f'Replacing key {old} -> {new}')

    # Update citation keys to point to kept keys
    if replacements:
        updated_cites: Set[str] = set()
        for c in all_cites:
            updated_cites.add(replacements.get(c, c))
        all_cites = updated_cites

    # If there are replacements, apply them to all tex files (including nested inputs)
    if replacements:
        def gather_tex_files(entry_paths: List[Path]) -> Set[Path]:
            """Return a set of all tex files reachable from the given entry tex files via \input/\include."""
            collected: Set[Path] = set()
            stack = [p.resolve() for p in entry_paths]
            seen: Set[Path] = set()
            while stack:
                p = stack.pop()
                if p in seen or not p.exists():
                    continue
                seen.add(p)
                collected.add(p)
                try:
                    txt = p.read_text()
                except Exception:
                    continue
                # remove comments when searching for includes
                lines = replace_comments(txt.splitlines())
                txt2 = '\n'.join(lines)
                for m in re.finditer(r'\\(?:input|include)\{([^}]+)\}', txt2):
                    ref = m.group(1).strip()
                    ref_path = Path(ref)
                    if not ref_path.suffix:
                        ref_path = ref_path.with_suffix('.tex')
                    candidate = (p.parent / ref_path).resolve()
                    if candidate.exists() and candidate not in seen:
                        stack.append(candidate)
            return collected

        def replace_bibkeys_in_tex_files(replacements: Dict[str, str], tex_paths: Set[Path]) -> int:
            """Replace citation keys in all tex files. Returns number of replacements made."""
            total_replacements = 0
            cite_pattern = re.compile(r'\\cite[a-zA-Z*]*\{([^}]+)\}', flags=re.DOTALL)
            for tp in sorted(tex_paths):
                try:
                    original = tp.read_text()
                except Exception:
                    continue
                text = original
                new_text = text
                # iterate matches from end to start to keep replacements stable
                matches = list(cite_pattern.finditer(text))
                for m in reversed(matches):
                    span_start = m.start()
                    # skip if inside a commented region on same line
                    line_start = text.rfind('\n', 0, span_start) + 1
                    before = text[line_start:span_start]
                    # detect unescaped % in 'before'
                    if re.search(r'(?<!\\)%', before):
                        continue
                    keys_text = m.group(1)
                    keys = [k.strip() for k in keys_text.split(',') if k.strip()]
                    new_keys = [replacements.get(k, k) for k in keys]
                    if new_keys != keys:
                        total_replacements += sum(1 for a, b in zip(keys, new_keys) if a != b)
                        replaced = ','.join(new_keys)
                        # build new cite string preserving the cite command prefix
                        prefix = text[m.start():m.start(1)]
                        new_cite = prefix + replaced + '}'
                        # replace in new_text using absolute positions
                        new_text = new_text[:m.start()] + new_cite + new_text[m.end():]
                if new_text != original:
                    try:
                        tp.write_text(new_text)
                        logging.info(f'Updated citations in {tp} ({total_replacements} replacements so far)')
                    except Exception as e:
                        logging.warning(f'Failed to write updated tex file {tp}: {e}')
            return total_replacements

        tex_set = gather_tex_files([Path(p) for p in tex_files])
        num = replace_bibkeys_in_tex_files(replacements, tex_set)
        logging.info(f'Replaced {num} citation keys across {len(tex_set)} tex files')
        # Log the number of updated citation keys per tex file
        for tp in sorted(tex_set):
            logging.debug(f'Updated citations in tex file: {tp.name}')




    


if __name__ == "__main__":
    logging.info('Starting bibliography combination process...')
    main()