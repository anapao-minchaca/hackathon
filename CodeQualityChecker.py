import gradio as gr
from langchain_openai import ChatOpenAI

import httpx
client = httpx.Client(verify=False)

# Your credentials
GENAI_BASE_URL = "https://genailab.tcs.in"
GENAI_API_KEY = "sk-qXX8aIa3K4bjW8pkHU5SlQ"

# Initialize the model
gpt4o = ChatOpenAI(
    base_url=GENAI_BASE_URL,
    model="azure/genailab-maas-gpt-4o",
    api_key=GENAI_API_KEY,
    temperature=0.3,
    http_client=client
)

def check_code_quality(code, checklist):
    checklist_items = [i.strip() for i in checklist.split("\n") if i.strip()]
    results = []

    for idx, item in enumerate(checklist_items, start=1):
        # Show a loading message for this specific item
        yield f"## CHECKLIST ITEM {idx}: {item}\nAnalyzing...\n\n---"

        prompt = (
            f"Evaluate the following code against the checklist item: '{item}'.\n\n"
            f"Code:\n{code}\n\nProvide observations and suggestions."
        )
        response = gpt4o.invoke(prompt)
        feedback = response.content

        # Save the final feedback
        results.append(f"## CHECKLIST ITEM {idx}: {item}\n{feedback}\n\n---")

        # Stream the accumulated results so far
        yield "\n\n".join(results)

    # Finally return the full consolidated report
    return "\n\n".join(results)

iface = gr.Interface(
    fn=check_code_quality,
    inputs=[
        gr.Textbox(lines=10, label="Paste your code here"),
        gr.Textbox(lines=5, label="Enter checklist items (one per line)")
    ],
    outputs="markdown",
    title="Code Quality Checker",
    description="Upload code and checklist to get AI-powered feedback."
)

iface.launch()