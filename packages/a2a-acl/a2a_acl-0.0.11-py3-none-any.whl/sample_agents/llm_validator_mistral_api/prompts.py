import os
from mistralai import Mistral


llm_api_key = os.environ["MISTRAL_API_KEY"]
llm_model = "mistral-small-latest"

llm_client = Mistral(api_key=llm_api_key)

failure = "failure"


def log(m):
    print("[LOG] " + m)


def filter(t: str):
    t = t.lower()
    if t.startswith("true"):
        return True
    elif t.startswith("false"):
        return False
    else:
        return None


def ask_llm_for_correctness(spec: str, req: str) -> bool:
    try:
        chat_response = llm_client.chat.complete(
            model=llm_model,
            messages=[
                {
                    "role": "system",
                    "content": "Given a specification of a system, and a requirement,"
                    " evaluate if that requirements is correct with respect to the given specification."
                    + " Answer with True or False, don't explain.",
                },
                {
                    "role": "user",
                    "content": "Specification: "
                    + spec
                    + "(end of the specification) Requirement: "
                    + req
                    + "(end of requirement).",
                },
            ],
            max_tokens=10,
        )
        res = chat_response.choices[0].message.content
        log(
            "I had an interaction with "
            + llm_model
            + " to evaluate the correctness of a requirement."
        )
        log("I gave the following spec: " + spec)
        log("I also gave the following requirement: " + req)
        log("The LLM gave me the following answer: " + res)
        b = filter(res)
        return b
    except Exception as e:
        print(str(e))
        raise Exception("LLM failure: " + str(type(e))) from e
