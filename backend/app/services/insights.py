from datetime import datetime, timedelta

def generate_summary(tasks):
    now = datetime.utcnow()
    start_of_week = now - timedelta(days=now.weekday())
    start_of_month = now.replace(day=1)

    total_tasks = len(tasks)
    completed_tasks = [t for t in tasks if t.completed]
    active_tasks = [t for t in tasks if not t.completed]
    overdue_tasks = [t for t in tasks if not t.completed and t.due_date and t.due_date < now]

    completed_this_week = [
        t for t in completed_tasks
        if t.due_date and t.due_date >= start_of_week
    ]
    completed_this_month = [
        t for t in completed_tasks
        if t.due_date and t.due_date >= start_of_month
    ]

    completion_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0

    return {
        "total_tasks": total_tasks,
        "completed_tasks": len(completed_tasks),
        "active_tasks": len(active_tasks),
        "overdue_tasks": len(overdue_tasks),
        "completion_rate": round(completion_rate, 1),
        "completed_this_week": len(completed_this_week),
        "completed_this_month": len(completed_this_month),
    }

