def enrich_document(doc):
    text = doc.page_content.lower()

    doc.metadata["obligation_type"] = infer_obligation(text)
    doc.metadata["risk_category"] = infer_risk(text)
    doc.metadata["applies_to"] = infer_actor(text)

    return doc


def infer_obligation(text):
    if "consent" in text:
        return "User Rights"
    if "record" in text or "log" in text:
        return "Record Keeping"
    if "risk" in text:
        return "Risk Management"
    if "oversight" in text:
        return "Human Oversight"
    if "transparen" in text:
        return "Transparency"
    return "Data Governance"


def infer_risk(text):
    if "biometric" in text:
        return "Unacceptable Risk"
    if "credit scoring" in text or "profiling" in text:
        return "High Risk"
    return None


def infer_actor(text):
    actors = []
    if "controller" in text:
        actors.append("Controller")
    if "processor" in text:
        actors.append("Processor")
    if not actors:
        actors.append("General")
    return actors
