import gradio as gr
from rag_pipeline import answer


def _query(question: str):
    if not question.strip():
        return "", ""
    result = answer(question.strip())
    sources_text = "\n".join(result["sources"])
    return result["answer"], sources_text


with gr.Blocks(title="CS Internship & Career Guide") as demo:
    gr.Markdown("## CS Internship & Career Guide\nAsk anything about internship hunting, LeetCode prep, resumes, offers, and more.")

    question = gr.Textbox(label="Your question", placeholder="e.g. How do I get my first internship with no experience?", lines=2)
    submit = gr.Button("Ask", variant="primary")
    answer_out = gr.Textbox(label="Answer", lines=10, interactive=False)
    sources_out = gr.Textbox(label="Sources", lines=3, interactive=False)

    submit.click(fn=_query, inputs=question, outputs=[answer_out, sources_out])
    question.submit(fn=_query, inputs=question, outputs=[answer_out, sources_out])


if __name__ == "__main__":
    demo.launch()
