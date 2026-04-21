from typing import Dict, List


class ReportGenerator:
    """
    Generates structured compliance reports from reasoning output.
    """

    # -------------------------
    # MAIN ENTRY
    # -------------------------
    def generate(self, analysis_result: Dict, user_input: str) -> Dict:
        """
        Returns both structured JSON + formatted report
        """

        report = {
            "system_description": user_input,
            "risk_category": analysis_result["risk_category"],
            "applicable_laws": analysis_result["applicable_laws"],
            "obligations": analysis_result["obligations"],
            "compliance_gaps": analysis_result["compliance_gaps"],
            "recommendations": self._generate_recommendations(
                analysis_result["compliance_gaps"]
            ),
            "final_verdict": self._generate_verdict(
                analysis_result["compliance_gaps"]
            ),
            "llm_explanation": analysis_result["explanation"]
        }

        formatted_report = self._format_markdown(report)

        return {
            "json": report,
            "markdown": formatted_report
        }

    # -------------------------
    # RECOMMENDATIONS
    # -------------------------
    def _generate_recommendations(self, gaps: List[str]) -> List[str]:
        recommendations = []

        for gap in gaps:
            if "transparency" in gap.lower():
                recommendations.append(
                    "Implement explainable AI mechanisms and user disclosures."
                )

            elif "risk" in gap.lower():
                recommendations.append(
                    "Establish a formal risk management framework."
                )

            elif "human oversight" in gap.lower():
                recommendations.append(
                    "Introduce human-in-the-loop validation processes."
                )

            else:
                recommendations.append(
                    "Review regulatory requirements and align system accordingly."
                )

        if not recommendations:
            recommendations.append(
                "Maintain continuous monitoring and compliance auditing."
            )

        return list(set(recommendations))

    # -------------------------
    # FINAL VERDICT
    # -------------------------
    def _generate_verdict(self, gaps: List[str]) -> str:
        if not gaps:
            return "COMPLIANT"

        if len(gaps) <= 2:
            return "PARTIALLY COMPLIANT"

        return "NON-COMPLIANT"

    # -------------------------
    # MARKDOWN FORMATTER
    # -------------------------
    def _format_markdown(self, report: Dict) -> str:
        md = f"# 🛡 AI Compliance Report\n\n"

        md += f"## 📌 System Overview\n"
        md += f"{report['system_description']}\n\n"

        md += f"## ⚠ Risk Classification\n"
        md += f"**{report['risk_category']}**\n\n"

        md += f"## 📚 Applicable Laws\n"
        for law in report["applicable_laws"]:
            md += f"- {law}\n"

        md += "\n## 📋 Key Obligations\n"
        for o in report["obligations"][:5]:
            md += f"- **{o['law']} ({o.get('article')})**: {o['obligation_type']}\n"

        md += "\n## 🚨 Compliance Gaps\n"
        if report["compliance_gaps"]:
            for g in report["compliance_gaps"]:
                md += f"- {g}\n"
        else:
            md += "No major gaps detected.\n"

        md += "\n## ✅ Recommendations\n"
        for r in report["recommendations"]:
            md += f"- {r}\n"

        md += "\n## 🏁 Final Verdict\n"
        md += f"**{report['final_verdict']}**\n"

        md+= "\n## 🧠 AI Explanation\n"
        md += report['llm_explanation']+"\n"

        return md