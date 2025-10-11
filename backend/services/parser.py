
import re
from typing import Dict, Optional

STATUS_RE = re.compile(r"Status:\s*(Not Started|In Progress|Blocked|Done)", re.IGNORECASE)
PCT_RE = re.compile(r"Percent(?:\s|\-|_)?complete:\s*(\d{1,3})", re.IGNORECASE)
BLOCKERS_RE = re.compile(r"Blockers?:\s*(.+)", re.IGNORECASE)
ETA_RE = re.compile(r"ETA:\s*([\w\-\/\,\s]+)", re.IGNORECASE)
TASK_RE = re.compile(r"Task:\s*(.+)", re.IGNORECASE)

def parse_status_from_text(text: str) -> Dict[str, Optional[str]]:
    """Attempt rules-first parsing to extract status_label, status_pct, blockers, eta, summary, and task_name."""
    result = {
        'status_label': None,
        'status_pct': None,
        'blockers': None,
        'eta_date': None,
        'summary': None,
        'task_name': None
    }
    if not text:
        return result

    s = text

    # Extract status_label
    m = STATUS_RE.search(s)
    if m:
        result['status_label'] = m.group(1).title()

    # Extract status_pct
    m = PCT_RE.search(s)
    if m:
        try:
            pct = int(m.group(1))
            pct = max(0, min(100, pct))
            result['status_pct'] = pct
        except:
            pass

    # Extract blockers
    m = BLOCKERS_RE.search(s)
    if m:
        result['blockers'] = m.group(1).strip()

    # Extract eta_date
    m = ETA_RE.search(s)
    if m:
        result['eta_date'] = m.group(1).strip()

    # Extract task_name
    m = TASK_RE.search(s)
    if m:
        result['task_name'] = m.group(1).strip()

    # Extract summary
    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    if lines:
        # Prefer a non-template line
        for ln in lines:
            if not ln.lower().startswith(('status:', 'percent', 'blockers:', 'eta:', 'task:')):
                result['summary'] = ln[:500]
                break
        if not result['summary']:
            result['summary'] = lines[0][:500]

    return result
