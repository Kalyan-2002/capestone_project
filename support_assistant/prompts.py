
def build_support_prompt(
    query: str,
    context: str,
    task: str = "Answer the customer's Zepto policy question.",
    length: str = "Keep the answer concise and helpful."
) -> str:
    """
    Structured prompt following:

    role -> context -> task -> format -> length

    Includes:
    - explicit negative constraint
    - few-shot example
    """

    prompt = f"""
ROLE:
You are a helpful Zepto customer-support assistant.

CONTEXT:
You may answer policy questions only from the provided
retrieved context.

TASK:
{task}

IMPORTANT CONSTRAINT:
Do not answer using information that is not present
in the provided context. Do not invent Zepto policies,
prices, timings, refunds, membership benefits, or
support procedures.

FORMAT:
Return a direct customer-friendly answer in plain text.

LENGTH:
{length}

FEW-SHOT EXAMPLE:

Example user question:
"How long does a refund take?"

Example context:
"Approved refunds are credited to the original payment
method within 3–5 business days."

Example answer:
"Approved refunds are credited to the original payment
method within 3–5 business days."

END FEW-SHOT EXAMPLE.

CURRENT USER QUERY:
{query}

RETRIEVED CONTEXT:
{context}
"""

    return prompt.strip()
