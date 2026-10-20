import heapq
import re
from pathlib import Path

from pypdf import PdfReader
from docx import Document


# ============================================================
# AI RESUME SCREENER
# Classical AI Approach
#
# 1. Constraint Satisfaction Problem (CSP)
# 2. Constraint Propagation
# 3. Backtracking Search
# 4. Heuristic Evaluation
# 5. Best-First Search
#
# NO MACHINE LEARNING
# NO DEEP LEARNING
# ============================================================


# ============================================================
# SKILL VOCABULARY
# ============================================================

SKILL_VOCAB = [
    "python",
    "java",
    "c",
    "c++",
    "c#",

    "javascript",
    "typescript",

    "html",
    "css",

    "react",
    "angular",

    "node.js",
    "node",

    "flask",
    "django",

    "sql",
    "mysql",
    "postgresql",
    "mongodb",

    "power bi",
    "tableau",
    "excel",

    "git",
    "github",

    "machine learning",
    "deep learning",

    "data analysis",
    "data structures",
    "algorithms",

    "communication",

    "aws",
    "azure",
    "docker",
    "linux",

    "figma"
]


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize(text):

    if not text:
        return ""

    text = text.lower()

    # Avoid special handling problems
    text = text.replace("c++", "cplusplus")
    text = text.replace("c#", "csharp")

    # Replace unwanted characters with spaces
    text = re.sub(
        r"[^a-z0-9+#.\s]",
        " ",
        text
    )

    # Remove multiple spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# PARSE COMMA-SEPARATED VALUES
# ============================================================

def parse_csv(value):

    if not value:
        return []

    return [
        item.strip().lower()
        for item in value.split(",")
        if item.strip()
    ]


# ============================================================
# RESUME TEXT EXTRACTION
# ============================================================

def extract_text(file_path):

    path = Path(file_path)

    extension = path.suffix.lower()

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if extension == ".pdf":

        reader = PdfReader(
            str(path)
        )

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text


    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    if extension == ".docx":

        document = Document(
            str(path)
        )

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )


    # --------------------------------------------------------
    # TXT
    # --------------------------------------------------------

    if extension == ".txt":

        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )


    return ""


# ============================================================
# EXTRACT NUMBER
# ============================================================

def extract_number(
    pattern,
    text,
    default=0.0
):

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if not match:
        return default

    try:

        return float(
            match.group(1)
        )

    except (ValueError, TypeError):

        return default


# ============================================================
# EXTRACT RESUME INFORMATION
# ============================================================

def extract_resume_data(text):

    normalized = normalize(text)


    # ========================================================
    # CGPA
    # ========================================================

    cgpa = extract_number(

        r"(?:cgpa|gpa)\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)",

        normalized

    )


    # ========================================================
    # EXPERIENCE
    # ========================================================

    experience = extract_number(

        r"(\d+(?:\.\d+)?)\s*\+?\s*"
        r"(?:years?|yrs?)\s*"
        r"(?:of\s*)?"
        r"(?:experience|exp)",

        normalized

    )


    # ========================================================
    # DEGREE
    # ========================================================

    degree = ""

    degree_patterns = [

        (
            "b.e",
            r"\bb\.?\s*e\.?\b"
        ),

        (
            "b.tech",
            r"\bb\.?\s*tech\.?\b"
        ),

        (
            "bca",
            r"\bbca\b"
        ),

        (
            "mca",
            r"\bmca\b"
        ),

        (
            "m.e",
            r"\bm\.?\s*e\.?\b"
        ),

        (
            "m.tech",
            r"\bm\.?\s*tech\.?\b"
        )

    ]


    for degree_name, pattern in degree_patterns:

        if re.search(
            pattern,
            normalized
        ):

            degree = degree_name

            break


    # ========================================================
    # COMPUTER SCIENCE DETECTION
    # ========================================================

    is_cse = bool(

        re.search(
            r"\bcomputer\s+science\b",
            normalized
        )

        or

        re.search(
            r"\bcse\b",
            normalized
        )

        or

        re.search(
            r"computer\s+science\s+and\s+engineering",
            normalized
        )

    )


    # ========================================================
    # EMAIL DETECTION
    # ========================================================

    email_match = re.search(

        r"[\w.+-]+@[\w-]+\.[\w.-]+",

        text

    )

    if email_match:

        email = email_match.group(0)

    else:

        email = ""


    # ========================================================
    # PHONE DETECTION
    # ========================================================

    phone_match = re.search(

        r"(?:\+91[\s-]?)?[6-9]\d{9}",

        text

    )

    if phone_match:

        phone = phone_match.group(0)

    else:

        phone = ""


    # ========================================================
    # SKILL DETECTION
    # ========================================================

    found_skills = []

    for skill in SKILL_VOCAB:

        skill_normalized = normalize(skill)

        # Convert special skill names to searchable forms
        if skill_normalized == "cplusplus":

            pattern = r"(?<![a-z0-9])cplusplus(?![a-z0-9])"

        elif skill_normalized == "csharp":

            pattern = r"(?<![a-z0-9])csharp(?![a-z0-9])"

        else:

            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(skill_normalized)
                + r"(?![a-z0-9])"
            )

        if re.search(
            pattern,
            normalized
        ):

            found_skills.append(skill)


    # ========================================================
    # PROJECT EVIDENCE
    # ========================================================

    project_keywords = [
        "project",
        "developed",
        "application",
        "system",
        "website"
    ]

    project_evidence = (

        sum(
            1
            for word in project_keywords
            if word in normalized
        ) >= 2

    )


    return {

        "email": email,

        "phone": phone,

        "cgpa": cgpa,

        "experience": experience,

        "degree": degree,

        "is_cse": is_cse,

        "skills": sorted(
            set(found_skills)
        ),

        "project_evidence":
            project_evidence

    }


# ============================================================
# CSP
# CONSTRAINT SATISFACTION PROBLEM
# ============================================================

def build_constraints(job):

    return [

        {
            "name": "Education",

            "type": "hard",

            "description":
                f"Degree should match "
                f"{job['degree']}"
        },

        {
            "name": "CGPA",

            "type": "hard",

            "description":
                f"CGPA should be >= "
                f"{job['min_cgpa']}"
        },

        {
            "name": "Experience",

            "type": "hard",

            "description":
                f"Experience should be >= "
                f"{job['min_experience']} years"
        },

        {
            "name": "Required Skills",

            "type": "hard",

            "description":
                "All required skills "
                "should be present"
        }

    ]


# ============================================================
# EDUCATION CONSTRAINT CHECK
# ============================================================

def degree_matches(
    candidate,
    required_degree
):

    required = normalize(
        required_degree
    )

    # No degree requirement
    if not required:

        return True


    candidate_degree = candidate.get(
        "degree",
        ""
    )


    # Candidate degree not detected
    if not candidate_degree:

        return False


    # --------------------------------------------------------
    # CSE requirement
    # --------------------------------------------------------

    if (
        "cse" in required
        or
        "computer science" in required
    ):

        valid_degree = (

            candidate_degree
            in {
                "b.e",
                "b.tech",
                "m.e",
                "m.tech"
            }

        )

        return (

            valid_degree
            and
            candidate.get(
                "is_cse",
                False
            )

        )


    # --------------------------------------------------------
    # General degree requirement
    # --------------------------------------------------------

    return (

        candidate_degree
        in required

    )


# ============================================================
# EVALUATE ONE CONSTRAINT
# ============================================================

def evaluate_constraint(
    candidate,
    job,
    constraint_name
):

    required_skills = parse_csv(
        job["required_skills"]
    )

    candidate_skills = set(
        candidate["skills"]
    )


    # ========================================================
    # EDUCATION
    # ========================================================

    if constraint_name == "Education":

        return degree_matches(

            candidate,

            job["degree"]

        )


    # ========================================================
    # CGPA
    # ========================================================

    if constraint_name == "CGPA":

        return (

            candidate["cgpa"]
            >= float(
                job["min_cgpa"]
            )

        )


    # ========================================================
    # EXPERIENCE
    # ========================================================

    if constraint_name == "Experience":

        return (

            candidate["experience"]
            >= float(
                job["min_experience"]
            )

        )


    # ========================================================
    # REQUIRED SKILLS
    # ========================================================

    if constraint_name == "Required Skills":

        return all(

            skill in candidate_skills

            for skill in required_skills

        )


    return True


# ============================================================
# CONSTRAINT PROPAGATION
# ============================================================

def constraint_propagation(
    candidate,
    job
):

    constraints = build_constraints(
        job
    )

    trace = []

    remaining = list(
        constraints
    )


    # Check constraints one by one
    for constraint in constraints:

        passed = evaluate_constraint(

            candidate,

            job,

            constraint["name"]

        )


        trace.append({

            "constraint":
                constraint["name"],

            "status":
                "PASS"
                if passed
                else
                "FAIL",

            "description":
                constraint["description"]

        })


        # ----------------------------------------------------
        # PROPAGATION
        #
        # If a hard constraint fails,
        # candidate is removed from
        # the feasible solution space.
        # ----------------------------------------------------

        if not passed:

            remaining = [

                item

                for item in remaining

                if item["name"]
                != constraint["name"]

            ]


            return {

                "eligible": False,

                "remaining_constraints":
                    [
                        item["name"]
                        for item in remaining
                    ],

                "trace": trace

            }


    return {

        "eligible": True,

        "remaining_constraints":
            [
                item["name"]
                for item in remaining
            ],

        "trace": trace

    }


# ============================================================
# BACKTRACKING SEARCH
# ============================================================

def backtracking_search(
    candidate,
    job,
    constraints,
    index=0,
    trace=None
):

    if trace is None:

        trace = []


    # ========================================================
    # BASE CASE
    # All constraints satisfied
    # ========================================================

    if index == len(
        constraints
    ):

        trace.append(
            "All constraints satisfied. "
            "Solution found."
        )

        return True, trace


    # Current constraint
    current = constraints[
        index
    ]


    # Check current constraint
    passed = evaluate_constraint(

        candidate,

        job,

        current["name"]

    )


    trace.append(

        f"Checking "
        f"{current['name']}: "
        f"{'PASS' if passed else 'FAIL'}"

    )


    # ========================================================
    # BACKTRACK
    # ========================================================

    if not passed:

        trace.append(

            f"Backtracking from "
            f"{current['name']} "
            f"because the constraint failed."

        )

        return False, trace


    # ========================================================
    # RECURSIVELY CHECK NEXT CONSTRAINT
    # ========================================================

    return backtracking_search(

        candidate,

        job,

        constraints,

        index + 1,

        trace

    )


# ============================================================
# HEURISTIC FUNCTION
# ============================================================

def heuristic_score(
    candidate,
    job
):

    required = parse_csv(
        job["required_skills"]
    )

    preferred = parse_csv(
        job["preferred_skills"]
    )

    candidate_skills = set(
        candidate["skills"]
    )


    # ========================================================
    # REQUIRED SKILLS
    # Maximum = 50 points
    # ========================================================

    if required:

        required_ratio = (

            sum(

                skill in candidate_skills

                for skill in required

            )

            /

            len(required)

        )

    else:

        required_ratio = 1.0


    required_points = (

        required_ratio * 50

    )


    # ========================================================
    # PREFERRED SKILLS
    # Maximum = 20 points
    # ========================================================

    if preferred:

        preferred_ratio = (

            sum(

                skill in candidate_skills

                for skill in preferred

            )

            /

            len(preferred)

        )

    else:

        preferred_ratio = 1.0


    preferred_points = (

        preferred_ratio * 20

    )


    # ========================================================
    # EDUCATION
    # Maximum = 15 points
    # ========================================================

    if degree_matches(

        candidate,

        job["degree"]

    ):

        education_points = 15

    else:

        education_points = 0


    # ========================================================
    # CGPA
    # Maximum = 10 points
    # ========================================================

    min_cgpa = float(
        job["min_cgpa"]
    )


    if min_cgpa <= 0:

        cgpa_points = 10

    elif candidate["cgpa"] >= min_cgpa:

        cgpa_points = 10

    else:

        cgpa_points = max(

            0,

            (
                candidate["cgpa"]
                /
                min_cgpa
            ) * 10

        )


    # ========================================================
    # EXPERIENCE
    # Maximum = 5 points
    # ========================================================

    min_experience = float(
        job["min_experience"]
    )


    if min_experience <= 0:

        experience_points = 5

    elif candidate["experience"] >= min_experience:

        experience_points = 5

    else:

        experience_points = max(

            0,

            (
                candidate["experience"]
                /
                min_experience
            ) * 5

        )


    # ========================================================
    # TOTAL HEURISTIC SCORE
    # ========================================================

    total_score = (

        required_points
        +
        preferred_points
        +
        education_points
        +
        cgpa_points
        +
        experience_points

    )


    return round(

        min(total_score, 100),

        2

    )


# ============================================================
# BEST-FIRST SEARCH
# ============================================================

def best_first_search(
    candidates
):

    priority_queue = []


    # ========================================================
    # CREATE PRIORITY QUEUE
    #
    # Higher heuristic score =
    # Higher priority
    #
    # Negative score is used because
    # Python heapq is a min-heap.
    # ========================================================

    for candidate in candidates:

        heapq.heappush(

            priority_queue,

            (

                -candidate[
                    "heuristic_score"
                ],

                candidate[
                    "filename"
                ],

                candidate

            )

        )


    ordered = []

    order = 1


    # ========================================================
    # BEST-FIRST SEARCH
    # ========================================================

    while priority_queue:

        _, _, candidate = heapq.heappop(
            priority_queue
        )


        candidate[
            "search_order"
        ] = order


        ordered.append(
            candidate
        )


        order += 1


    return ordered


# ============================================================
# SCREEN ONE RESUME
# ============================================================

def screen_one_resume(
    item,
    job
):

    # ========================================================
    # EXTRACT RESUME TEXT
    # ========================================================

    text = extract_text(
        item["path"]
    )


    # ========================================================
    # EXTRACT INFORMATION
    # ========================================================

    candidate = extract_resume_data(
        text
    )


    candidate[
        "filename"
    ] = item["filename"]


    # ========================================================
    # STEP 1
    # CONSTRAINT PROPAGATION
    # ========================================================

    propagation = constraint_propagation(

        candidate,

        job

    )


    # ========================================================
    # STEP 2
    # BACKTRACKING SEARCH
    # ========================================================

    constraints = build_constraints(
        job
    )


    backtracking_ok, backtracking_trace = (

        backtracking_search(

            candidate,

            job,

            constraints

        )

    )


    # ========================================================
    # STEP 3
    # HEURISTIC EVALUATION
    # ========================================================

    score = heuristic_score(

        candidate,

        job

    )


    candidate[
        "heuristic_score"
    ] = score


    # ========================================================
    # FINAL ELIGIBILITY
    # ========================================================

    candidate[
        "eligible"
    ] = (

        propagation["eligible"]
        and
        backtracking_ok

    )


    # ========================================================
    # SAVE AI EXPLANATION
    # ========================================================

    candidate[
        "constraint_trace"
    ] = propagation[
        "trace"
    ]


    candidate[
        "backtracking_trace"
    ] = backtracking_trace


    return candidate


# ============================================================
# MAIN RESUME SCREENING FUNCTION
# ============================================================

def screen_resumes(
    resume_items,
    job
):

    candidates = []


    # ========================================================
    # PROCESS EACH RESUME
    # ========================================================

    for item in resume_items:

        candidate = screen_one_resume(

            item,

            job

        )

        candidates.append(
            candidate
        )


    # ========================================================
    # SEPARATE ELIGIBLE CANDIDATES
    # ========================================================

    eligible = [

        candidate

        for candidate in candidates

        if candidate["eligible"]

    ]


    # ========================================================
    # SEPARATE REJECTED CANDIDATES
    # ========================================================

    rejected = [

        candidate

        for candidate in candidates

        if not candidate["eligible"]

    ]


    # ========================================================
    # BEST-FIRST SEARCH
    #
    # Only eligible candidates are
    # ranked using heuristic score.
    # ========================================================

    ranked = best_first_search(
        eligible
    )


    # ========================================================
    # REJECTED CANDIDATES
    # ========================================================

    for candidate in rejected:

        candidate[
            "search_order"
        ] = None


    # ========================================================
    # FINAL RESULT
    #
    # Eligible candidates first,
    # followed by rejected candidates.
    # ========================================================

    final_results = (

        ranked
        +
        rejected

    )


    return final_results