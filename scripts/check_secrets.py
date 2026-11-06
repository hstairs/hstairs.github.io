"""Reject credential-shaped values in tracked files without printing any values."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = {
    'Google API key': re.compile(rb'AIza[0-9A-Za-z_-]{35}'),
    'GitHub token': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{60,255})\b'),
    'Private key': re.compile(rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----'),
}

def check():
    names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).split(b'\0')
    problems=[]
    for name in names:
        if not name:continue
        path=ROOT/name.decode()
        if not path.is_file():continue
        data=path.read_bytes()
        for label,pattern in PATTERNS.items():
            if pattern.search(data):problems.append((name.decode(),label))
    for path,label in problems:print(f'FAIL: {label} pattern in {path}')
    if problems:return 1
    print('PASS: no credential patterns found in tracked files.')
    return 0

if __name__=='__main__':sys.exit(check())
