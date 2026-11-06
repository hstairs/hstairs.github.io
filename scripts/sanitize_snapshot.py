"""Remove third-party runtime scripts and credential-shaped strings from snapshots."""
import re

GOOGLE_API_KEY = re.compile(rb'AIza[0-9A-Za-z_-]{35}')
SCRIPTS = re.compile(rb'<script\b[^>]*>.*?</script\s*>', re.I | re.S)

def sanitize_snapshot(data):
    # Snapshot files are evidence of visible content, not runnable copies of Sites.
    # Encoded data-code attributes (including the original News) remain intact.
    clean=GOOGLE_API_KEY.sub(b'[REDACTED_GOOGLE_API_KEY]', SCRIPTS.sub(b'', data))
    return b'\n'.join(line.rstrip() for line in clean.split(b'\n'))
