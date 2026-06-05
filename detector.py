# backend/detector.py
import re
from ml_model import JobClassifier

# Global runtime instance of ML classifier
ml_engine = JobClassifier()

# Scam DNA Templates (Structural Signatures of Fraud)
SCAM_DNA_PATTERNS = [
    r"(?=.*whatsapp)(?=.*earn)(?=.*(daily|weekly|hours))",
    r"(?=.*no experience)(?=.*urgent hiring)(?=.*income)",
    r"(?=.*part time)(?=.*simple online task)(?=.*pay)"
]

def analyze_job(title, company, salary, email, description):
    # Layer 0: Gibberish Validation
    combined_input = f"{title} {company} {description}"
    if len(combined_input.strip()) < 15 or len(set(combined_input.split())) < 3:
        return "SCAM", 100.0, ["Gibberish input or insufficient data provided."]

    flags = []
    scam_score = 0.0
    
    # Layer 1: Machine Learning Model
    ml_pred, ml_conf = ml_engine.predict(description)
    if ml_pred == 1:
        flags.append(f"ML Classifier flags text pattern as suspicious ({ml_conf}% confidence)")
        scam_score += 35.0

    # Layer 2: Keyword-Based Detection
    scam_keywords = ["whatsapp", "telegram", "urgent hiring", "no experience", "guaranteed", "work from home", "daily pay", "income potential"]
    found_keywords = [w for w in scam_keywords if w in description.lower() or w in title.lower()]
    if found_keywords:
        flags.append(f"Suspicious terminology found: {', '.join(found_keywords)}")
        scam_score += 20.0

    # Layer 3: Free Email Provider Screening
    free_domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "rediffmail.com"]
    email_domain = email.split('@')[-1].lower() if "@" in email else ""
    if email_domain in free_domains:
        flags.append(f"Recruiter uses public webmail host ({email_domain}) instead of corporate domain.")
        scam_score += 15.0

    # Layer 4: Salary Anomaly Evaluation
    try:
        numeric_salary = float(re.sub(r'[^\d.]', '', str(salary)))
        # Outlier tracking checks (e.g. > 5 Million monthly or < 1000)
        if numeric_salary > 5000000 or (0 < numeric_salary < 1000):
            flags.append(f"Salary parameter ({salary}) flagged as financial outlier.")
            scam_score += 15.0
    except ValueError:
        pass # Handle case where salary is a non-numeric string descriptor

    # Layer 5: DNA Structural Fingerprinting
    for pattern in SCAM_DNA_PATTERNS:
        if re.search(pattern, description.lower()):
            flags.append("DNA Fingerprint Match: Layout mimics known high-frequency forward templates.")
            scam_score += 15.0
            break

    # Determine final outcome verdict
    final_score = min(scam_score, 100.0)
    verdict = "SCAM" if (final_score >= 40.0 or len(flags) >= 2) else "SAFE"
    
    if not flags:
        flags.append("Passed all evaluation layer filters clean.")
        final_score = 0.0

    return verdict, final_score, flags