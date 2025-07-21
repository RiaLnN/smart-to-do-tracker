def generate_summary(tasks):
    # Group tasks by day, completion time, etc
    completed = [t for t in tasks if t.completed]
    return f"You completed {len(completed)} tasks this week!"

# Later, you can integrate OpenAI:
# import openai
# def generate_ai_summary(...): ...
