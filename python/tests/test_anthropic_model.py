import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

def main():
    # Confirm the key is loaded
    ai_api_key = os.environ.get("ANTHROPIC_AI_API_KEY")
    if not ai_api_key:
        raise RuntimeError("ANTHROPIC_AI_API_KEY is not set in your environment variables.")
    
    # Confirm the key is loaded
    ai_model = os.environ.get("ANTHROPIC_AI_MODEL")
    if not ai_model:
        raise RuntimeError("ANTHROPIC_AI_MODEL is not set in your environment variables.")

    client = Anthropic(api_key=ai_api_key)

    print("Model:", ai_model)
    print("Calling Claude…")

    response = client.messages.create(
        model=ai_model,
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": "Say a short sentence confirming that the Anthropic API is working."
            }
        ]
    )

    print("\n--- API Response ---")
    print(response.content[0].text)

if __name__ == "__main__":
    main()