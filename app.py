from fastapi import FastAPI
from pydantic import BaseModel

from agents.compliance_reasoner import ComplianceReasoner
from agents.report_generator import ReportGenerator


app = FastAPI(
    title="AI Policy & Compliance Agent",
    description="Analyze AI systems for regulatory compliance",
    version="1.0"
)

reasoner = ComplianceReasoner()
report_gen = ReportGenerator()


# -------------------------
# REQUEST SCHEMA
# -------------------------
class ComplianceRequest(BaseModel):
    system_description: str


# -------------------------
# HEALTH CHECK
# -------------------------
@app.get("/")
def root():
    return {"message": "AI Compliance Agent is running 🚀"}


# -------------------------
# MAIN ENDPOINT
# -------------------------
@app.post("/analyze")
def analyze_system(request: ComplianceRequest):

    user_input = request.system_description

    # Step 1: Analyze
    analysis = reasoner.analyze(user_input)

    # Step 2: Generate report
    report = report_gen.generate(analysis, user_input)

    return {
        "analysis": analysis,
        "report": report
    }