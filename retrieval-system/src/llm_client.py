import os
import openai

_twcc_client: openai.OpenAI | None = None


def _get_twcc_client() -> openai.OpenAI:
    global _twcc_client
    if _twcc_client is None:
        api_key = os.environ.get("TWCC_API_KEY")
        base_url = os.environ.get("TWCC_API_URL", "https://api-ams.twcc.ai/api") + "/models"
        timeout = float(os.environ.get("TWCC_TIMEOUT", "60"))
        max_retries = int(os.environ.get("TWCC_MAX_RETRY", "2"))
        if not api_key:
            raise RuntimeError("TWCC_API_KEY 未設定，請在 .env 中填入 API key。")
        _twcc_client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
    return _twcc_client


def _ask_twcc(question: str, system_prompt: str, max_tokens: int) -> str:
    model = os.environ.get("TWCC_MODEL", "llama3.3-ffm-70b-16k-chat")
    response = _get_twcc_client().chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


def _ask_gemini(question: str, system_prompt: str, max_tokens: int) -> str:
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY 未設定，請在 .env 中填入 Gemini API key。")
    model_name = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=max_tokens,
        ),
    )
    return response.text or ""


def ask(question: str, system_prompt: str, max_tokens: int = 1024) -> str:
    provider = os.environ.get("LLM_PROVIDER", "twcc").lower()
    if provider == "gemini":
        return _ask_gemini(question, system_prompt, max_tokens)
    return _ask_twcc(question, system_prompt, max_tokens)
