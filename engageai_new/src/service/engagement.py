from models import engagement

def engagement_score(eng: engagement) -> float:
    """
    Calculate an engagement score for a student.
    You can adjust the weights based on importance.
    """
    # Example scoring formula
    score = (
        (eng.login_count * 0.2) +
        (eng.forum_posts * 0.3) +
        (eng.video_minutes_watched / 60 * 0.5)  # convert minutes to hours
    )
    return round(score, 2)


def engagement_summary(eng: engagement) -> dict:
    """
    Return a summary dictionary for reporting or saving to S3.
    """
    return {
        "student_id": eng.student_id,
        "login_count": eng.login_count,
        "forum_posts": eng.forum_posts,
        "video_minutes_watched": eng.video_minutes_watched,
        "engagement_score": engagement_score(eng)
    }
