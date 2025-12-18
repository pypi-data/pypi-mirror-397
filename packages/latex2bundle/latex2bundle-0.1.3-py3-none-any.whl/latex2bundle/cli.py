import re
from pathlib import Path
from typing import List, Tuple, Dict, Union
from shutil import copyfile, rmtree, make_archive
import argparse
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def is_document_class(line: str):
    if line.startswith('\\documentclass'):
        if line.endswith('}'):
            return line.split('{')[1].split('}')[0]


def is_input_cmd(line: str):
    if '\\input{' in line:
        return line.split('\\input{')[1].split('}')[0]


def is_bib_file_include(line: str):
    m = re.search(r'\\bibliography\{([^}]*)\}', line)
    if m:
        return m.group(1)
    m = re.search(r'\\addbibresource(?:\[[^\]]*\])?\{([^}]*)\}', line)
    if m:
        return m.group(1)
    # logging.debug(f'No bibliography include found in line: {line}')


def check_filename(name: str):
    if not name.endswith('.tex'):
        return f'{name}.tex'
    return name


def read_file(path: Path):
    print(f'Opening file: {path}')
    with open(path) as file:
        return file.read()

def extract_citations_from_path(tex_path: Union[Path, str]):
    if isinstance(tex_path, Path):
        tex_path = str(tex_path)
    tex = tex_path.read_text()
    return extract_citations(tex)

def extract_citations(tex_content: str):
    pattern = r'\\cite[a-zA-Z*]*\{([^}]*)\}'
    matches = re.findall(pattern, tex_content)
    
    citations = set()
    for match in matches:
        for key in match.split(','):
            citations.add(key.strip())
    return citations


def extract_bib_keys(bib_path):
    bib = Path(bib_path).read_text()
    pattern = r'@\w+\{([^,]+),'
    return set(re.findall(pattern, bib))


def filter_bib_entries(bib_path: Path, used_keys: set) -> str:
    bib_content = bib_path.read_text()
    entries = re.split(r'@', bib_content)
    filtered_entries = []
    for entry in entries:
        if not entry.strip():
            continue
        key_match = re.match(r'\w+\{([^,]+),', entry)
        if key_match:
            key = key_match.group(1).strip()
            if key in used_keys:
                filtered_entries.append(f'@{entry}')
    return '\n'.join(filtered_entries)




def process(content: str, base_path: Path, verbose: bool = False) -> List[str]:
    new_content = []
    lines = content.split('\n')
    for line in lines:
        
        input_file = is_input_cmd(line)
        if input_file:
            if line.lstrip().startswith('%'):
                # This is a comment; will not include in the main file
                continue

            if verbose:
                logging.info(
                    f'Detected linked tex file: {check_filename(input_file)}')
            file_path = base_path / Path(check_filename(input_file))
            pattern = f'\\input{{{input_file}}}'
            file_contents = read_file(file_path)
            file_lines = process(file_contents, base_path, verbose)
            line = line.replace(pattern, '\n'.join(file_lines))
            new_content += line.split('\n')
        else:
            new_content.append(line)
    return new_content


def find_auxiliary_files(lines: List[str]) -> List[str]:
    aux_files = []
    for l in lines:
        document_template = is_document_class(l)
        if document_template:
            if document_template in ['book', 'report', 'article', 'letter']:
                logging.info(f'Skipping file: {document_template} because it is a standard document class')
                continue
            if not document_template.endswith('.cls'):
                document_template = f'{document_template}.cls'
            aux_files.append(document_template)
        bib_file = is_bib_file_include(l)
        if bib_file:
            if not bib_file.endswith('.bib'):
                bib_file = f'{bib_file}.bib'
            aux_files.append(bib_file)
    return aux_files


def strip_comments(lines: List[str]) -> List[str]:
    lines = [x for x in lines if not x.startswith('%')]
    lines = [re.sub(r'([^\\])(%.*)', r"\1%comment", x) for x in lines]
    return lines


def find_figures(lines: List[str], rename = True) -> Tuple[List[str], Dict[str, str]]:
    text = '\n'.join(lines)
    logging.debug(f'Searching for figures in the document. Renaming figures: {rename}')
    orig_figures = re.findall(r"\\includegraphics.*{([^}]*)}", text)

    
    # Unique
    unique_list = []
    for item in orig_figures:
        if item not in unique_list:
            unique_list.append(item)
    mapped = {}
    for idx, item in enumerate(unique_list):
        p = Path(item)
        if not rename:
            new_name = p.name
        else:
            new_name = f'FIG{idx+1}' + p.suffix
        new_path = f'figures/{new_name}'
        mapped[str(p)] = new_path

    for item in orig_figures:
        pattern = rf"(\\includegraphics.*){{({re.escape(item)})}}"
        new_name = mapped[item]
        text = re.sub(pattern, rf"\1{{{new_name}}}", text)
    return text.split('\n'), mapped


def run(main_tex_file: Path, target_dir : Union[Path, None] = None, copy_files=None, verbose: bool = False, no_reduce_bib: bool = False, no_rename_figures: bool = False, mode: str = 'both'):
    if copy_files is None:
        copy_files = []
    base_path = main_tex_file.parent
    print(f'{base_path.absolute()=};')
    if target_dir is not None:
        out_dir = target_dir / base_path.name
    else:
        out_dir = base_path / base_path.name
    if out_dir.exists():
        rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file_path = out_dir / main_tex_file.name
    last_line_is_empty = False
    with open(main_tex_file) as file:
        data = file.read()
        lines = process(data, base_path, verbose)
        lines = strip_comments(lines)
        aux_files = find_auxiliary_files(lines)
        aux_files += copy_files
        lines = strip_comments(lines)
        lines, graphics_mapping = find_figures(lines, no_rename_figures)

        def del_suc_empty_lines(x: str):
            nonlocal last_line_is_empty
            if x:
                last_line_is_empty = False
                return True
            if last_line_is_empty:
                return False
            last_line_is_empty = True
            return True
        lines = filter(del_suc_empty_lines, lines)

        new_data = '\n'.join(lines)

        with open(out_file_path, 'w+') as out_file:
            out_file.write(new_data)

        for orig_name, new_name in graphics_mapping.items():
            src_path = base_path / orig_name
            dest_path = out_dir / new_name
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            copyfile(src_path, dest_path)
        if verbose:
            logging.info(f'Copied {len(graphics_mapping)} figures')

        for aux_file in aux_files:
            aux_path = base_path / aux_file
            aux_dest = out_dir / aux_file


            # Check if file is bib file
            if not no_reduce_bib and aux_file.endswith('.bib'):
                logging.info(f'Processing bibliography file: {aux_file}')
                tex_cites = extract_citations(new_data)
                bib_keys = extract_bib_keys(base_path / aux_file)

                used = tex_cites & bib_keys
                unused = bib_keys - tex_cites
                missing = tex_cites - bib_keys

                logging.info(f'Num used citations: {len(used)}, Num unused citations: {len(unused)}, Num missing citations: {len(missing)}.')

                # Filter bib file
                filtered_bib_content = filter_bib_entries(
                    base_path / aux_file, used_keys=used)
                
                logging.info(f'Writing filtered bibliography to: {aux_dest}')
                with open(aux_dest, 'w+') as bib_out:
                    bib_out.write(filtered_bib_content)

                # exit()
            else:
                logging.info(f'Copying file: {aux_file}')
                copyfile(aux_path, aux_dest)
                if verbose:
                    logging.info(f'Copied file: {aux_file}')
    # archive_path = out_dir.parent / main_tex_file.stem
    archive_path = out_dir.parent / (main_tex_file.parent.name + '')
    logging.info(f'Archive path: {archive_path}')
    logging.info(f'Output directory: {out_dir}')
    if not archive_path.exists():
        logging.error(f'Output directory does not exist: {out_dir}')


    # Validate mode
    if mode not in ("zip-only", "bundle-only", "both"):
        raise ValueError(f"Invalid mode: {mode}. Expected 'zip-only', 'bundle-only' or 'both'.")

    # Create zip if requested
    if mode in ("zip-only", "both"):
        logging.info(f'Creating zip archive at: {archive_path}.zip')
        make_archive(str(archive_path), 'zip', out_dir)

    # If zip-only, remove the bundle directory and leave only the zip
    if mode == "zip-only":
        if out_dir.exists():
            rmtree(out_dir)

    project_files_log = f'Cleaned project files at: {out_dir}'
    zip_file_log = f'Zip file created at: {archive_path}.zip'

    if mode == "bundle-only":
        if verbose:
            logging.info(project_files_log)
        else:
            print(project_files_log)
    elif mode == "zip-only":
        if verbose:
            logging.info(zip_file_log)
        else:
            print(zip_file_log)
    else:  # both
        if verbose:
            logging.info(project_files_log)
            logging.info(zip_file_log)
        else:
            print(project_files_log)
            print(zip_file_log)


def main():
    parser = argparse.ArgumentParser('Some description')
    parser.add_argument(
        'file', help='The main latex file of the paper/journal')
    parser.add_argument('-c', '--copy-files', nargs='+',
                        help='<Required> Set flag', required=False, default=[])
    parser.add_argument('-v', dest='verbose', action='store_true')

    # Give target location to copy files to
    parser.add_argument('-t', '--target-dir', dest='target_dir', type=Path, default=None, help='Target directory to copy auxiliary files to')

    # Add toggle to reduce bib file to only used entries; default is yes
    parser.add_argument('--no-reduce-bib', dest='no_reduce_bib', action='store_false', default=False, help='Reduce bibliography to only used entries (default: True)')

    # Add toggle to not rename figures; default is to rename
    parser.add_argument('--no-rename-figures', dest='no_rename_figures', action='store_false', default=True, help='Do not rename figures (default: False)')

    # Mode: zip-only, bundle-only, or both
    parser.add_argument('--mode', dest='mode', choices=['zip-only', 'bundle-only', 'both'], default='both', help='What to produce: zip-only, bundle-only, or both (default: both)')

    args = parser.parse_args()
    run(Path(args.file), args.target_dir, args.copy_files, args.verbose, args.no_reduce_bib, args.no_rename_figures, args.mode)
