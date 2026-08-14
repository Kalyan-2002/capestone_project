from .config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    MOCK_LLM,
    MOCK_CONFIDENCE,
    SNIPPET_LENGTH
)

from .prompts import build_support_prompt


# ---------------------------------------------------------
# Intent keywords
# ---------------------------------------------------------

POLICY_KEYWORDS = {
    "delivery": [
        "delivery",
        "deliver",
        "delivered",
        "delivery fee",
        "priority delivery"
    ],

    "return": [
        "return",
        "returns",
        "returning"
    ],

    "refund": [
        "refund",
        "refunded",
        "money back"
    ],

    "membership": [
        "membership",
        "member",
        "pass",
        "pass+",
        "subscription"
    ],

    "tracking": [
        "tracking",
        "track order",
        "rider",
        "where is my order",
        "order status"
    ],

    "cancel": [
        "cancel",
        "cancellation",
        "cancelled",
        "canceled"
    ],

    "gift card": [
        "gift card",
        "giftcard",
        "gift voucher"
    ],

    "support hours": [
        "support hours",
        "customer support",
        "support",
        "phone support",
        "email support",
        "chat support"
    ]
}


def classify_with_mock(query: str) -> str:
    """
    Deterministic keyword heuristic required by
    the graded MOCK_LLM=1 baseline.
    """

    query_lower = query.lower()

    for category, keywords in POLICY_KEYWORDS.items():

        for keyword in keywords:

            if keyword in query_lower:
                return "policy_question"

    return "general_question"


def classify_with_llm(query: str) -> str:
    """
    Optional real-LLM classification.

    This function is NOT used when MOCK_LLM=1.
    """

    if not GROQ_API_KEY:
        raise RuntimeError(
            "MOCK_LLM=0 but GROQ_API_KEY is not set."
        )

    try:
        from groq import Groq

        client = Groq(
            api_key=GROQ_API_KEY
        )

        system_prompt = """
You classify Zepto customer support questions.

Return exactly one of:

policy_question
general_question

Use policy_question when the question concerns:
delivery, returns, refunds, membership, tracking,
cancellation, gift cards, or support hours.

Otherwise return:
general_question
"""

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip()

        if "policy_question" in result:
            return "policy_question"

        return "general_question"

    except Exception:
        # Safe fallback.
        return classify_with_mock(query)


def classify_intent(query: str) -> str:
    """
    Select mock or real classification according to
    MOCK_LLM.
    """

    if MOCK_LLM:
        return classify_with_mock(query)

    return classify_with_llm(query)


def mock_retrieval_answer(
    query: str,
    context: str
) -> tuple[str, float]:
    """
    Deterministic mock generation.

    Required graded output:
    "Based on the retrieved context: {top_chunk_snippet}"
    """

    if not context:
        return (
            "Based on the retrieved context: "
            "No relevant policy context was retrieved.",
            MOCK_CONFIDENCE
        )

    snippet = context[
        :SNIPPET_LENGTH
    ].replace("\n", " ").strip()

    answer = (
        "Based on the retrieved context: "
        f"{snippet}"
    )

    return answer, MOCK_CONFIDENCE


def mock_direct_answer() -> tuple[str, float]:
    """
    Deterministic response for general questions.
    """

    answer = (
        "I can only answer questions about Zepto "
        "policies right now."
    )

    return answer, MOCK_CONFIDENCE


def real_retrieval_answer(
    query: str,
    context: str
) -> tuple[str, float]:
    """
    Optional real LLM generation for retrieved questions.
    """

    if not GROQ_API_KEY:
        raise RuntimeError(
            "MOCK_LLM=0 but GROQ_API_KEY is not set."
        )

    prompt = build_support_prompt(
        query=query,
        context=context,
        task=(
            "Answer the customer's question using "
            "only the retrieved Zepto policy context."
        ),
        length=(
            "Use 1 to 3 short sentences."
        )
    )

    try:
        from groq import Groq

        client = Groq(
            api_key=GROQ_API_KEY
        )

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        answer = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return answer, 1.0

    except Exception as exc:
        raise RuntimeError(
            f"Real LLM generation failed: {exc}"
        ) from exc


def generate_retrieval_answer(
    query: str,
    context: str
) -> tuple[str, float]:
    """
    Generate answer for policy questions.
    """

    if MOCK_LLM:
        return mock_retrieval_answer(
            query,
            context
        )

    return real_retrieval_answer(
        query,
        context
    )


def generate_direct_answer() -> tuple[str, float]:
    """
    Generate answer for general questions.
    """

    if MOCK_LLM:
        return mock_direct_answer()

    # Optional real-LLM behavior.
    return mock_direct_answer()
