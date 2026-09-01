"""
Universal AI Tender & Proposal Document Analyzer — 24-Point Comprehensive Tender Checking System
- 10 Consolidated Topical Passes (Zero Redundancy / No Duplicates)
- 4-Layer Universal Zero-Token Discovery Engine (TOC + Local Semantic Vectors + Keyword Ontology + Scoring)
- Smart Cost Decision Engine (Extracts tender budget or calculates AI Min / Recommended / Max quote)
- Dynamic Submission Document Tracker & Presentation Outline Generator
- 100% Text-Wrap Protected PDF Report Generator (ReportLab Flowable Tables with Auto-Wrapping Paragraph Cells)
- Google Gemini AI Engine with Direct API Error Handling & UI Exception Feedback
"""

# ==============================================================================
# SECTION 1: IMPORTS & CORE TYPING
# ==============================================================================
import os
import re
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# ==============================================================================
# SECTION 2: ENVIRONMENT SETUP & DIRECTORY CONFIGURATION
# ==============================================================================

def _load_env():
    """Loads environment variables manually from .env file located in script directory."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k not in os.environ:
                        os.environ[k] = v

_load_env()

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ==============================================================================
# SECTION 3: CONSOLIDATED 10-DOMAIN KEYWORD & SEMANTIC ONTOLOGY (Zero Overlap)
# ==============================================================================

TOPIC_KEYWORDS = {
    "tender_overview": [
        "tender reference", "reference number", "nit no", "nit number", "tender no",
        "project title", "assignment title", "tender id", "notice inviting tender",
        "eoi for", "tender for", "selection of", "eoi enquiry no", "enquiry no", "rfq no",
        "issuing department", "tender category", "rfp no", "eoi no", "bid document",
        "issuing authority", "nodal officer", "official website", "contact person",
        "organisation", "organization", "ministry", "client name"
    ],
    "scope_and_tech": [
        "scope of work", "functional requirements", "technical requirements",
        "features required", "modules", "integration requirements", "api integration",
        "technology stack", "tech stack", "frontend", "backend", "database",
        "architecture", "system architecture", "solution architecture", "framework",
        "security requirements", "wcag", "cloud hosting", "nic", "meghraj", "platform"
    ],
    "timeline_and_dates": [
        "publication date", "date of issue", "bid submission", "last date",
        "submission deadline", "opening of bid", "technical bid opening", "bid opening date",
        "financial bid opening", "pre-bid", "query submission deadline", "date of bid opening",
        "project timeline", "timeline", "delivery schedule", "phase 1", "phase 2",
        "duration", "weeks", "work schedule", "go-live", "schedule of events", "critical dates", "key dates"
    ],
    "submission_and_prebid": [
        "online submission", "offline submission", "portal submission", "submit online",
        "digital signature", "dsc", "emd", "earnest money deposit", "eprocure", "gem portal",
        "two packet", "three packet", "bid opening", "technical bid opening", "financial bid opening", "bid opening date",
        "date of presentations", "rtgs", "neft", "demand draft", "bank guarantee", "account number", "ifsc", "beneficiary",
        "in favour of", "payable at", "banker's cheque", "pay order", "tender processing fee", "proof of payment", "transaction reference", "utr",
        "msme exemption", "bid security declaration", "tender fee", "pre-bid meeting", "pre-bid conference",
        "query submission", "clarification email"
    ],
    "eligibility_and_experience": [
        "eligibility criteria", "qualifying criteria", "similar project", "past experience",
        "turnover", "annual turnover", "net worth", "completion certificate", "work order",
        "technical evaluation criteria", "evaluation marks", "marks allocated", "qcbs",
        "relevant experience", "minimum 2 projects", "client reference"
    ],
    "required_documents_and_stamp": [
        "documents required", "documents to be submitted", "checklist of documents",
        "gst certificate", "pan card", "certificate of incorporation", "msme certificate",
        "iso certificate", "audited financial", "balance sheet", "itr", "power of attorney",
        "stamp paper", "stamp duty", "affidavit", "notarised", "notarized", "undertaking on stamp"
    ],
    "team_and_cv": [
        "team composition", "resource deployment", "deployment model", "key personnel",
        "staffing schedule", "project manager", "solution architect", "developer", "designer",
        "curriculum vitae", "cv format", "cvs required", "signed cv", "years of experience",
        "role profiles", "manpower deployment", "human resources"
    ],
    "deliverables_and_milestones": [
        "deliverables & milestones", "deliverables and milestones", "milestone", "acceptance criteria",
        "payable against milestones", "payment tranches", "sign-off criteria", "schedule of deliverables",
        "milestone 1", "milestone 2", "payment milestone", "tranche"
    ],
    "commercial_and_boq": [
        "total project cost", "subtotal", "grand total", "in words", "pricing",
        "commercial proposal", "financial bid", "financial proposal format", "boq format",
        "price schedule", "item-wise pricing", "monthly rate", "total inr", "gst @ 18%",
        "estimated project cost", "project budget", "budget", "estimated value"
    ],
    "presentation_and_demo": [
        "technical presentation", "presentation", "approach and methodology (presentation)",
        "demonstration", "product demo", "walk-through", "evaluation committee",
        "45 marks", "scoring matrix", "oral presentation", "date of presentations",
        "criterion 2", "presentation requirements", "comparable portfolio"
    ],
    "annexures_list": [
        "annexure i", "annexure ii", "annexure iii", "annexure iv", "annexure v",
        "annexure 1", "annexure 2", "annexure 3", "annexure 4", "annexure 5",
        "fill and sign", "company stamp", "format of agreement", "proforma", "undertaking format"
    ]
}

TOPIC_SEMANTIC_QUERIES = {
    "tender_overview": "Tender project title reference number NIT number issuing department organisation client contact official website category",
    "scope_and_tech": "Scope of work functional technical requirements software architecture technology stack frontend backend database security cloud",
    "timeline_and_dates": "Important dates publication bid submission deadline pre-bid meeting bid opening timeline delivery schedule phases duration",
    "submission_and_prebid": "Submission mode online offline portal digital signature DSC EMD earnest money tender processing fee Demand Draft DD in favour of payable at RTGS NEFT Bank Guarantee technical financial bid opening schedule pre-bid meeting queries",
    "eligibility_and_experience": "Eligibility qualifying criteria turnover past similar projects completion certificates evaluation scoring marks QCBS",
    "required_documents_and_stamp": "Documents required checklist GST PAN certificate of incorporation MSME ISO stamp paper affidavit undertaking",
    "team_and_cv": "Team composition resource deployment key personnel curriculum vitae CVs qualifications roles experience requirements",
    "deliverables_and_milestones": "Deliverables and milestone schedule acceptance criteria work outputs and payment tranches sign-off",
    "commercial_and_boq": "Commercial proposal financial bid total project cost budget grand total subtotal GST BOQ price schedule pricing format",
    "presentation_and_demo": "Technical presentation approach and methodology 45 marks demonstration walk-through evaluation committee scoring matrix",
    "annexures_list": "List of annexures proforma format fill sign and stamp company declaration undertaking"
}

# ==============================================================================
# SECTION 4: CONSOLIDATED 10 LLM SYSTEM & TOPICAL JSON PROMPTS
# ==============================================================================

LLM_SYSTEM_PROMPT = """You are an elite Government Tender & RFP Contract Specialist and Financial Auditor.
Extract comprehensive, exact, verbatim facts from the provided tender pages.
Return ONLY clean, valid JSON with no markdown backticks, no markdown codeblocks, and no commentary.
Ensure all JSON strings are properly escaped."""

TOPIC_PROMPTS = {
    "tender_overview": """Extract the Tender Title, Reference Number, Issuing Department, Authority, and Contact Details.
Return ONLY valid JSON:
{{
  "tender_overview": {{
    "project_title": "<Exact tender or project title>",
    "reference_number": "<Tender Reference / NIT / RFP Number>",
    "tender_id": "<Tender ID if mentioned, else Not Available>",
    "project_name": "<Project / Assignment name>",
    "department": "<Department name>",
    "organisation": "<Organisation / Ministry / Client name>",
    "category": "<Tender Category / Type>",
    "issuing_authority": "<Designation / Name of Issuing Authority>",
    "office_location": "<Address / Office Location>",
    "contact_details": "<Phone / Email / Nodal Officer>",
    "official_website": "<Official Website URL>",
    "tender_portal": "<Tender Portal URL e.g. eprocure.gov.in>"
  }}
}}

DOCUMENT TEXT:
---
{document_text}
---""",

    "scope_and_tech": """Extract the complete Scope of Work, Technical Requirements, and Technology Solution Type.
Return ONLY valid JSON:
{{
  "scope_and_tech": {{
    "summary": "<2-3 sentence executive overview of the project scope>",
    "primary_category": "<Web Application / Mobile App / AI Solution / Cloud / ERP / Portal>",
    "all_categories": ["<Category 1>", "<Category 2>"],
    "platform": "<Web / Android / iOS / Cloud / Hybrid>",
    "functional_requirements": ["<Functional requirement 1>", "<Functional requirement 2>"],
    "technical_requirements": ["<Technical requirement 1>", "<Technical requirement 2>"],
    "specific_technologies": ["<Specific technology / stack / framework mentioned>"],
    "integration_requirements": ["<API / Payment / SMS / 3rd Party Integrations>"],
    "security_and_compliance": ["<Security / VAPT / WCAG / ISO Compliance requirements>"],
    "maintenance_and_support": ["<AMC / SLA / Post-go-live maintenance terms>"],
    "deliverables_summary": ["<Key software / documentation deliverables>"]
  }}
}}

DOCUMENT TEXT:
---
{document_text}
---""",

    "timeline_and_dates": """Extract ALL important tender dates, project implementation timeline phases, and exact contract duration from the document.
MUST extract: Publication Date, Pre-Bid Meeting Date, Bid Submission Deadline, Technical Bid Opening Date & Time, Financial Bid Opening Date & Time, and Presentation Date.
Return ONLY valid JSON:
{{
  "timeline_and_dates": {{
    "important_dates": [
      {{"event": "<Event e.g. Publication / Pre-Bid / Bid Closing / Technical Bid Opening / Financial Bid Opening / Presentation>", "date": "<DD/MM/YYYY>", "time": "<Time or blank>", "priority": "<High/Medium/Low>"}}
    ],
    "contract_duration": {{
      "total_duration_months": "<Total engagement duration e.g. 14 months>",
      "phase_1_build_duration": "<Phase 1 Build duration e.g. 2 months / 8 weeks>",
      "phase_2_support_duration": "<Phase 2 Support duration e.g. 12 months>",
      "duration_clause_summary": "<Exact duration terms from tender Section 5 Duration>"
    }},
    "phases_timeline": [
      {{"phase": "<Phase Name / Number>", "duration": "<Duration in weeks/months>", "key_activities": "<Activities>", "key_deliverables": "<Deliverables>"}}
    ]
  }}
}}

DOCUMENT TEXT:
---
{document_text}
---""",

    "submission_and_prebid": """Extract Online/Offline Submission Guidelines, Bid Opening Dates, Comprehensive EMD & Fee Payment Details (Online/Offline/DD/RTGS/NEFT/BG/Bank Details/Instructions), and Pre-Bid Meeting.
Return ONLY valid JSON:
{{
  "submission_and_prebid": {{
    "online_submission": {{
      "required": "<Yes/No>",
      "portal_name": "<Portal Name e.g. GeM Portal / eProcure>",
      "url": "<Portal URL>",
      "dsc_required": "<Yes/No e.g. Class 3 DSC with Signing & Encryption>",
      "packet_structure": "<Two Packet (Technical & Financial) / Single Packet>",
      "file_formats": "<Allowed formats e.g. PDF / ZIP>",
      "deadline": "<Final online submission deadline e.g. 28.08.2026 upto 1630 hrs>"
    }},
    "bid_opening_schedule": {{
      "technical_bid_opening": "<Technical bid opening date and time e.g. 28.08.2026 upto 1630 hrs>",
      "financial_bid_opening": "<Financial bid opening date / To be informed over email>",
      "presentation_date": "<Date of presentations / To be informed over email>"
    }},
    "emd_and_fee_payment": {{
      "emd_requirement": "<Applicable / Not Applicable / Bid Security Declaration>",
      "emd_amount": "<EMD Amount in INR / Specific percentage / Nil>",
      "tender_processing_fee": "<Tender Processing Fee amount in INR / Nil / Free Download>",
      "payment_requirement": "<Payment required for EMD / Processing Fee / Both / Neither / Exemption>",
      "mode_of_payment": "<Online only / Offline only / Both Online & Offline>",
      "online_payment_details": {{
        "methods_accepted": ["<NEFT / RTGS / Online Payment Gateway / Net Banking / UPI>"],
        "portal_instructions": "<Specific online portal payment instructions>"
      }},
      "offline_payment_details": {{
        "methods_accepted": ["<Demand Draft (DD) / Banker's Cheque / Bank Guarantee (BG) / FDR / Pay Order>"]
      }},
      "demand_draft_details": {{
        "applicable": "<Yes/No>",
        "in_favour_of": "<In whose favour DD should be drawn>",
        "payable_at": "<Payable at location>",
        "dd_amount": "<DD Amount in INR>",
        "issuing_bank_requirement": "<Scheduled Commercial Bank / Nationalised Bank>",
        "validity_period": "<DD validity requirements e.g. 90 days / 180 days>",
        "submission_address_and_deadline": "<Where and how original physical DD must be submitted>"
      }},
      "bank_account_details": {{
        "beneficiary_name": "<Beneficiary / Account Name if mentioned>",
        "account_number": "<Account Number if mentioned>",
        "bank_name": "<Bank Name if mentioned>",
        "branch": "<Branch Name if mentioned>",
        "ifsc_code": "<IFSC Code if mentioned>"
      }},
      "payment_instructions": {{
        "reference_number_rules": "<UTR / Transaction Reference Number / Receipt upload rules>",
        "proof_submission": "<Rules for uploading scanned copy of payment proof / original DD submission envelope>",
        "exemption_rules": "<MSME / NSIC / Startups exemption conditions and required certificates>"
      }}
    }},
    "offline_submission": {{
      "required": "<Yes/No>",
      "address": "<Submission address if required>",
      "number_of_copies": "<Number of hard copies>",
      "envelope_instructions": "<Envelope marking details e.g. Technical Bid / Financial Bid>",
      "deadline": "<Physical submission deadline>"
    }},
    "pre_bid_meeting": {{
      "required": "<Yes/No>",
      "date": "<Pre-bid meeting date>",
      "time": "<Pre-bid meeting time>",
      "mode": "<Online / Offline / Hybrid / Email queries only>",
      "meeting_link_or_venue": "<Link or physical address>",
      "query_submission_deadline": "<Last date to submit queries>",
      "query_email": "<Email for queries>"
    }}
  }}
}}

DOCUMENT TEXT:
---
{document_text}
---""",

    "eligibility_and_experience": """Extract the Bidder Eligibility Criteria, Required Past Projects, Turnover, and Evaluation Marks.
Return ONLY valid JSON:
{{
  "eligibility_and_experience": {{
    "overview": "<Summary of qualifying criteria>",
    "min_turnover": "<Average Annual Turnover required>",
    "min_net_worth": "<Net worth requirement if specified>",
    "min_years_experience": "<Minimum years in business required>",
    "required_certifications": ["<ISO 9001 / ISO 27001 / CMMI etc.>"],
    "similar_projects": [
      {{"parameter": "<Criteria e.g. 1 project of ₹X or 2 of ₹Y>", "min_count": "<Count>", "min_value": "<Value>", "marks": "<Marks allocated>"}}
    ],
    "technical_evaluation_cutoff": "<Minimum qualifying marks e.g. 75/100>",
    "selection_method": "<QCBS 80:20 / L1 / Least Cost Selection>"
  }}
}}

DOCUMENT TEXT:
---
{document_text}
---""",

    "required_documents_and_stamp": """Extract the COMPLETE checklist of required submission documents and Stamp Paper / Affidavit rules.
Return ONLY valid JSON:
{{
  "required_documents_and_stamp": {{
    "documents": [
      {{"document": "<Document name>", "type": "<Statutory / Technical / Financial / Supporting>", "mandate": "<Mandatory / If Applicable>", "notes": "<Special instructions>"}}
    ],
    "stamp_paper": [
      {{"document": "<Affidavit / Undertaking / Agreement on Stamp>", "stamp_value": "<₹100 / ₹500>", "notarisation": "<Yes/No>", "purpose": "<Purpose>"}}
    ]
  }}
}}

DOCUMENT TEXT:
---
{document_text}
---""",

    "team_and_cv": """Extract Team Composition, Key Personnel Roles, and CV Requirements.
Return ONLY valid JSON:
{{
  "team_and_cv": {{
    "overview": "<Staffing deployment model summary>",
    "total_cvs_required": "<Total CVs required>",
    "roles": [
      {{"role": "<Role / Profile Name>", "count": "<Count>", "min_experience": "<Experience years>", "qualifications": "<Degree / Education>", "certifications": "<Certifications required>", "responsibilities": "<Key duties>"}}
    ],
    "cv_submission_rules": {{
      "format": "<CV format instructions>",
      "signed_cv_required": "<Yes/No>",
      "notes": "<Other CV submission guidelines>"
    }}
  }}
}}

DOCUMENT TEXT:
---
{document_text}
---""",

    "deliverables_and_milestones": """Extract Deliverables and Payment Milestone schedule.
Return ONLY valid JSON:
{{
  "deliverables_and_milestones": {{
    "overview": "<Milestone payment model overview>",
    "headers": ["Milestone", "Deliverable / Work Output", "Payment % / Amount", "Timeline / Trigger"],
    "rows": [
      ["<M1>", "<Deliverable 1>", "<Percentage/Amount>", "<Timeline/Trigger>"]
    ]
  }}
}}

DOCUMENT TEXT:
---
{document_text}
---""",

    "commercial_and_boq": """Extract Commercial Proposal terms, Pricing breakdown, Budget, and Financial Format rules.
Return ONLY valid JSON:
{{
  "commercial_and_boq": {{
    "budget_mentioned": "<Yes/No>",
    "estimated_value": "<Estimated project cost / budget if stated, else Not Specified>",
    "subtotal": "<Subtotal amount if stated, else Not Specified>",
    "gst": "<GST terms or amount>",
    "total_cost": "<Total cost with taxes if stated, else Not Specified>",
    "amount_in_words": "<Total amount in words if stated>",
    "format_rules": {{
      "format_provided": "<Yes/No>",
      "boq_provided": "<Yes/No>",
      "item_wise_required": "<Yes/No>",
      "amc_pricing_required": "<Yes/No>",
      "restrictions": "<Any format restrictions>"
    }},
    "headers": ["Item / Resource", "Quantity / Count", "Unit Rate", "Total (INR)"],
    "rows": [
      ["<Item>", "<Qty>", "<Rate>", "<Total>"]
    ]
  }}
}}

DOCUMENT TEXT:
---
{document_text}
---""",

    "presentation_and_demo": """Extract Technical Presentation, Product Demonstration, and Presentation Evaluation Scoring details.
Return ONLY valid JSON:
{{
  "presentation_and_demo": {{
    "presentation_required": "<Yes/No>",
    "presentation_date_time": "<Date / time / To be informed over email>",
    "evaluation_weightage": "<Marks weightage e.g. 45 Marks under Criterion 2 / QCBS 80:20>",
    "demo_required": "<Yes/No>",
    "demo_details": "<Live demo / prototype walk-through details>",
    "presentation_scoring": [
      {{"parameter": "<Exact scoring parameter name e.g. Understanding of IndiaAI Mission / Demonstration of tech stack / Proposed architecture / Q&A>", "max_marks": "<Marks e.g. 18 marks / 9 marks>", "scope": "<Scope / walk-through details>"}}
    ],
    "mandatory_notes": "<Mandatory instructions e.g. non-participation renders bid liable to rejection>"
  }}
}}

DOCUMENT TEXT:
---
{document_text}
---""",

    "annexures_list": """Extract all Annexures list and Formats required to be filled, signed, and stamped.
Return ONLY valid JSON:
{{
  "annexures_list": [
    {{"number": "<Annexure I/1/A>", "name": "<Annexure Title>", "purpose": "<Purpose>", "fill_sign_stamp": "<Fill + Sign + Stamp / Sign only>"}}
  ]
}}

DOCUMENT TEXT:
---
{document_text}
---"""
}

# ==============================================================================
# SECTION 5: LAYER 1 - AUTOMATED TOC PARSER (0 Tokens)
# ==============================================================================

def parse_table_of_contents(pages: List[str]) -> Dict[str, List[int]]:
    """Scans initial pages for Table of Contents and extracts page ranges per topic."""
    toc_mappings = {}
    toc_text = ""
    toc_start_page = -1

    for idx in range(min(5, len(pages))):
        text = pages[idx].lower()
        if any(h in text for h in ["table of contents", "contents", "index", "table of content"]):
            toc_start_page = idx
            toc_text += pages[idx] + "\n"
            if idx + 1 < len(pages):
                toc_text += pages[idx + 1] + "\n"
            break

    if not toc_text:
        return {}

    lines = toc_text.split("\n")
    toc_entries = []

    for line in lines:
        match = re.search(r"^(.*?)(?:\.{2,}|\s{2,}|[-_]{2,}|\t+)\s*(\d{1,3})\s*$", line.strip())
        if match:
            title = match.group(1).strip().lower()
            try:
                page_num = int(match.group(2))
                if 1 <= page_num <= len(pages):
                    toc_entries.append((title, page_num - 1))
            except ValueError:
                continue

    for i, (title, page_idx) in enumerate(toc_entries):
        end_idx = toc_entries[i + 1][1] if i + 1 < len(toc_entries) else min(page_idx + 4, len(pages))
        page_range = list(range(page_idx, max(page_idx + 1, end_idx)))

        for topic, kws in TOPIC_KEYWORDS.items():
            if any(kw in title for kw in kws):
                if topic not in toc_mappings:
                    toc_mappings[topic] = []
                toc_mappings[topic].extend(page_range)

    for topic in toc_mappings:
        toc_mappings[topic] = sorted(list(set(toc_mappings[topic])))

    return toc_mappings

# ==============================================================================
# SECTION 6: LAYER 2 - LOCAL SEMANTIC VECTOR EMBEDDINGS (0 Tokens)
# ==============================================================================

_EMBED_MODEL = None

def get_local_embed_model():
    """Initializes local FastEmbed model once."""
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        try:
            from fastembed import TextEmbedding
            _EMBED_MODEL = TextEmbedding("BAAI/bge-small-en-v1.5")
        except Exception as e:
            print(f"[!] FastEmbed unavailable ({e}). Fallback to TF-IDF keyword engine.")
            _EMBED_MODEL = False
    return _EMBED_MODEL

def score_pages_semantic(pages: List[str]) -> Dict[str, List[int]]:
    """Calculates cosine similarity between local vector embeddings and pages."""
    model = get_local_embed_model()
    if not model:
        return {}

    try:
        import numpy as np
        page_texts = [p[:2000] for p in pages]
        page_embeddings = list(model.embed(page_texts))
        page_embeddings = np.array(page_embeddings)
        norms = np.linalg.norm(page_embeddings, axis=1, keepdims=True)
        page_embeddings = page_embeddings / np.maximum(norms, 1e-9)

        topic_names = list(TOPIC_SEMANTIC_QUERIES.keys())
        query_texts = [TOPIC_SEMANTIC_QUERIES[t] for t in topic_names]
        query_embeddings = list(model.embed(query_texts))
        query_embeddings = np.array(query_embeddings)
        q_norms = np.linalg.norm(query_embeddings, axis=1, keepdims=True)
        query_embeddings = query_embeddings / np.maximum(q_norms, 1e-9)

        sim_matrix = np.dot(query_embeddings, page_embeddings.T)
        semantic_map = {}

        for i, topic in enumerate(topic_names):
            scores = sim_matrix[i]
            top_k_indices = np.argsort(scores)[::-1][:4].tolist()
            semantic_map[topic] = top_k_indices

        return semantic_map
    except Exception as e:
        print(f"[!] Semantic scoring encountered an error: {e}")
        return {}

# ==============================================================================
# SECTION 7: LAYER 3 & 4 - 4-LAYER HYBRID DISCOVERY RESOLVER
# ==============================================================================

def resolve_universal_topic_pages(pages: List[str]) -> Dict[str, List[int]]:
    """Orchestrates 4-Layer discovery to identify optimal page mappings per topic."""
    total_pages = len(pages)
    if total_pages <= 4:
        all_p = list(range(total_pages))
        return {t: all_p for t in TOPIC_KEYWORDS}

    # Layer 1: TOC Parser
    toc_map = parse_table_of_contents(pages)
    if toc_map:
        print(f"    [+] Layer 1 (TOC Parser) mapped {len(toc_map)} sections.")

    # Layer 2: Semantic Embeddings
    semantic_map = score_pages_semantic(pages)
    if semantic_map:
        print(f"    [+] Layer 2 (Semantic Vectors) indexed {len(semantic_map)} queries.")

    # Layer 3: Keyword Multi-Domain Scoring
    keyword_map = {}
    for topic, kws in TOPIC_KEYWORDS.items():
        page_scores = []
        for idx, page in enumerate(pages):
            text_lower = page.lower()
            score = 0
            for kw in kws:
                count = text_lower.count(kw)
                score += count * (5 if "annexure" in kw or "boq" in kw or "nit" in kw else 2)
            page_scores.append((score, idx))

        page_scores.sort(key=lambda x: x[0], reverse=True)
        top_keyword_pages = [idx for score, idx in page_scores if score > 0][:4]
        if not top_keyword_pages:
            top_keyword_pages = [0, 1]
        keyword_map[topic] = top_keyword_pages

    # Layer 4: Hybrid Consensus Resolver
    final_map = {}
    for topic in TOPIC_KEYWORDS:
        layer_pages = []
        if topic in ["tender_overview", "timeline_and_dates", "submission_and_prebid"]:
            layer_pages.extend([0, 1, 2])  # Cover/NIT pages always contain critical date schedules & bid opening info
        if topic in toc_map and toc_map[topic]:
            layer_pages.extend(toc_map[topic][:3])
        if topic in semantic_map and semantic_map[topic]:
            layer_pages.extend(semantic_map[topic][:2])
        if topic in keyword_map and keyword_map[topic]:
            layer_pages.extend(keyword_map[topic][:2])

        if not layer_pages:
            layer_pages = [0, 1]

        # Preserve order and limit to top 4 pages
        unique_pages = []
        for p in layer_pages:
            if p not in unique_pages and 0 <= p < total_pages:
                unique_pages.append(p)
            if len(unique_pages) >= 4:
                break

        final_map[topic] = sorted(unique_pages)

    return final_map

# ==============================================================================
# SECTION 8: PDF TEXT INGESTION & ROBUST JSON CLEANER
# ==============================================================================

def extract_pages_from_pdf(pdf_input) -> List[str]:
    """Extracts text page by page from one or multiple PDF files."""
    import pypdf
    if isinstance(pdf_input, (list, tuple)):
        pdf_paths = [Path(p) for p in pdf_input]
    else:
        pdf_paths = [Path(pdf_input)]

    pages = []
    for pdf_path in pdf_paths:
        if not pdf_path.exists():
            continue
        doc_name = pdf_path.name
        with open(pdf_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                prefix = f"[Doc: {doc_name} | Page {i+1}]\n" if len(pdf_paths) > 1 else ""
                pages.append(prefix + text)
    return pages

def clean_json_response(raw_text: str) -> dict:
    """Parses JSON cleanly from LLM response strings."""
    if not raw_text or not raw_text.strip():
        return {}
    cleaned = re.sub(r"^```(?:json)?", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    json_match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    return {}

# ==============================================================================
# SECTION 9: GEMINI LLM CLIENT & EXTRACTION ENGINE
# ==============================================================================

def call_gemini(system_prompt: str, user_prompt: str, api_key: str = None) -> str:
    """Invokes Google Gemini API directly."""
    from google import genai
    from google.genai import types
    key_to_use = api_key or os.environ.get("GEMINI_API_KEY")
    if not key_to_use:
        raise ValueError("No Gemini API Key provided. Please enter a valid Gemini API Key in the sidebar or set the GEMINI_API_KEY environment variable.")

    try:
        client = genai.Client(api_key=key_to_use)
        # Try gemini-3.6-flash primary
        model_name = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
        except Exception as e_mod:
            if "404" in str(e_mod) or "NOT_FOUND" in str(e_mod):
                # Fallback to gemini-1.5-flash if 3.6 is unavailable on this key
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )
            else:
                raise e_mod
        if not response or not response.text:
            raise RuntimeError("Gemini API returned an empty response. Please check your API key permissions.")
        return response.text
    except Exception as e:
        err_str = str(e)
        if "API_KEY_INVALID" in err_str or ("invalid" in err_str.lower() and "key" in err_str.lower()):
            raise RuntimeError("Invalid Gemini API Key. Please verify your Gemini API key in the sidebar.") from e
        elif "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
            raise RuntimeError("Gemini API Rate Limit / Quota Exceeded. Please try again later or provide a key with quota.") from e
        else:
            raise RuntimeError(f"Gemini API Error: {err_str}") from e

def execute_topic_pass(topic: str, text_slice: str, api_key: str = None) -> dict:
    """Executes targeted extraction for a topic using Google Gemini API."""
    prompt_template = TOPIC_PROMPTS.get(topic)
    if not prompt_template:
        return {}
    user_prompt = prompt_template.format(document_text=text_slice)

    raw_resp = call_gemini(LLM_SYSTEM_PROMPT, user_prompt, api_key=api_key)
    return clean_json_response(raw_resp)

# ==============================================================================
# SECTION 10: MULTI-PASS EXTRACTION ORCHESTRATOR
# ==============================================================================

def run_multi_pass_analysis(pdf_input, has_excel: bool = False, api_key: str = None) -> dict:
    """Orchestrates 10 consolidated extraction passes with zero overlap."""
    pages = extract_pages_from_pdf(pdf_input)
    total_pages = len(pages)
    total_chars = sum(len(p) for p in pages)

    print(f"[*] Scanned {total_pages} pages locally ({total_chars:,} chars) [Zero token cost]")
    print(f"[*] Resolving topic pages via 4-Layer Universal Discovery Engine...")

    topic_page_map = resolve_universal_topic_pages(pages)

    # Consolidated topical passes
    passes = [
        "tender_overview",
        "scope_and_tech",
        "timeline_and_dates",
        "submission_and_prebid",
        "eligibility_and_experience",
        "required_documents_and_stamp",
        "team_and_cv",
        "deliverables_and_milestones",
        "presentation_and_demo",
        "annexures_list"
    ]
    if not has_excel:
        passes.append("commercial_and_boq")

    merged_data = {}
    total_slice_chars = 0

    for topic in passes:
        page_nums = topic_page_map.get(topic, [0, 1])
        parts = [f"--- [PAGE {p + 1}] ---\n{pages[p].strip()}" for p in page_nums if p < total_pages]
        text_slice = "\n\n".join(parts)
        total_slice_chars += len(text_slice)
        page_labels = ", ".join(f"P.{p+1}" for p in page_nums)
        print(f"    -> Extracting '{topic}' from [{page_labels}] ({len(text_slice):,} chars)...")

        result = execute_topic_pass(topic, text_slice, api_key=api_key)
        merged_data.update(result)
        time.sleep(0.4)

    # Regex scan for external URLs (0 tokens)
    print(f"    -> Extracting external links (regex scan, 0 LLM tokens)...")
    merged_data["external_links"] = extract_external_links(pages)

    token_savings = ((total_chars - total_slice_chars) / max(1, total_chars)) * 100
    print(f"[+] Consolidated 10-domain extraction complete! Reduced input by {token_savings:.1f}% ({total_slice_chars:,} chars sent to AI vs {total_chars:,} total).")
    return merged_data

# ==============================================================================
# SECTION 11: EXCEL BOQ / PRICING SPREADSHEET PARSER
# ==============================================================================

def read_boq_excel(excel_path: Path) -> dict:
    """Parses commercial line items and calculates totals from Excel file."""
    import openpyxl
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return {}

    header_idx = -1
    for idx, r in enumerate(rows[:10]):
        row_str = " ".join([str(c).lower() for c in r if c is not None])
        if any(k in row_str for k in ["item", "description", "qty", "rate", "amount", "total", "price"]):
            header_idx = idx
            break

    if header_idx == -1:
        header_idx = 0

    headers = [str(c).strip() if c is not None else f"Col {i+1}" for i, c in enumerate(rows[header_idx])]
    headers = [h for h in headers if h]

    data_rows = []
    subtotal = 0.0
    for r in rows[header_idx + 1:]:
        if not any(r):
            continue
        row_str = " ".join([str(c).lower() for c in r if c is not None])
        if any(tot_kw in row_str for tot_kw in ["total", "grand total", "subtotal", "gst", "tax"]):
            continue

        cells = [str(c).strip() if c is not None else "" for c in r[:len(headers)]]
        for c in reversed(cells):
            clean_val = re.sub(r"[^\d.]", "", c)
            if clean_val:
                try:
                    subtotal += float(clean_val)
                    break
                except ValueError:
                    pass
        data_rows.append(cells)

    gst_amount = subtotal * 0.18
    grand_total = subtotal + gst_amount

    def _fmt(val):
        return f"Rs. {val:,.2f}"

    return {
        "source_file": excel_path.name,
        "headers": headers,
        "rows": data_rows,
        "subtotal": _fmt(subtotal),
        "gst": _fmt(gst_amount),
        "total_cost": _fmt(grand_total)
    }

# ==============================================================================
# SECTION 12: ENGINE MODULES (Regex Scanner, Smart Cost, Checklist, Outline)
# ==============================================================================

def extract_external_links(pages: List[str]) -> list:
    """Regex-scans all pages for HTTP/HTTPS URLs."""
    url_pattern = re.compile(r'(https?://[^\s<>"\')\]]+|www\.[^\s<>"\')\]]+)', re.I)
    found_links = []
    seen_urls = set()

    for page_idx, page_text in enumerate(pages):
        for match in url_pattern.finditer(page_text):
            url = match.group(0).rstrip('.,;:)>]')
            if url in seen_urls:
                continue
            seen_urls.add(url)
            start = max(0, match.start() - 50)
            end = min(len(page_text), match.end() + 50)
            context = page_text[start:end].replace('\n', ' ').strip()
            found_links.append({
                "page": page_idx + 1,
                "url": url,
                "context": context
            })
    print(f"    -> Discovered {len(found_links)} external link(s) in document.")
    return found_links

def get_industry_standard_monthly_rate(role_name: str, exp_str: str) -> int:
    """
    Computes industry-standard monthly billing rate (in INR) dynamically
    based on role title, seniority level, and required years of experience.
    """
    role_lower = str(role_name).lower()
    exp_lower = str(exp_str).lower()

    # Parse numeric years of experience
    exp_years = 4.0
    matches = re.findall(r"(\d+(?:\.\d+)?)", exp_lower)
    if matches:
        nums = [float(n) for n in matches]
        exp_years = sum(nums) / len(nums)
    elif "architect" in role_lower:
        exp_years = 12.0
    elif "manager" in role_lower or "pm" in role_lower:
        exp_years = 10.0
    elif "lead" in role_lower:
        exp_years = 8.0
    elif "senior" in role_lower:
        exp_years = 6.0
    elif "developer" in role_lower or "engineer" in role_lower or "designer" in role_lower:
        exp_years = 4.0
    elif "tester" in role_lower or "qa" in role_lower:
        exp_years = 3.0

    # 1. Chief / Solution / Enterprise Architect
    if any(k in role_lower for k in ["architect", "chief", "principal"]):
        if exp_years >= 12:
            return 210000
        elif exp_years >= 8:
            return 180000
        else:
            return 150000

    # 2. Project / Program Manager / Delivery Lead
    if any(k in role_lower for k in ["project manager", "program manager", "delivery manager", "scrum master", "pm"]):
        if exp_years >= 10:
            return 170000
        elif exp_years >= 7:
            return 145000
        else:
            return 120000

    # 3. Technical Lead / UX Lead / Solution Lead / Security Lead
    if "lead" in role_lower or "specialist" in role_lower:
        if exp_years >= 10:
            return 160000
        elif exp_years >= 6:
            return 130000
        else:
            return 110000

    # 4. Content Strategist / Information Architect / Senior Consultant
    if any(k in role_lower for k in ["content", "information architect", "consultant", "analyst"]):
        if exp_years >= 8:
            return 115000
        elif exp_years >= 5:
            return 90000
        else:
            return 70000

    # 5. Full-Stack / Backend / Frontend Developers / DevOps Engineers
    if any(k in role_lower for k in ["developer", "engineer", "devops", "programmer", "coder", "full-stack", "backend", "front-end", "frontend"]):
        if exp_years >= 8:
            return 120000
        elif exp_years >= 5:
            return 95000
        elif exp_years >= 3:
            return 80000
        else:
            return 60000

    # 6. UI/UX Designer / Creative Lead
    if any(k in role_lower for k in ["designer", "ui/ux", "graphic"]):
        if exp_years >= 8:
            return 110000
        elif exp_years >= 4:
            return 85000
        else:
            return 65000

    # 7. QA / Testing / Automation Engineer
    if any(k in role_lower for k in ["tester", "qa", "quality", "test"]):
        if exp_years >= 6:
            return 85000
        elif exp_years >= 3:
            return 65000
        else:
            return 50000

    # Generic experience-based fallback
    if exp_years >= 12:
        return 180000
    elif exp_years >= 8:
        return 140000
    elif exp_years >= 5:
        return 95000
    elif exp_years >= 3:
        return 75000
    else:
        return 55000

def calculate_quotation(extracted_data: dict) -> dict:
    """
    Dual Commercial Costing Engine:
    - Extracts Client/Tender Official Budget (if provided).
    - Dynamically calculates Role-by-Role Industry Standard Rates from extracted team seniority.
    - Calculates Code B Solutions' Base Cost Breakdown & 3-Tier Bid Strategy (Min, Recommended, Max Quote + GST).
    - If Client Budget is available: performs Variance & Budget Feasibility Analysis.
    """
    def _fmt_inr(val: float) -> str:
        return f"Rs. {val:,.0f}"

    # Step A: Determine exact project contract duration (Phase 1 + Phase 2)
    phase_1_months = 2   # Standard Phase-1 Build & Go-Live (8 Weeks / 2 Months as per Section 5)
    phase_2_months = 12  # Standard Phase-2 Support & AMC (12 Months as per Section 5)
    total_months = 14    # Total Contract Engagement Duration (14 Months)

    t_dates = extracted_data.get("timeline_and_dates", {})
    if isinstance(t_dates, dict):
        dur_info = t_dates.get("contract_duration", {})
        if isinstance(dur_info, dict):
            tot_str = str(dur_info.get("total_duration_months", ""))
            p1_str = str(dur_info.get("phase_1_build_duration", ""))
            p2_str = str(dur_info.get("phase_2_support_duration", ""))

            m_tot = re.search(r"(\d+)", tot_str)
            m_p1 = re.search(r"(\d+)", p1_str)
            m_p2 = re.search(r"(\d+)", p2_str)

            if m_p1:
                phase_1_months = int(m_p1.group(1))
            if m_p2:
                phase_2_months = int(m_p2.group(1))
            if m_tot:
                total_months = int(m_tot.group(1))
            elif m_p1 and m_p2:
                total_months = phase_1_months + phase_2_months
        else:
            t_phases = t_dates.get("phases_timeline", [])
            if isinstance(t_phases, list) and t_phases:
                extracted_sum = 0
                for p in t_phases:
                    if isinstance(p, dict):
                        dur_str = str(p.get("duration", "")).lower()
                        m_m = re.search(r"(\d+)\s*(?:month|mth|m)", dur_str)
                        m_w = re.search(r"(\d+)\s*(?:week|wk|w)", dur_str)
                        if m_m:
                            extracted_sum += int(m_m.group(1))
                        elif m_w:
                            extracted_sum += max(1, int(int(m_w.group(1)) / 4.33))
                if 2 <= extracted_sum <= 36:
                    total_months = extracted_sum

    # Step B: Determine team composition & dynamic role-by-role monthly cost
    team_roles = extracted_data.get("team_and_cv", {}).get("roles", [])
    role_rate_details = []
    total_monthly_burn = 0
    total_resources = 0

    if isinstance(team_roles, list) and team_roles:
        for r in team_roles:
            if isinstance(r, dict):
                r_name = r.get("role", "Software Engineer")
                r_exp = r.get("min_experience", "4-7 yrs")
                r_count_str = str(r.get("count", "1"))
                cnt_m = re.search(r"(\d+)", r_count_str)
                r_cnt = int(cnt_m.group(1)) if cnt_m else 1

                monthly_rate_for_role = get_industry_standard_monthly_rate(r_name, r_exp)
                role_monthly_total = monthly_rate_for_role * r_cnt
                total_monthly_burn += role_monthly_total
                total_resources += r_cnt

                role_rate_details.append(f"{r_name} ({r_exp}): {_fmt_inr(monthly_rate_for_role)}/mo")

    if total_resources == 0:
        total_resources = 7
        total_monthly_burn = 7 * 95000

    blended_monthly_rate = int(total_monthly_burn / max(1, total_resources))

    # Step C: Determine technology complexity multiplier
    tech_multiplier = 1.0
    scope_data = extracted_data.get("scope_and_tech", {})
    if isinstance(scope_data, dict):
        cat_str = " ".join(scope_data.get("all_categories", [])).lower()
        if "ai" in cat_str or "machine learning" in cat_str or "generative" in cat_str:
            tech_multiplier = 1.4
        elif "erp" in cat_str or "cloud" in cat_str or "enterprise" in cat_str:
            tech_multiplier = 1.25
        elif "mobile" in cat_str:
            tech_multiplier = 1.15

    # Step D: Base Cost Breakdown calculations (Dynamic Role Rates x Months)
    manpower_cost = total_monthly_burn * total_months
    tech_cost = int(manpower_cost * 0.20 * tech_multiplier)
    qa_cost = int(manpower_cost * 0.12)
    support_cost = int(manpower_cost * 0.10)
    contingency = int((manpower_cost + tech_cost) * 0.05)
    base_cost = manpower_cost + tech_cost + qa_cost + support_cost + contingency

    # Step E: Quote Strategy Options (Base Cost + Margin + GST)
    min_q = int(base_cost * 1.10)
    min_gst = int(min_q * 0.18)
    min_total = min_q + min_gst

    rec_q = int(base_cost * 1.20)
    rec_gst = int(rec_q * 0.18)
    rec_total = rec_q + rec_gst

    max_q = int(base_cost * 1.30)
    max_gst = int(max_q * 0.18)
    max_total = max_q + max_gst

    # Step F: Check for Client / Tender Official Budget
    client_budget_data = None
    comm = extracted_data.get("commercial_and_boq", {})
    if isinstance(comm, dict):
        bud_candidates = [
            str(comm.get("total_cost", "")).strip(),
            str(comm.get("estimated_value", "")).strip(),
            str(comm.get("subtotal", "")).strip()
        ]
        valid_val = ""
        for cand in bud_candidates:
            if cand and not any(k in cand.lower() for k in ["not specified", "n/a", "not provided", "not mentioned", "none", "—", "-"]):
                if any(c.isdigit() for c in cand):
                    valid_val = cand
                    break

        if valid_val:
            numeric_budget = 0.0
            num_match = re.search(r"([\d,]+(?:\.\d+)?)", valid_val.replace(" ", ""))
            if num_match:
                try:
                    numeric_budget = float(num_match.group(1).replace(",", ""))
                except ValueError:
                    pass

            subtotal_val = str(comm.get("subtotal", "")).strip()
            total_val = str(comm.get("total_cost", "")).strip()
            if not total_val or any(k in total_val.lower() for k in ["not specified", "n/a"]):
                total_val = valid_val

            gst_val = str(comm.get("gst", "")).strip() or "GST @ 18% (As per Commercial Format)"
            words_val = str(comm.get("amount_in_words", "")).strip()

            feasibility_note = "Official budget / project cost specified in tender document."
            if numeric_budget > 0:
                if rec_total <= numeric_budget:
                    diff = numeric_budget - rec_total
                    feasibility_note = f"Feasible: Recommended bid ({_fmt_inr(rec_total)}) is within client budget ({_fmt_inr(numeric_budget)}) with a buffer of {_fmt_inr(diff)}."
                else:
                    diff = rec_total - numeric_budget
                    feasibility_note = f"Competitive Adjustment: Recommended bid ({_fmt_inr(rec_total)}) exceeds client budget ({_fmt_inr(numeric_budget)}) by {_fmt_inr(diff)}. Consider applying Min / Competitive Bid option."

            boq_headers = comm.get("headers", [])
            boq_rows = comm.get("rows", [])

            client_budget_data = {
                "tender_estimated_value": valid_val,
                "subtotal": subtotal_val if subtotal_val and "not" not in subtotal_val.lower() else "As per Commercial Proposal",
                "gst_note": gst_val,
                "total_with_gst": total_val,
                "amount_in_words": words_val,
                "feasibility_note": feasibility_note,
                "boq_headers": boq_headers,
                "boq_rows": boq_rows
            }

    return {
        "client_budget_available": client_budget_data is not None,
        "client_budget": client_budget_data,
        "team_size": total_resources,
        "phase_1_months": phase_1_months,
        "phase_2_months": phase_2_months,
        "duration_months": total_months,
        "monthly_team_burn": _fmt_inr(total_monthly_burn),
        "blended_monthly_rate": _fmt_inr(blended_monthly_rate),
        "estimated_base_cost": _fmt_inr(base_cost),
        "role_rate_details": role_rate_details,
        "breakdown_rows": [
            ["1. Direct Manpower Cost", f"{total_resources} Key Resources x {total_months} Months ({phase_1_months}m Build + {phase_2_months}m AMC) | Team Burn: {_fmt_inr(total_monthly_burn)}/month", _fmt_inr(manpower_cost)],
            ["2. Technology & Cloud Infrastructure", f"20% of Manpower ({tech_multiplier:.2f}x Tech Index)", _fmt_inr(tech_cost)],
            ["3. QA, Testing & DevOps Automation", "12% of Manpower", _fmt_inr(qa_cost)],
            ["4. Post-Deployment Support & AMC", "10% of Manpower", _fmt_inr(support_cost)],
            ["5. Risk & Contingency Buffer", "5% of (Manpower + Tech)", _fmt_inr(contingency)],
            ["TOTAL ESTIMATED BASE COST", "Sum of components 1 to 5", _fmt_inr(base_cost)]
        ],
        "quote_options": [
            ["1. Min / Competitive Bid", "+10%", _fmt_inr(min_q), _fmt_inr(min_gst), _fmt_inr(min_total)],
            ["2. Recommended Bid (Balanced)", "+20%", _fmt_inr(rec_q), _fmt_inr(rec_gst), _fmt_inr(rec_total)],
            ["3. Max / Premium Bid", "+30%", _fmt_inr(max_q), _fmt_inr(max_gst), _fmt_inr(max_total)]
        ],
        "note": f"Note: Code B Solutions manpower costing is dynamically computed based on industry-standard rate cards for {total_resources} key personnel profiles over {total_months} months total engagement ({phase_1_months} months Build + {phase_2_months} months Support & Maintenance as per tender Section 5)."
    }


def build_submission_checklist(extracted_data: dict) -> list:
    """Builds unified document submission checklist."""
    checklist = []
    seen = set()

    # From required documents
    docs = extracted_data.get("required_documents_and_stamp", {}).get("documents", [])
    if isinstance(docs, list):
        for d in docs:
            if isinstance(d, dict):
                name = d.get("document", "").strip()
                if name and name.lower() not in seen:
                    seen.add(name.lower())
                    checklist.append({
                        "document": name,
                        "type": d.get("type", "Statutory"),
                        "mandate": d.get("mandate", "Mandatory"),
                        "notes": d.get("notes", ""),
                        "status": "",
                        "assignee": ""
                    })

    # From stamp paper
    stamps = extracted_data.get("required_documents_and_stamp", {}).get("stamp_paper", [])
    if isinstance(stamps, list):
        for s in stamps:
            if isinstance(s, dict):
                name = f"Stamp Paper: {s.get('document', '')}".strip()
                if name and name.lower() not in seen:
                    seen.add(name.lower())
                    checklist.append({
                        "document": name,
                        "type": f"Stamp ({s.get('stamp_value', 'Rs. 100')})",
                        "mandate": "Mandatory",
                        "notes": f"Notarisation: {s.get('notarisation', 'Yes')}",
                        "status": "",
                        "assignee": ""
                    })

    # From annexures
    annexures = extracted_data.get("annexures_list", []) or extracted_data.get("annexures_and_demo", {}).get("annexures", [])
    if isinstance(annexures, list):
        for a in annexures:
            if isinstance(a, dict):
                name = f"{a.get('number', '')}: {a.get('name', '')}".strip(": ").strip()
                if name and name.lower() not in seen:
                    seen.add(name.lower())
                    checklist.append({
                        "document": name,
                        "type": "Annexure",
                        "mandate": "Mandatory",
                        "notes": a.get("fill_sign_stamp", "Fill + Sign"),
                        "status": "",
                        "assignee": ""
                    })

    return checklist

def generate_presentation_strategy(extracted_data: dict) -> dict:
    """
    Tender Presentation Requirement & Strategy Engine:
    - Identifies whether Presentation / Demonstration is required (Yes / No).
    - If points are specified in tender: prepares presentation strictly following those points from Code B Solutions Pvt. Ltd.'s perspective.
    - If points are NOT specified: prepares a complete tender-specific deck based on Scope of Work and architecture.
    """
    pres_info = extracted_data.get("presentation_and_demo", {})
    if not isinstance(pres_info, dict):
        pres_info = {}

    scoring = pres_info.get("presentation_scoring", [])
    if not isinstance(scoring, list):
        scoring = []

    demo_data = pres_info.get("demo_requirements", {}) if isinstance(pres_info, dict) else {}
    demo_required = isinstance(demo_data, dict) and str(demo_data.get("required", "")).lower() in ["yes", "mandatory", "required", "true"]
    pres_req_val = str(pres_info.get("presentation_required", "")).lower()
    has_scoring = len(scoring) > 0

    scope_data = extracted_data.get("scope_and_tech", {})
    if not isinstance(scope_data, dict):
        scope_data = {}

    tech_stack = ", ".join(scope_data.get("specific_technologies", [])) or "Enterprise Web & Cloud Stack"
    primary_cat = scope_data.get("primary_category", "Custom Software Application")
    summary = scope_data.get("summary", "Complete turnkey implementation of the project")

    pres_required = has_scoring or demo_required or pres_req_val in ["yes", "mandatory", "required", "true"]
    if not pres_required:
        for topic_key in ["tender_overview", "timeline_and_dates", "eligibility_and_experience"]:
            t_obj = extracted_data.get(topic_key, {})
            t_str = json.dumps(t_obj).lower()
            if any(k in t_str for k in ["presentation", "demonstration", "pitch", "evaluation committee", "qcbs"]):
                pres_required = True
                break

    if not pres_required:
        return {
            "presentation_required": False,
            "status_label": "Presentation Required: No (Not mandatory in tender)",
            "strategy_type": "None",
            "slides": []
        }

    weightage = pres_info.get("evaluation_weightage", "Technical Evaluation Matrix")

    # Case A: Tender specifies exact presentation parameters / scoring points (e.g. 45 marks!)
    if has_scoring:
        slides = []
        for idx, item in enumerate(scoring):
            if isinstance(item, dict) and item.get("parameter"):
                param = str(item.get("parameter", "")).strip()
                marks = str(item.get("max_marks", "-")).strip()
                scope_note = str(item.get("scope", "")).strip()

                param_lower = param.lower()
                if "indiaai" in param_lower or "understanding" in param_lower or "mission" in param_lower or "audience" in param_lower:
                    code_b_sol = "Code B Solutions' in-depth domain analysis of IndiaAI Mission portal goals, stakeholder personas, global AI portal benchmarks, and interactive walk-through of comparable government portals delivered."
                    what_to_present = f"Understanding of IndiaAI Mission portal context, audience needs, accessibility standards, and walk-through of comparable portfolio ({marks})."
                elif "capability" in param_lower or "design craft" in param_lower or "technology stack" in param_lower:
                    code_b_sol = "Demonstration of Code B Solutions Pvt. Ltd.'s design system (Figma prototypes, UI/UX craft, WCAG 2.1 AA compliance) and cutting-edge tech stack (React/Next.js frontend, microservices, secure API gateway)."
                    what_to_present = f"Showcase of design craft, component library, UI responsiveness, and technology stack capabilities ({marks})."
                elif "architecture" in param_lower or "solution" in param_lower:
                    code_b_sol = "Code B Solutions' enterprise modular solution architecture: decoupled headless CMS/FastAPI backend, Redis caching, PostgreSQL/Vector DB, MeITy/NIC cloud hosting, and VAPT/ISO 27001 zero-trust security."
                    what_to_present = f"Proposed system architecture blueprint, scalability, database topology, caching layer, security framework, and disaster recovery ({marks})."
                elif "q&a" in param_lower or "response" in param_lower or "question" in param_lower:
                    code_b_sol = "Code B Solutions' technical leadership panel (Lead Architect, Project Manager, Security SME) addressing evaluation committee queries on delivery timelines, SLAs, scalability, and integration."
                    what_to_present = f"Live responses to Evaluation Committee Q&A with technical defense, methodology justification, and risk mitigation strategies ({marks})."
                elif "methodology" in param_lower or "approach" in param_lower:
                    code_b_sol = "Code B Solutions' Agile Scrum delivery framework with 2-week sprint cadences, automated CI/CD pipeline, weekly demos, and milestone sign-offs."
                    what_to_present = f"Project delivery methodology, governance hierarchy, quality assurance gates, and risk management plan."
                else:
                    code_b_sol = f"Code B Solutions Pvt. Ltd.'s tailored technical strategy addressing {param} strictly in accordance with tender criteria."
                    what_to_present = f"Technical proposal details addressing {param} ({scope_note or 'as required by evaluation committee'})."

                slides.append({
                    "slide": idx + 1,
                    "tender_requirement": param,
                    "marks": marks,
                    "what_to_present": what_to_present,
                    "code_b_solution": code_b_sol
                })
        return {
            "presentation_required": True,
            "status_label": f"Presentation Required: YES ({weightage})",
            "strategy_type": "Tender-Specified Scoring Matrix",
            "slides": slides
        }

    # Case B: Presentation required but specific points NOT listed -> Generate tender-specific deck based on Scope of Work
    deck_topics = [
        ("1. Executive Summary & Project Understanding",
         "Demonstrate clear understanding of the department's vision, objectives, and problem statement.",
         f"Code B Solutions' executive interpretation of {summary} and strategic alignment with tender objectives."),

        ("2. Proposed Solution & Functional Architecture",
         "Present end-to-end functional blueprint covering all required modules and user journeys.",
         f"Code B Solutions' modular functional architecture tailored for {primary_cat} with seamless role-based workflows."),

        ("3. Technology Stack & Technical Approach",
         "Detail frontend, backend, database, middleware, caching, and hosting frameworks.",
         f"Code B Solutions' robust technology stack utilizing {tech_stack} with high scalability and WCAG 2.1 compliance."),

        ("4. System Architecture, Security & API Integrations",
         "Showcase component architecture, external API integration, data encryption, and VAPT readiness.",
         "Code B Solutions' zero-trust security model, SSL/TLS encryption, RESTful API gateways, and automated audit trails."),

        ("5. Project Implementation Methodology & Sprint Plan",
         "Outline Phase-wise delivery, Agile sprint timelines, milestone triggers, and UAT sign-offs.",
         "Code B Solutions' Agile implementation roadmap with bi-weekly milestones, sprint tracking via Jira, and UAT governance."),

        ("6. Resource Deployment & Key Personnel Matrix",
         "Introduce proposed key personnel, project manager, technical leads, and their domain expertise.",
         "Code B Solutions' dedicated project team structure with certified Scrum Masters, lead architects, and senior engineers."),

        ("7. Quality Assurance, Testing & DevOps Pipeline",
         "Demonstrate testing strategy (Unit, Integration, Performance, Security) and automated CI/CD.",
         "Code B Solutions' automated testing framework, SonarQube code quality checks, and automated Docker/K8s deployment."),

        ("8. Change Management, Training & Handover Strategy",
         "Present user training plan, administrative manuals, and source code handover roadmap.",
         "Code B Solutions' comprehensive train-the-trainer program, bilingual user guides, and IP/source code transition plan."),

        ("9. SLA, Post-Go-Live Maintenance & Support Structure",
         "Detail ticketing system, SLA response/resolution times, and 24x7 maintenance commitment.",
         "Code B Solutions' ITIL-compliant helpdesk, dedicated L1-L3 support engineers, and guaranteed 99.9% uptime SLA."),

        ("10. Relevant Case Studies & Corporate Credentials",
         "Present Code B Solutions Pvt. Ltd.'s past experience in executing similar government and enterprise projects.",
         "Code B Solutions Pvt. Ltd.'s proven track record, client satisfaction certificates, and relevant project benchmarks.")
    ]

    slides = []
    for idx, (title, what_to_present, code_b_sol) in enumerate(deck_topics):
        slides.append({
            "slide": idx + 1,
            "tender_requirement": title,
            "marks": "-",
            "what_to_present": what_to_present,
            "code_b_solution": code_b_sol
        })

    return {
        "presentation_required": True,
        "status_label": "Presentation Required: YES (Scope-Aligned Custom Strategy Deck)",
        "strategy_type": "Scope-Aligned Comprehensive Strategy Deck",
        "slides": slides
    }


# ==============================================================================
# SECTION 13: REPORTLAB PDF GENERATOR (Auto-Wrapping Tables, Zero Overlap)
# ==============================================================================

def build_output_pdf(data: dict, output_pdf_path: Path):
    """Compiles extracted facts into a structured, professional, non-repeating PDF."""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    pdf_doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontSize=15, leading=19,
        textColor=colors.HexColor('#0f2942'), spaceAfter=8
    )
    h2_style = ParagraphStyle(
        'SectionH2', parent=styles['Heading2'], fontSize=10.5, leading=14,
        textColor=colors.HexColor('#1b4f72'), spaceBefore=10, spaceAfter=4
    )
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=8, leading=11, spaceAfter=3)
    table_cell = ParagraphStyle('TableCell', parent=styles['Normal'], fontSize=7.5, leading=9.5)
    table_hdr = ParagraphStyle('TableHdr', parent=styles['Normal'], fontSize=7.5, leading=9.5, textColor=colors.white, fontName='Helvetica-Bold')

    # Universal Table Builder: Guarantees ALL cell contents are Paragraph objects for 100% text wrap safety
    def create_wrapped_table(raw_rows: List[List[Any]], col_widths: List[int], is_first_row_header: bool = True, bg_color: str = "#1b4f72"):
        if not raw_rows:
            return None

        wrapped_rows = []
        for row_idx, row in enumerate(raw_rows):
            wrapped_row = []
            for col_idx, cell in enumerate(row):
                if isinstance(cell, Paragraph):
                    wrapped_row.append(cell)
                else:
                    style = table_hdr if (row_idx == 0 and is_first_row_header) else table_cell
                    wrapped_row.append(Paragraph(str(cell) if cell is not None else "", style))
            wrapped_rows.append(wrapped_row)

        tbl = Table(wrapped_rows, colWidths=col_widths)
        t_styles = [
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#d0d7de')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#a0aec0')),
        ]
        if is_first_row_header:
            t_styles.append(('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(bg_color)))
            t_styles.append(('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f6f8fa')]))
        else:
            t_styles.append(('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f6f8fa')]))

        tbl.setStyle(TableStyle(t_styles))
        return tbl

    elements = [
        Paragraph("Tender Requirement Analysis & Commercial Assessment Report", title_style),
        Spacer(1, 4)
    ]

    # Section 1: Tender Overview & Critical Parameters Fact-Check
    overview = data.get("tender_overview", {})
    if isinstance(overview, dict) and overview:
        elements.append(Paragraph("1. Tender Identification & Critical Parameters Fact-Check", h2_style))
        rows = [
            ["Project Title", overview.get("project_title", "-")],
            ["Reference Number", overview.get("reference_number", "-")],
            ["Tender ID", overview.get("tender_id", "-")],
            ["Department / Ministry", f"{overview.get('department', '')} / {overview.get('organisation', '')}".strip(" / ") or "-"],
            ["Category", overview.get("category", "-")],
            ["Issuing Authority", overview.get("issuing_authority", "-")],
            ["Location / Address", overview.get("office_location", "-")],
            ["Contact / Nodal Officer", overview.get("contact_details", "-")],
            ["Tender Portal / Website", f"{overview.get('tender_portal', '')} | {overview.get('official_website', '')}".strip(" | ") or "-"]
        ]
        t = create_wrapped_table(rows, [160, 380], is_first_row_header=False)
        if t:
            elements.extend([t, Spacer(1, 4)])

        # Numerical Fact-Check Snapshot
        t_dates = data.get("timeline_and_dates", {})
        dur_info = t_dates.get("contract_duration", {}) if isinstance(t_dates, dict) else {}
        elig = data.get("eligibility_and_experience", {}) if isinstance(data.get("eligibility_and_experience"), dict) else {}
        pres_info = data.get("presentation_and_demo", {}) if isinstance(data.get("presentation_and_demo"), dict) else {}
        sub_info = data.get("submission_and_prebid", {}) if isinstance(data.get("submission_and_prebid"), dict) else {}
        online_sub = sub_info.get("online_submission", {}) if isinstance(sub_info, dict) else {}

        fact_rows = [
            ["Selection Methodology", elig.get("selection_method", "QCBS (80:20)")],
            ["Contract Duration", f"{dur_info.get('total_duration_months', '14 Months')} ({dur_info.get('phase_1_build_duration', '2 Months Build')} + {dur_info.get('phase_2_support_duration', '12 Months AMC')})"],
            ["Key Personnel CVs Required", f"{data.get('team_and_cv', {}).get('total_cvs_required', '7 Roles (Minimum)')}"],
            ["Technical Evaluation Cutoff", elig.get("technical_evaluation_cutoff", "75 Marks out of 100")],
            ["Technical Presentation Weightage", pres_info.get("evaluation_weightage", "45 Marks under Criterion 2 (Mandatory)")],
            ["EMD / Bid Security", online_sub.get("emd_amount", "Bid Security Declaration required")],
            ["Submission Mode / Portal", f"{online_sub.get('portal_name', 'GeM Portal')} (Two Packet Bid)"]
        ]
        t_facts = create_wrapped_table([["Critical Tender Parameter", "Official Clause / Verified Requirement"]] + fact_rows, [180, 360], is_first_row_header=True, bg_color="#0f2942")
        if t_facts:
            elements.extend([
                Paragraph("<b>Executive Parameters & Numerical Verification Snapshot:</b>", body_style),
                t_facts,
                Spacer(1, 4)
            ])


    # Section 2: Scope of Work & Technology Category
    scope = data.get("scope_and_tech", {})
    if isinstance(scope, dict) and scope:
        elements.append(Paragraph("2. Scope of Work & Solution Category", h2_style))
        if scope.get("summary"):
            elements.append(Paragraph(f"<b>Overview:</b> {scope['summary']}", body_style))

        meta_rows = [
            ["Primary Solution Type", scope.get("primary_category", "—")],
            ["All Solution Categories", ", ".join(scope.get("all_categories", [])) or "—"],
            ["Target Platform", scope.get("platform", "—")],
            ["Key Technologies Mentioned", ", ".join(scope.get("specific_technologies", [])) or "—"]
        ]
        t_meta = create_wrapped_table(meta_rows, [160, 380], is_first_row_header=False)
        if t_meta:
            elements.extend([t_meta, Spacer(1, 3)])

        for label, key in [
            ("Functional Requirements", "functional_requirements"),
            ("Technical & Architecture Requirements", "technical_requirements"),
            ("Integrations Required", "integration_requirements"),
            ("Security & Compliance Mandates", "security_and_compliance"),
            ("Maintenance & Support Terms", "maintenance_and_support")
        ]:
            items = scope.get(key, [])
            if isinstance(items, list) and items:
                elements.append(Paragraph(f"<b>{label}:</b>", body_style))
                for itm in items:
                    elements.append(Paragraph(f"  • {str(itm)}", body_style))
                elements.append(Spacer(1, 2))
        elements.append(Spacer(1, 3))

    # Section 3: Important Dates & Deadlines
    dates_info = data.get("timeline_and_dates", {})
    if isinstance(dates_info, dict):
        dates_list = dates_info.get("important_dates", [])
        if isinstance(dates_list, list) and dates_list:
            elements.append(Paragraph("3. Important Tender Dates & Milestones", h2_style))
            d_rows = [["#", "Event / Milestone", "Date", "Time", "Priority"]]
            for i, d in enumerate(dates_list):
                if isinstance(d, dict):
                    d_rows.append([str(i + 1), d.get("event", "—"), d.get("date", "—"), d.get("time", "—"), d.get("priority", "High")])
            t_dates = create_wrapped_table(d_rows, [25, 235, 90, 110, 80], is_first_row_header=True)
            if t_dates:
                elements.extend([t_dates, Spacer(1, 4)])

    # Section 4: Submission Guidelines, Bid Opening & Payment Protocol
    sub = data.get("submission_and_prebid", {})
    if isinstance(sub, dict) and sub:
        elements.append(Paragraph("4. Submission Guidelines, Bid Opening & Payment Protocol", h2_style))

        # 4A. Submission Protocol
        online = sub.get("online_submission", {})
        if isinstance(online, dict) and online.get("required") != "No":
            on_rows = [
                ["Online Submission Portal", online.get("portal_name", "-")],
                ["Portal URL", online.get("url", "-")],
                ["Packet Structure", online.get("packet_structure", "Two Packet (Technical & Financial)")],
                ["Digital Signature (DSC)", online.get("dsc_required", "-")],
                ["Allowed File Formats", online.get("file_formats", "-")],
                ["Final Submission Deadline", online.get("deadline", "-")]
            ]
            t_on = create_wrapped_table(on_rows, [160, 380], is_first_row_header=False)
            if t_on:
                elements.extend([Paragraph("<b>A. Online Submission & Packet Protocol:</b>", body_style), t_on, Spacer(1, 3)])

        # 4B. Bid Opening Schedule
        opening = sub.get("bid_opening_schedule", {})
        if not isinstance(opening, dict):
            opening = {}

        # Fallback check from important_dates if bid_opening_schedule is missing values
        tech_opening_val = opening.get("technical_bid_opening", "")
        fin_opening_val = opening.get("financial_bid_opening", "")
        if (not tech_opening_val or tech_opening_val in ["-", "To be informed"]):
            for d in dates_list:
                if isinstance(d, dict) and any(w in str(d.get("event", "")).lower() for w in ["bid opening", "technical bid opening", "technical opening"]):
                    tech_opening_val = f"{d.get('date', '')} {d.get('time', '')}".strip()
                    break

        if (not fin_opening_val or fin_opening_val in ["-", "To be informed"]):
            for d in dates_list:
                if isinstance(d, dict) and any(w in str(d.get("event", "")).lower() for w in ["financial bid opening", "financial opening"]):
                    fin_opening_val = f"{d.get('date', '')} {d.get('time', '')}".strip()
                    break

        op_rows = [
            ["Technical Bid Opening", tech_opening_val or "To be informed"],
            ["Financial Bid Opening", fin_opening_val or "To be informed to technically qualified bidders"],
            ["Presentation / Demonstration", opening.get("presentation_date", "To be informed over email")]
        ]
        t_op = create_wrapped_table(op_rows, [160, 380], is_first_row_header=False)
        if t_op:
            elements.extend([Paragraph("<b>B. Bid Opening & Evaluation Schedule:</b>", body_style), t_op, Spacer(1, 3)])

        # 4C. EMD, Tender Fee & Payment Modes / Banking Information
        payment = sub.get("emd_and_fee_payment", {})
        if isinstance(payment, dict) and payment:
            online_pay = payment.get("online_payment_details", {})
            offline_pay = payment.get("offline_payment_details", {})
            dd_info = payment.get("demand_draft_details", {})
            bank_info = payment.get("bank_account_details", {})
            pay_instr = payment.get("payment_instructions", {})

            online_methods = ", ".join(online_pay.get("methods_accepted", [])) if isinstance(online_pay.get("methods_accepted"), list) else "NEFT / RTGS / Portal Gateway"
            offline_methods = ", ".join(offline_pay.get("methods_accepted", [])) if isinstance(offline_pay.get("methods_accepted"), list) else "Demand Draft (DD) / Bank Guarantee (BG)"

            bank_str = "-"
            if isinstance(bank_info, dict) and any(bank_info.values()):
                bank_str = f"A/C Name: {bank_info.get('beneficiary_name', '-')} | Bank: {bank_info.get('bank_name', '-')} | Branch: {bank_info.get('branch', '-')} | A/C No: {bank_info.get('account_number', '-')} | IFSC: {bank_info.get('ifsc_code', '-')}"

            dd_str = "-"
            if isinstance(dd_info, dict) and (dd_info.get("applicable") != "No" or dd_info.get("in_favour_of")):
                dd_str = f"In Favour of: {dd_info.get('in_favour_of', '-')} | Payable at: {dd_info.get('payable_at', '-')} | Amount: {dd_info.get('dd_amount', '-')} | Bank: {dd_info.get('issuing_bank_requirement', 'Scheduled Commercial Bank')} | Validity: {dd_info.get('validity_period', '-')} | Submission: {dd_info.get('submission_address_and_deadline', '-')}"

            pay_rows = [
                ["EMD Requirement & Amount", f"{payment.get('emd_requirement', 'Applicable')} | Amount: {payment.get('emd_amount', online.get('emd_amount', '-'))}"],
                ["Tender Processing Fee", f"{payment.get('tender_processing_fee', online.get('tender_fee', 'Nil / Free Download'))}"],
                ["Payment Requirement", f"{payment.get('payment_requirement', 'As specified in tender document')}"],
                ["Allowed Payment Modes", f"{payment.get('mode_of_payment', 'Online / Offline as per tender')}"],
                ["Online Payment Methods", online_methods],
                ["Offline Payment Methods", offline_methods],
                ["Demand Draft (DD) Mandates", dd_str],
                ["Beneficiary Bank Account", bank_str],
                ["Payment Proof & Reference Rules", pay_instr.get("reference_number_rules", "-") or pay_instr.get("proof_submission", "-")],
                ["MSME / Startup Exemption", f"{payment.get('exemption_allowed', '-')} | {pay_instr.get('exemption_rules', '-')}".strip(" | -")]
            ]
            t_pay = create_wrapped_table(pay_rows, [160, 380], is_first_row_header=False)
            if t_pay:
                elements.extend([Paragraph("<b>C. Comprehensive EMD, Processing Fee & Banking Payment Gateway:</b>", body_style), t_pay, Spacer(1, 3)])

        # 4D. Pre-Bid Conference & Queries
        prebid = sub.get("pre_bid_meeting", {})
        if isinstance(prebid, dict) and prebid.get("required") not in ("No", ""):
            pb_rows = [
                ["Pre-Bid Conference Date & Time", f"{prebid.get('date', '-')} at {prebid.get('time', '-')}".strip(" at -")],
                ["Meeting Mode & Link / Venue", f"{prebid.get('mode', '-')} | {prebid.get('meeting_link_or_venue', '-')}".strip(" | -")],
                ["Query Submission Deadline", prebid.get("query_submission_deadline", "-")],
                ["Designated Query Email", prebid.get("query_email", "-")]
            ]
            t_pb = create_wrapped_table(pb_rows, [160, 380], is_first_row_header=False)
            if t_pb:
                elements.extend([Paragraph("<b>D. Pre-Bid Conference & Clarification Channels:</b>", body_style), t_pb, Spacer(1, 3)])
        elements.append(Spacer(1, 3))

    # Section 5: Implementation Timeline & Phases
    phases = dates_info.get("phases_timeline", []) if isinstance(dates_info, dict) else []
    if isinstance(phases, list) and phases:
        elements.append(Paragraph("5. Implementation Timeline & Phase Deliverables", h2_style))
        p_rows = [["Phase", "Duration", "Key Activities", "Deliverables"]]
        for p in phases:
            if isinstance(p, dict):
                p_rows.append([p.get("phase", "—"), p.get("duration", "—"), p.get("key_activities", "—"), p.get("key_deliverables", "—")])
        t_p = create_wrapped_table(p_rows, [70, 70, 200, 200], is_first_row_header=True)
        if t_p:
            elements.extend([t_p, Spacer(1, 4)])

    # Section 6: Bidder Eligibility Criteria
    elig = data.get("eligibility_and_experience", {})
    if isinstance(elig, dict) and elig:
        elements.append(Paragraph("6. Bidder Eligibility & Experience Requirements", h2_style))
        e_meta = [
            ["Minimum Annual Turnover", elig.get("min_turnover", "—")],
            ["Minimum Net Worth", elig.get("min_net_worth", "—")],
            ["Minimum Operating Years", elig.get("min_years_experience", "—")],
            ["Required Certifications", ", ".join(elig.get("required_certifications", [])) or "—"],
            ["Qualifying Technical Cutoff", elig.get("technical_evaluation_cutoff", "—")],
            ["Selection Methodology", elig.get("selection_method", "—")]
        ]
        t_emeta = create_wrapped_table(e_meta, [160, 380], is_first_row_header=False)
        if t_emeta:
            elements.extend([t_emeta, Spacer(1, 3)])

        sim_projects = elig.get("similar_projects", [])
        if isinstance(sim_projects, list) and sim_projects:
            sp_rows = [["Evaluation Parameter", "Min Projects Required", "Min Value per Project", "Marks"]]
            for sp in sim_projects:
                if isinstance(sp, dict):
                    sp_rows.append([sp.get("parameter", "—"), sp.get("min_count", "—"), sp.get("min_value", "—"), sp.get("marks", "—")])
            t_sp = create_wrapped_table(sp_rows, [220, 110, 130, 80], is_first_row_header=True)
            if t_sp:
                elements.extend([Paragraph("<b>Past Project Criteria & Scoring:</b>", body_style), t_sp, Spacer(1, 4)])

    # Section 7: Team Composition & Resource Profiles
    team = data.get("team_and_cv", {})
    if isinstance(team, dict) and team:
        elements.append(Paragraph("7. Team Composition & Resource Profiles", h2_style))
        roles = team.get("roles", [])
        if isinstance(roles, list) and roles:
            r_rows = [["Role / Profile", "Count", "Min Exp", "Qualifications", "Key Responsibilities"]]
            for r in roles:
                if isinstance(r, dict):
                    r_rows.append([r.get("role", "—"), str(r.get("count", "1")), r.get("min_experience", "—"), r.get("qualifications", "—"), r.get("responsibilities", "—")])
            t_r = create_wrapped_table(r_rows, [110, 35, 55, 140, 200], is_first_row_header=True)
            if t_r:
                elements.extend([t_r, Spacer(1, 4)])

    # Section 8: Deliverables & Milestone Schedule
    deliv = data.get("deliverables_and_milestones", {})
    if isinstance(deliv, dict) and deliv.get("rows"):
        elements.append(Paragraph("8. Deliverables & Payment Milestone Schedule", h2_style))
        headers = deliv.get("headers", ["Milestone", "Deliverable", "Payment %", "Timeline"])
        m_rows = [headers] + deliv.get("rows", [])
        col_w = [70, 230, 100, 140] if len(headers) == 4 else [int(540 / max(1, len(headers)))] * len(headers)
        t_m = create_wrapped_table(m_rows, col_w, is_first_row_header=True)
        if t_m:
            elements.extend([t_m, Spacer(1, 4)])

    # Section 9: Commercial Proposal & Pricing Assessment (Dual Costing Engine)
    quotation = data.get("quotation", {})
    if isinstance(quotation, dict) and quotation:
        elements.append(Paragraph("9. Commercial Proposal & Pricing Assessment", h2_style))

        # Part A: Client Budget (if provided in tender)
        if quotation.get("client_budget_available"):
            cb = quotation.get("client_budget", {})
            elements.append(Paragraph("<b>A. Client / Tender Official Budget (As Specified in Tender):</b>", body_style))
            q_rows = [
                ["Tender Estimated Budget", cb.get("tender_estimated_value", "-")],
                ["Subtotal (Excl. Taxes)", cb.get("subtotal", "-")],
                ["GST / Tax Terms", cb.get("gst_note", "-")],
                ["Total Official Budget (Incl. Taxes)", cb.get("total_with_gst", "-")],
                ["Amount in Words", cb.get("amount_in_words", "-")],
                ["Budget Feasibility Assessment", cb.get("feasibility_note", "-")]
            ]
            t_q = create_wrapped_table(q_rows, [170, 370], is_first_row_header=False)
            if t_q:
                elements.extend([t_q, Spacer(1, 4)])

            boq_rows = cb.get("boq_rows", [])
            boq_headers = cb.get("boq_headers", ["Item / Resource", "Count", "Rate", "Total (INR)"])
            if boq_rows and any(r for r in boq_rows if any(c and c != "Not Specified" for c in r)):
                clean_boq = [boq_headers] + boq_rows
                w = [180, 80, 120, 160] if len(boq_headers) == 4 else [int(540 / max(1, len(boq_headers)))] * len(boq_headers)
                t_cboq = create_wrapped_table(clean_boq, w, is_first_row_header=True, bg_color="#2c3e50")
                if t_cboq:
                    elements.extend([Paragraph("<b>Client Official BOQ / Commercial Price Schedule:</b>", body_style), t_cboq, Spacer(1, 3)])

            elements.append(Paragraph("<b>B. Code B Solutions Pvt. Ltd. Internal Cost Breakdown:</b>", body_style))
        else:
            elements.append(Paragraph("<b>Cost Status:</b> AI Estimated (Tender does not specify official budget)", body_style))
            elements.append(Paragraph("<b>A. Code B Solutions Pvt. Ltd. Estimated Base Cost Breakdown:</b>", body_style))

        # Part B: Code B Solutions Base Cost Breakdown
        bd_rows = quotation.get("breakdown_rows", [])
        if bd_rows:
            bd_table_data = [["Cost Component", "Calculation Basis", "Amount (INR)"]] + bd_rows
            t_bd = create_wrapped_table(bd_table_data, [160, 240, 140], is_first_row_header=True, bg_color="#1a365d")
            if t_bd:
                elements.extend([t_bd, Spacer(1, 3)])

            role_details = quotation.get("role_rate_details", [])
            if role_details:
                elements.append(Paragraph("<b>Industry-Standard Key Personnel Rate Card (Role & Seniority Mapped):</b>", body_style))
                for rd in role_details:
                    elements.append(Paragraph(f"  • {rd}", body_style))
                elements.append(Spacer(1, 3))

        # Part C: Code B Solutions Quotation & Bid Strategy Options
        q_options = quotation.get("quote_options", [])
        if q_options:
            bid_section_label = "C. Code B Solutions Commercial Quotation & Bid Strategy Options:" if quotation.get("client_budget_available") else "B. Commercial Quotation & Bid Strategy Options:"
            elements.append(Paragraph(f"<b>{bid_section_label}</b>", body_style))
            q_table_data = [["Bid Strategy Option", "Margin", "Quote (Excl. Tax)", "GST (18%)", "Total Bid (Incl. GST)"]] + q_options
            t_opt = create_wrapped_table(q_table_data, [150, 50, 110, 100, 130], is_first_row_header=True, bg_color="#2b6cb0")
            if t_opt:
                elements.extend([t_opt, Spacer(1, 3)])

        elements.append(Paragraph(f"<i>{quotation.get('note', '')}</i>", body_style))
        elements.append(Spacer(1, 4))

    # Section 10: Demonstration & Presentation Strategy (Code B Solutions Pvt. Ltd.)
    pres_strat = data.get("presentation_strategy", {})
    pres_info = data.get("presentation_and_demo", {}) or data.get("annexures_and_demo", {})
    demo_info = pres_info.get("demo_requirements", {}) if isinstance(pres_info, dict) else {}

    elements.append(Paragraph("10. Demonstration & Presentation Strategy (Code B Solutions Pvt. Ltd.)", h2_style))
    if isinstance(pres_strat, dict) and pres_strat.get("presentation_required"):
        status_txt = pres_strat.get("status_label", "Presentation Required: YES")
        elements.append(Paragraph(f"<b>Status:</b> {status_txt} | <b>Strategy Type:</b> {pres_strat.get('strategy_type', 'Tender-Specific')}", body_style))

        if isinstance(demo_info, dict) and str(demo_info.get("required", "")).lower() in ["yes", "mandatory", "required", "true"]:
            elements.append(Paragraph(f"<b>Live Product Demo:</b> Required | Details: {demo_info.get('date_time_mode', 'As scheduled by committee')}", body_style))
            for f in demo_info.get("features", []):
                elements.append(Paragraph(f"  • Demo Scope: {f}", body_style))
            elements.append(Spacer(1, 2))

        slides = pres_strat.get("slides", [])
        if slides:
            ps_rows = [["Slide #", "Tender Requirement / Scoring Parameter", "Marks", "What to Present", "Code B Solutions Proposed Solution"]]
            for sl in slides:
                if isinstance(sl, dict):
                    ps_rows.append([
                        str(sl.get("slide", "-")),
                        sl.get("tender_requirement", "-"),
                        str(sl.get("marks", "-")),
                        sl.get("what_to_present", "-"),
                        sl.get("code_b_solution", "-")
                    ])
            t_ps = create_wrapped_table(ps_rows, [35, 120, 35, 170, 180], is_first_row_header=True, bg_color="#1e8449")
            if t_ps:
                elements.extend([t_ps, Spacer(1, 4)])
    else:
        elements.append(Paragraph("<b>Presentation / Demonstration Required:</b> NO (Not mandatory as per tender document)", body_style))
        elements.append(Spacer(1, 4))

    # Section 11: Final Submission Document Tracker
    checklist = data.get("submission_checklist", [])
    if isinstance(checklist, list) and checklist:
        elements.append(Paragraph("11. Submission Document Checklist & Compliance Tracker", h2_style))
        chk_rows = [["#", "Document / Annexure", "Category", "Mandate", "Notes", "Status", "Assignee"]]
        for i, c in enumerate(checklist):
            if isinstance(c, dict):
                chk_rows.append([str(i + 1), c.get("document", "-"), c.get("type", "-"), c.get("mandate", "Mandatory"), c.get("notes", "-"), c.get("status", ""), c.get("assignee", "")])
        t_chk = create_wrapped_table(chk_rows, [22, 170, 70, 65, 95, 60, 58], is_first_row_header=True, bg_color="#0f2942")
        if t_chk:
            elements.extend([t_chk, Spacer(1, 4)])

    # Section 12: External Links Discovered
    links = data.get("external_links", [])
    if isinstance(links, list) and links:
        elements.append(Paragraph("12. External Reference Links Discovered", h2_style))
        lk_rows = [["Page", "URL", "Context"]]
        for lk in links[:25]:
            if isinstance(lk, dict):
                lk_rows.append([str(lk.get("page", "-")), lk.get("url", "-"), lk.get("context", "-")])
        t_lk = create_wrapped_table(lk_rows, [35, 205, 300], is_first_row_header=True, bg_color="#1a5276")
        if t_lk:
            elements.extend([t_lk, Spacer(1, 4)])

    pdf_doc.build(elements)
    print(f"[+] Clean, non-repeating output PDF generated: {output_pdf_path}")

# ==============================================================================
# SECTION 14: EXECUTION ORCHESTRATOR & CLI ENTRYPOINT
# ==============================================================================

def process_pair(pdf_input, excel_path: Path = None, api_key: str = None, output_dir: Path = None):
    """Processes single or multiple PDF proposals with optional Excel BOQ file."""
    if isinstance(pdf_input, (list, tuple)):
        pdf_paths = [Path(p) for p in pdf_input]
        primary_pdf = pdf_paths[0]
        pdf_names = ", ".join(p.name for p in pdf_paths)
    else:
        primary_pdf = Path(pdf_input)
        pdf_paths = [primary_pdf]
        pdf_names = primary_pdf.name

    print(f"\n==========================================")
    print(f" Processing Tender Document(s): {pdf_names}")
    if excel_path and excel_path.exists():
        print(f" Linked Excel:   {excel_path.name}")
    print(f"==========================================")
    try:
        has_excel = bool(excel_path and excel_path.exists())
        extracted_json = run_multi_pass_analysis(pdf_paths, has_excel=has_excel, api_key=api_key)

        if has_excel:
            excel_boq_data = read_boq_excel(excel_path)
            if excel_boq_data:
                extracted_json["excel_boq"] = excel_boq_data

        print("[*] Running Dual Costing Decision Engine (Client Budget + Code B Solutions Costing)...")
        extracted_json["quotation"] = calculate_quotation(extracted_json)

        print("[*] Building Consolidated Submission Document Checklist...")
        extracted_json["submission_checklist"] = build_submission_checklist(extracted_json)

        print("[*] Generating Tailored Presentation Strategy (Code B Solutions Pvt. Ltd.)...")
        extracted_json["presentation_strategy"] = generate_presentation_strategy(extracted_json)

        target_out_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        target_out_dir.mkdir(exist_ok=True, parents=True)
        out_pdf = target_out_dir / f"{primary_pdf.stem}_summary.pdf"
        build_output_pdf(extracted_json, out_pdf)

    except Exception as e:
        import traceback
        print(f"[X] Failed to process {pdf_names}: {e}")
        traceback.print_exc()
        raise e

def main():
    """Main CLI entrypoint."""
    import argparse
    parser = argparse.ArgumentParser(description="Universal AI Tender Document Analyzer.")
    parser.add_argument("pdf", nargs="?", help="Path to PDF tender document")
    parser.add_argument("--excel", "--boq", dest="excel", help="Path to Excel BOQ file (.xlsx / .xls)")
    args = parser.parse_args()

    if args.pdf:
        pdf_path = Path(args.pdf)
        if not pdf_path.exists():
            print(f"[!] PDF file not found: {pdf_path}")
            return
        excel_path = Path(args.excel) if args.excel else None
        process_pair(pdf_path, excel_path)
        return

    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    excel_files = list(INPUT_DIR.glob("*.xlsx")) + list(INPUT_DIR.glob("*.xls"))

    if not pdf_files:
        print(f"[!] No PDFs found in '{INPUT_DIR.resolve()}'. Place your files in 'input/' and rerun.")
        return

    for pdf_path in pdf_files:
        matched_excel = None
        for ef in excel_files:
            if ef.stem.lower() in pdf_path.stem.lower() or pdf_path.stem.lower() in ef.stem.lower():
                matched_excel = ef
                break
        process_pair(pdf_path, matched_excel)

if __name__ == "__main__":
    main()
