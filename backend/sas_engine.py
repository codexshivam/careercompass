"""
SAS Model Execution Engine
Evaluates the SAS Decision Tree / Logistic Regression model derived from SAS Viya.
"""
import math

def score_record(dashboard: float, maths: float, ai_ml: float, big_data: float, coding: float) -> float:
    """
    SAS In-Database / In-Memory Scoring Logic
    Computes exact probability of high promotion hike (P_salary_hike_high_or_low1)
    """
    z = (
        -26.2236
        + 1.8210 * maths
        + 1.3547 * dashboard
        + 1.2639 * ai_ml
        + 0.9961 * big_data
        + 0.6090 * coding
    )
    # Logistic link function 1 / (1 + exp(-z))
    return 1.0 / (1.0 + math.exp(-z))


def evaluate_promotion(dashboard: float, maths: float, ai_ml: float, big_data: float, coding: float):
    """
    Runs the full model inference, maps to verdict zones, and computes Upskilling ROI.
    """
    prob = score_record(dashboard, maths, ai_ml, big_data, coding)
    percentage = int(round(prob * 100))

    if percentage >= 70:
        verdict = "High Likelihood Zone (>= 70%)"
    elif percentage >= 40:
        verdict = "Moderate Competitive Zone (40-69%)"
    else:
        verdict = "Low Probability Zone (< 40%)"

    # Compute Upskilling ROI: test +0.5 increment on each competency
    competencies = [
        ("Dashboard & Storytelling", dashboard, "dash"),
        ("Maths & Statistical Rigor", maths, "math"),
        ("AI & Machine Learning", ai_ml, "aiml"),
        ("Big Data Architecture", big_data, "big"),
        ("Core Programming (Python/SQL/SAS)", coding, "code"),
    ]

    scores = [dashboard, maths, ai_ml, big_data, coding]
    best_delta = 0
    best_skill = None

    for i, (name, val, _) in enumerate(competencies):
        if val < 5.0:
            hypo = list(scores)
            hypo[i] = min(5.0, val + 0.5)
            hypo_prob = score_record(hypo[0], hypo[1], hypo[2], hypo[3], hypo[4])
            delta = int(round(hypo_prob * 100)) - percentage
            if delta > best_delta:
                best_delta = delta
                best_skill = name

    return {
        "probability": prob,
        "percentage": percentage,
        "verdict": verdict,
        "roi_skill": best_skill,
        "roi_delta": best_delta,
        "source": "sas_score_engine"
    }
