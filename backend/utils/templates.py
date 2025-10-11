from datetime import datetime

def task_assignment_template(task, consultants, last_update=None):
    subject = f"[Task: {task.name}] {task.status_pct}% – Update requested by {datetime.utcnow().date()}"
    body_lines = [
        f"Task: {task.name}",
        f"Start → End: {task.start_date} → {task.end_date}",
        f"Current status: {task.status} ({task.status_pct}%)",
        f"Assignee(s): {', '.join([c.name for c in consultants])}",
        f"Last updated: {task.last_updated_at}",
        "\nPrevious update (for context):",
    ]
    if last_update:
        body_lines += [
            f"Status: {last_update.status_label} ({last_update.status_pct}%)",
            f"Blockers: {last_update.blockers}",
            f"ETA: {last_update.eta_date}",
        ]
    else:
        body_lines += ["No previous update found."]

    body_lines += [
        "\nPlease reply with (copy/paste):",
        "Status: <Not Started|In Progress|Blocked|Done>",
        "Percent complete: <0-100>",
        "Blockers: <text or 'None'>",
        "ETA: <date or 'N/A'>",
        "Notes: <free text>",
    ]

    body = "\n".join(body_lines)
    return subject, body
