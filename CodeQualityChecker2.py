import gradio as gr
from langchain_openai import ChatOpenAI
import httpx
import os

# Disable SSL verification (temporary fix)
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

# Function to check a single code snippet
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


# Function to check all code files in a folder
def check_code_quality_from_folder(folder_path, checklist):
    checklist_items = [i.strip() for i in checklist.split("\n") if i.strip()]
    results = []

    for root, _, files in os.walk(folder_path):
        for filename in files:
            # Only check code files (adjust extensions as needed)
            if filename.endswith((".py", ".js", ".java", ".cpp", ".ts")):
                file_path = os.path.join(root, filename)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()

                for idx, item in enumerate(checklist_items, start=1):
                    # Show loading message for this file + item
                    yield f"## FILE: {filename}\n### CHECKLIST ITEM {idx}: {item}\nAnalyzing...\n\n---"

                    prompt = (
                        f"Evaluate the following code file '{filename}' against the checklist item: '{item}'.\n\n"
                        f"Code:\n{code}\n\nProvide observations and suggestions."
                    )
                    response = gpt4o.invoke(prompt)
                    feedback = response.content

                    results.append(
                        f"## FILE: {filename}\n### CHECKLIST ITEM {idx}: {item}\n{feedback}\n\n---"
                    )

                    # Stream accumulated results so far
                    yield "\n\n".join(results)

    # Finally return the full consolidated report
    return "\n\n".join(results)


# Gradio interface with two modes: paste code OR folder path
with gr.Blocks() as iface:
    gr.Markdown("# Code Quality Checker\nUpload code or point to a folder to get AI-powered feedback.")

    with gr.Tab("Paste Code"):
        code_input = gr.Textbox(lines=10, label="Paste your code here")
        checklist_input1 = gr.Textbox(lines=5, label="Enter checklist items (one per line)")
        output1 = gr.Markdown()
        btn1 = gr.Button("Analyze Code")
        btn1.click(fn=check_code_quality, inputs=[code_input, checklist_input1], outputs=output1)

    with gr.Tab("Folder Path"):
        folder_input = gr.Textbox(label="Enter folder path on your system")
        checklist_input2 = gr.Textbox(lines=5, label="Enter checklist items (one per line)")
        output2 = gr.Markdown()
        btn2 = gr.Button("Analyze Folder")
        btn2.click(fn=check_code_quality_from_folder, inputs=[folder_input, checklist_input2], outputs=output2)

iface.launch()