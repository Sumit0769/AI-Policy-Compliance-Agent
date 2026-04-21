from typing import Dict, List
from rag.retriever import ComplianceRetriever
from agents.risk_classifier import RiskClassifier
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate

class ComplianceReasoner:
    """
    Core reasoning engine for AI Policy & Compliance Agent.
    Uses vectorless RAG (PageIndex) for deterministic retrieval.
    """

    def __init__(self):
        self.retriever = ComplianceRetriever()
        self.risk_classifier = RiskClassifier()
        self.llm=ChatOllama(model="llama3.2:1b", temperature=0.2)

    # -------------------------
    # MAIN ENTRY POINT
    # -------------------------
    def build_citation_context(self,obligations: List[Dict]) -> str:
        context_block=[]
        for i,o in enumerate(obligations[:5]):
            citation=f"{o["law"]} {o.get('article','')}"

            block=f"""
                  [Source{i+1}]
                  Law:{citation}
                  Type:{o['obligation_type']}
                  Text:{o['text'][:200]}"""
            context_block.append(block)
        return "\n".join(context_block)
    
    def llm_explanation(self, user_input: str, risk_category: str, obligations: List[Dict], gaps: List[str]) -> str:
        context=self.build_citation_context(obligations)
        
        prompt=ChatPromptTemplate.from_messages([
            ("system", """You are an AI compliance expert specializing in GDPR, EU AI ACt, and global AI regulation.
            Your task:
             -Analyze the AI system
             -Explain why it falls under a specific risk category
             -Explain key obligations clearly
             -Highlight compliance gaps
             -Give practical insights
            
            STRICT RULES:
            - Only use provided sources
            - ALWAYS cite sources like [Source 1], [Source 2]
            - Do NOT invent laws
            - Be precise and professional
             
            OUTPUT STRUCTURE:
            1. Risk Explanation
            2. Obligations (with citations)
            3. Compliance Gaps (with citations)
            4. Recommendations
            
              Keep it:
             -Claer
             -Professional
             -Concise
             -No hallucinations(only use provided context)"""),
             ("human",f"""AI System: {user_input}
                          Risk Category: {risk_category}
                          Legal Context: {context}
                          Indentified Gaps:{gaps}
                        Generate a clear compliance explanation based on the above information.""")
                        ])
        response=self.llm.invoke(prompt)
        return response.content
    
    def analyze(self, user_input: str) -> Dict:
        """
        Analyze user AI system for compliance.
        """

        # Step 1: Identify risk category
        risk_category = self.risk_classifier.classify(user_input)

        # Step 2: Retrieve relevant legal chunks
        retrieved_chunks = self._retrieve_legal_context(user_input, risk_category)

        # Step 3: Extract obligations
        obligations = self._extract_obligations(retrieved_chunks)

        # Step 4: Identify gaps
        gaps = self._identify_gaps(user_input, obligations)

        # Step 5: Generate explanation
        llm_explanation = self._llm_explanation(
                            user_input,
                            risk_category,
                            obligations,
                            gaps)
                                


        return {
            "risk_category": risk_category,
            "applicable_laws": self._extract_laws(retrieved_chunks),
            "obligations": obligations,
            "compliance_gaps": gaps,
            "explanation": llm_explanation
        }

    # -------------------------
    # RETRIEVAL
    # -------------------------
    def _retrieve_legal_context(self, query: str, risk_category: str):
        results = self.retriever.retrieve(
            query=query,
            top_k=10
        )

        # Optional filtering by risk category
        if risk_category:
            results = [
                r for r in results
                if r["metadata"].get("risk_category") == risk_category
                or r["metadata"].get("risk_category") is None
            ]

        return results

    # -------------------------
    # OBLIGATION EXTRACTION
    # -------------------------
    def _extract_obligations(self, chunks: List[Dict]):
        obligations = []

        for chunk in chunks:
            meta = chunk["metadata"]

            obligations.append({
                "law": meta.get("law"),
                "article": meta.get("article") or meta.get("section"),
                "obligation_type": meta.get("obligation_type"),
                "text": chunk["text"]
            })

        return obligations

    # -------------------------
    # GAP ANALYSIS
    # -------------------------
    def _identify_gaps(self, user_input: str, obligations: List[Dict]):
        gaps = []

        user_text = user_input.lower()

        for obligation in obligations:
            if obligation["obligation_type"] == "Transparency":
                if "explain" not in user_text:
                    gaps.append("Missing transparency / explainability measures")

            if obligation["obligation_type"] == "Risk Management":
                if "risk" not in user_text:
                    gaps.append("No clear risk management process defined")

            if obligation["obligation_type"] == "Human Oversight":
                if "human" not in user_text:
                    gaps.append("No human oversight mentioned")

        return list(set(gaps))  # remove duplicates

    # -------------------------
    # LAW EXTRACTION
    # -------------------------
    def _extract_laws(self, chunks):
        return list(set([c["metadata"].get("law") for c in chunks]))

    # -------------------------
    # EXPLANATION GENERATION
    # -------------------------
    def _generate_explanation(
        self,
        user_input: str,
        risk_category: str,
        obligations: List[Dict],
        gaps: List[str]
    ) -> str:

        explanation = f"\nAI System Analysis:\n{user_input}\n\n"

        explanation += f"Risk Category: {risk_category}\n\n"

        explanation += "Key Obligations:\n"
        for o in obligations[:5]:  # limit for readability
            explanation += f"- ({o['law']}) {o['obligation_type']}: {o['text'][:120]}...\n"

        explanation += "\nCompliance Gaps:\n"
        if gaps:
            for g in gaps:
                explanation += f"- {g}\n"
        else:
            explanation += "No major gaps detected.\n"

        explanation += "\nConclusion:\n"
        explanation += "The system requires alignment with the above obligations to ensure regulatory compliance."

        return explanation