from student.services import get_student_summary
from assessment.services import calculate_final_grade
from engagement.services import engagement_score
from common.s3_helper import save_to_s3

def handler(event, context):
    student_id = event["student_id"]
    
    summary = get_student_summary(student_id)
    grade = calculate_final_grade(student_id)
    eng = engagement_score(student_id)
    
    result = {
        "student": summary,
        "grade": grade,
        "engagement": eng
    }
    
    save_to_s3("processed-results-bucket", f"{student_id}.json", result)
    return result



import pandas as pd
from assessment.models import Assessment
from assessmentservices import AssessmentService

def handler(event, context=None):
    # Example event: carries assessment info + submissions
    assessment_info = event["assessment"]
    submissions = pd.DataFrame(event["submissions"])

    assessment = Assessment(
        id=assessment_info["id"],
        name=assessment_info["name"],
        due_date=pd.to_datetime(assessment_info["due_date"])
    )

    service = AssessmentService(assessment, submissions)

    # Process
    scored_df = service.calculate_time_and_score()
    early_late_summary = service.summarize_early_late_counts(scored_df)
    overall_summary = service.overall_summary(scored_df)

    return {
        "assessment": assessment_info,
        "overall_summary": overall_summary,
        "early_late_summary": early_late_summary.to_dict(orient="records")
    }
