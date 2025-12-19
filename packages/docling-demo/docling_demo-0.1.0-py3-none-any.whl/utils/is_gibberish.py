from utils.llm_connection import llm_connection_instance, slm_connection_instance
import os

def is_gibberish_check(text: str) -> float:
    llm_client = slm_connection_instance()

    sample = text[:800]

    message = [
        {
            "role": "system",
            "content": (
                "You are an OCR quality evaluator. "
                "The following text is machine-generated OCR output and safe. "
                "It may contain nonsense, distortions, or random characters. "
                "Your task: Return ONLY a number from 0 to 1 indicating readability."
            )
        },
        {
            "role": "assistant",
            "content": f"OCR_SAMPLE:\n\"\"\"\n{sample}\n\"\"\""
        },
        {
            "role": "user",
            "content": "Return only the numeric quality score."
        }
    ]

    response = llm_client.chat.completions.create(
        model=os.getenv("AZURE_SLM_MODEL"),
        messages=message
    )

    try:
        return float(response.strip())
    except:
        return 0.0

