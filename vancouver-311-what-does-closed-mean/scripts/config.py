"""Shared definitions: analyst-defined outcome mapping, flag rules, focus-family candidates.

Every grouping here is an ANALYST-DEFINED INTERPRETATION of the City's published
values. The original status and closure_reason values are always preserved.
"""
import re

TZ = "America/Vancouver"
AUTHOR = "Abhijit Mishra"   # change here; used by the report and the workbook README

G1 = "1. Service recorded as provided"
G2 = "2. Work assigned, referred or continuing"
G3 = "3. No service or no action recorded"
G4 = "4. Insufficient information / could not proceed"
G5 = "5. Unknown or N/A"
G6 = "6. Other - requires review"
GROUPS = [G1, G2, G3, G4, G5, G6]
SHORT = {G1: "Service provided", G2: "Assigned / referred / continuing", G3: "No service or no action",
         G4: "Insufficient info / unreachable", G5: "Unknown or N/A", G6: "Other - review"}

# closure_reason -> (outcome_group, outcome_subgroup, rationale, validation question)
MAPPING = {
    "Service provided": (G1, "Service provided",
        "Wording records that the service was provided.",
        "Does 'Service provided' mean the requested work was completed, or that a response was given?"),
    "Further action has been planned": (G2, "Further work planned",
        "Wording indicates work is still to come after the case was closed.",
        "Where is completion of the planned work recorded, and is it linked back to this case?"),
    "Assigned to inspector": (G2, "Assigned to inspector",
        "Wording indicates the case closed when assigned; the inspection outcome is not shown.",
        "Is the inspection tracked in another case or system, and is its outcome reportable?"),
    "Dispatched to Crew": (G2, "Dispatched to crew",
        "Wording indicates the case closed at dispatch; the crew outcome is not shown.",
        "Is crew completion recorded anywhere that can be linked to this case?"),
    "Referred to another service group": (G2, "Referred to another group",
        "Wording indicates a handoff; the receiving group's outcome is not shown.",
        "Does a referral create a new case, and can the two be linked for reporting?"),
    "Closed automatically and sent to service group": (G2, "Auto-closed and routed",
        "Wording indicates the case closed on routing, before any recorded action.",
        "Which system or team holds the work after automatic routing, and how is it closed?"),
    "Reviewed and no action planned": (G3, "Reviewed - no action",
        "Wording records a review with no action planned.",
        "What review criteria lead to 'no action', and are residents told why?"),
    "Issue not found or inaccessible": (G3, "Issue not found / inaccessible",
        "Wording records that the issue could not be found or reached.",
        "Would better location detail at intake reduce these outcomes?"),
    "Not a city provided service / jurisdiction": (G3, "Not City service / jurisdiction",
        "Wording records that the request is outside City responsibility.",
        "Could intake identify out-of-jurisdiction requests earlier?"),
    "Outside of Parameters (Sanitation)": (G3, "Outside service parameters",
        "Sanitation-specific value that appears to mean the request fell outside service criteria.",
        "What are the parameters, and is this an outcome or a classification issue?"),
    "Contaminated (Sanitation)": (G3, "Contaminated (sanitation)",
        "Sanitation-specific value that appears to mean the request could not be serviced as submitted.",
        "What happens next for the resident when this reason is used?"),
    "Insufficient info": (G4, "Insufficient information",
        "Wording records that the request lacked information needed to proceed.",
        "Which missing information fields cause this most often?"),
    "Customer unreachable": (G4, "Customer unreachable",
        "Wording records that the requester could not be contacted.",
        "Is contact attempted before closure, and how many attempts are expected?"),
    "Unknown": (G5, "Unknown",
        "The published value does not describe an outcome.",
        "Is 'Unknown' a system default for specific intake paths, and what is the real outcome?"),
    "N/A": (G5, "N/A",
        "The published value does not describe an outcome (see counts: in 2025 it appears on open cases).",
        "Is 'N/A' simply the placeholder for cases that are not yet closed?"),
    "Alternate Service Required": (G6, "Alternate service required",
        "Ambiguous: could mean redirection outside the City or a different City service.",
        "Does this mean the resident was redirected elsewhere, or that another City service will act?"),
    "Information received": (G6, "Information received",
        "Ambiguous: could record that information was provided or received.",
        "Is this an information-only outcome equivalent to 'Service provided'?"),
}

# Administrative/internal-SOUNDING request types: transparent name-based rule.
# "transfer case" is matched as a phrase so that "Disposal Facility - Transfer Station
# Inquiry Case" (a facility name) is NOT flagged.
ADMIN_RULE_TEXT = ('Request-type name contains (case-insensitive) "internal", "audit", "tracking", '
                   'or the phrase "transfer case".')
ADMIN_RE = re.compile(r"internal|audit|tracking|transfer case", re.IGNORECASE)

# Focus-family candidates (department, [request types]) for the evidence-based selection.
CANDIDATES = {
    "Street and sidewalk repair": ("ENG - Streets Operations",
        ["Pothole Case", "Street Repair Case", "Sidewalk Repair Case"]),
    "Missed collection": ("ENG - Sanitation Services",
        ["Missed Garbage Bin Pickup Case", "Missed Green Bin Pickup Case"]),
    "Abandoned items": ("ENG - Sanitation Services",
        ["Abandoned Non-Recyclables-Small Case", "Abandoned Non-Recyclables-Large Case",
         "Abandoned Recyclables Case", "Abandoned Mattress Case"]),
    "Bin requests": ("ENG - Sanitation Services",
        ["Garbage Bin Request Case", "Green Bin Request Case"]),
    "City and park trees": ("PR - Urban Forestry", ["City and Park Trees Maintenance Case"]),
    "Private property concerns": ("DBL - Property Use Inspections",
        ["Noise on Private Property Case", "Private Property Concern Case"]),
    "Street lights and signs": ("ENG - Traffic and Electrical Operations and Design",
        ["Street Light Out Case", "Sign Repair Case", "Traffic Signal Repair Case"]),
}
FOCUS_FAMILY = "Street and sidewalk repair"   # set after reviewing the selection matrix
PCTS = (0.50, 0.75, 0.90)
MIN_N_FOR_PERCENTILES = 30
