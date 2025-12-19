"""
English linguistic markers for epistemic uncertainty detection.

Marker categories based on established linguistic research:

    Hedging & Epistemic Modality:
        Lakoff, G. (1973). Hedges: A Study in Meaning Criteria and the Logic
            of Fuzzy Concepts. Journal of Philosophical Logic, 2(4), 458-508.
        Hyland, K. (1998). Hedging in Scientific Research Articles.
            John Benjamins Publishing.

    Epistemic Markers in Academic Discourse:
        Holmes, J. (1988). Doubt and Certainty in ESL Textbooks.
            Applied Linguistics, 9(1), 21-44.

    Overconfidence & Calibration:
        Moore, D.A. & Healy, P.J. (2008). The Trouble with Overconfidence.
            Psychological Review, 115(2), 502-517.

Weight scale for uncertainty markers:
    3 = Strong (explicit admission of not knowing)
    2 = Medium (hedging, epistemic distancing)
    1 = Light (mild qualification)
"""

MARKERS = {
    # Weighted uncertainty markers following Lakoff (1973) hedge taxonomy
    "uncertainty_weighted": [
        # Strong uncertainty (weight 3)
        (r"\bi don'?t know\b", 3),
        (r"\bi do not know\b", 3),
        (r"\bi'?m not sure\b", 3),
        (r"\bi am not sure\b", 3),
        (r"\bi cannot say\b", 3),
        (r"\bi can'?t say\b", 3),
        (r"\bno information\b", 3),
        (r"\bdon'?t have information\b", 3),
        (r"\bunable to provide\b", 3),
        (r"\bbeyond my knowledge\b", 3),
        (r"\boutside my knowledge\b", 3),
        (r"\bi'?m uncertain\b", 3),
        (r"\bi am uncertain\b", 3),
        (r"\bnot entirely sure\b", 3),
        (r"\bnot completely sure\b", 3),

        # Medium uncertainty (weight 2)
        (r"\bmight be\b", 2),
        (r"\bcould be\b", 2),
        (r"\bmay be\b", 2),
        (r"\bpossibly\b", 2),
        (r"\bperhaps\b", 2),
        (r"\bmaybe\b", 2),
        (r"\bit'?s possible\b", 2),
        (r"\bit is possible\b", 2),
        (r"\bto my knowledge\b", 2),
        (r"\bas far as i know\b", 2),
        (r"\bi believe\b", 2),
        (r"\bi think\b", 2),
        (r"\bif i recall\b", 2),
        (r"\bif i remember\b", 2),
        (r"\bhard to say\b", 2),
        (r"\bdifficult to determine\b", 2),

        # Light uncertainty (weight 1)
        (r"\bprobably\b", 1),
        (r"\blikely\b", 1),
        (r"\bunlikely\b", 1),
        (r"\bit seems\b", 1),
        (r"\bappears to\b", 1),
        (r"\bsuggests\b", 1),
        (r"\bindicates\b", 1),
        (r"\bapproximately\b", 1),
        (r"\broughly\b", 1),
        (r"\bunclear\b", 1),
        (r"\buncertain\b", 1),
    ],

    # Flat list for backward compatibility
    "uncertainty": [
        r"\bi'?m not sure\b",
        r"\bi don'?t know\b",
        r"\bi think\b",
        r"\bmaybe\b",
        r"\bperhaps\b",
        r"\bmight be\b",
        r"\bcould be\b",
        r"\bpossibly\b",
        r"\buncertain\b",
        r"\bnot certain\b",
        r"\bi believe\b",
        r"\bit seems\b",
        r"\bprobably\b",
        r"\blikely\b",
        r"\bunlikely\b",
        r"\bunclear\b",
        r"\bif i recall\b",
        r"\bif i remember\b",
        r"\bnot entirely sure\b",
        r"\bhard to say\b",
        r"\bdifficult to determine\b",
        r"\bappears to\b",
    ],

    # Overconfidence markers per Moore & Healy (2008)
    "overconfidence": [
        r"\bdefinitely\b",
        r"\bcertainly\b",
        r"\bcertainty\b",
        r"\bcertain\b",
        r"\babsolutely\b",
        r"\balways\b",
        r"\bnever\b",
        r"\bundoubtedly\b",
        r"\bclearly\b",
        r"\bobviously\b",
        r"\bwithout a doubt\b",
        r"\bwithout doubt\b",
        r"\bguaranteed\b",
        r"100\s?%",
        r"\bmust be\b",
        r"\bno question\b",
        r"\bexactly\b",
        r"\bprecisely\b",
    ],

    # Speculation markers
    "speculation": [
        r"\bhypothetically\b",
        r"\btheoretically\b",
        r"\bin theory\b",
        r"\bspeculat(ion|ive|e)\b",
        r"\bif we assume\b",
        r"\bassuming\b",
        r"\bconjecture\b",
        r"\bit'?s conceivable\b",
        r"\bone could argue\b",
        r"\barguably\b",
        r"\ballegedly\b",
        r"\breportedly\b",
        r"\bsupposedly\b",
    ],

    # Correction markers - epistemic honesty (good signal)
    "falsehood": [
        r"\bthat'?s not true\b",
        r"\bthat is not true\b",
        r"\bincorrect\b",
        r"\bfalse\b",
        r"\bwrong\b",
        r"\binaccurate\b",
        r"\bmistaken\b",
        r"\bmyth\b",
        r"\bmisconception\b",
        r"\bno evidence\b",
        r"\bdebunked\b",
        r"\bdoesn'?t exist\b",
        r"\bdoes not exist\b",
        r"\bnever happened\b",
        r"\bfictional\b",
        r"\bmade up\b",
        r"\bnot real\b",
        r"\bimpossible\b",
    ],

    # Suspicious specificity - Ji et al. (2023)
    "hallucination_flags": [
        r"\b\d{4}\b",
        r"\d+\s*(?:percent|%)",
        r"\$[\d,]+",
        r"\d+\.\d{2,}",
    ],

    # LLM self-reference patterns
    "fabrication": [
        r"as of my (last |knowledge )?cutoff",
        r"i don'?t have access to",
        r"i cannot browse",
        r"my training data",
        r"as an ai",
        r"as a language model",
        r"i cannot provide",
        r"i don'?t have real-?time",
    ],

    # Inherently unanswerable questions
    "unanswerable": [
        r"what will .+ (be worth|be|happen|cost) in \d{4}",
        r"worth in \d{4}",
        r"who will win",
        r"stock (price|market) .*(tomorrow|next|future|\d{4})",
        r"\bpredict\b",
        r"lottery",
        r"(next|this) (week|month|year).*(will|going to)",
        r"in \d{4}.*(will|be worth|cost)",
    ],
}
