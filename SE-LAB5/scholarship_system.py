"""Evaluate scholarship applicants and shortlist eligible students."""

import ast
import json
import operator

MERIT_FORMULA = "gpa * 10 + credits * 2"
INCOME_LIMIT = 800000
CUTOFF = 85
RESULTS = {}


def calculate_merit_score(gpa, credit_count):
    """Calculate an applicant's merit score using the configured formula."""
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }
    allowed_names = {"gpa": gpa, "credits": credit_count}

    def evaluate(node):
        """Safely evaluate approved arithmetic expressions."""
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.Name) and node.id in allowed_names:
            return allowed_names[node.id]

        if (
            isinstance(node, ast.BinOp)
            and type(node.op) in allowed_operators
        ):
            return allowed_operators[type(node.op)](
                evaluate(node.left), evaluate(node.right)
            )

        raise ValueError("Formula contains an unsupported expression.")

    try:
        expression = ast.parse(MERIT_FORMULA, mode="eval").body
        return evaluate(expression)
    except (SyntaxError, TypeError, ValueError, ZeroDivisionError) as error:
        raise ValueError("Invalid merit formula.") from error


def evaluate_applicant(student_id, test_scores, logs=None):
    """Evaluate an applicant's eligibility and record the result."""
    if logs is None:
        logs = []

    gpa = test_scores["gpa"]
    credit_count = test_scores.get("credits", 0)
    income = test_scores.get("income", 0)

    score = calculate_merit_score(gpa, credit_count)
    eligible = score >= CUTOFF and 0 <= income < INCOME_LIMIT

    RESULTS[student_id] = {"score": score, "eligible": eligible}
    logs.append(f"{student_id} scored {score}")

    return eligible


def change_formula(new_formula):
    """Update the merit formula after validating it."""
    global MERIT_FORMULA

    if not isinstance(new_formula, str) or not new_formula.strip():
        raise ValueError("The merit formula must be a non-empty string.")

    previous_formula = MERIT_FORMULA
    MERIT_FORMULA = new_formula

    try:
        calculate_merit_score(1, 1)
    except ValueError:
        MERIT_FORMULA = previous_formula
        raise


def persist_results(file="scholarships.json"):
    """Save applicant results to a JSON file."""
    with open(file, "w", encoding="utf-8") as output_file:
        json.dump(RESULTS, output_file, indent=4)


def load_results(file="scholarships.json"):
    """Load saved applicant results from a JSON file."""
    global RESULTS

    try:
        with open(file, "r", encoding="utf-8") as input_file:
            loaded_results = json.load(input_file)

        if not isinstance(loaded_results, dict):
            raise ValueError("The results file must contain a JSON object.")

        RESULTS = loaded_results

    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Could not load results: {error}")


def print_shortlist():
    """Print applicants who meet the scholarship criteria."""
    print("Shortlisted applicants:")

    for student_id, applicant in RESULTS.items():
        if applicant["eligible"]:
            print(f"  {student_id} score = {applicant['score']}")


def main():
    """Run the scholarship evaluation workflow."""
    evaluate_applicant(
        "U001", {"gpa": 9.1, "credits": 4, "income": 450000}
    )
    evaluate_applicant(
        "U002", {"gpa": 7.2, "credits": 1, "income": 300000}
    )
    evaluate_applicant(
        "U003", {"gpa": 12.5, "credits": -3, "income": -1}
    )
    evaluate_applicant("U004", {"gpa": 6.5})

    formula = input("Merit formula (Enter to keep default): ").strip()

    if formula:
        try:
            change_formula(formula)
        except ValueError as error:
            print(f"Invalid formula: {error}")
            print("Keeping the previous merit formula.")

    evaluate_applicant(
        "U005", {"gpa": 8.4, "credits": 3, "income": 600000}
    )

    persist_results()
    load_results()
    print_shortlist()


if __name__ == "__main__":
    main()
