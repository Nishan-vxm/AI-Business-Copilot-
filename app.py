import gradio as gr
import pandas as pd

from src.copilot import business_copilot_query

CUSTOM_CSS = """
.gradio-container {
    max-width: 1450px !important;
    margin: auto !important;
    font-family: Inter, ui-sans-serif, system-ui, sans-serif !important;
}
#app-header {
    border-radius: 18px;
    padding: 25px 28px;
    background: linear-gradient(120deg, #101b33, #1d3f78);
    color: white;
    margin-bottom: 18px;
}
#app-header h1 { color: white !important; margin-bottom: 8px; }
#app-header p { color: #cfdbf3 !important; }
#sidebar, #main-panel {
    border: 1px solid #dfe6f1;
    border-radius: 16px;
    padding: 18px;
}
#run-button {
    background: #2863d7 !important;
    color: white !important;
    border: none !important;
}
#run-button:hover { background: #194eaf !important; }
"""

def run_copilot_ui(question):
    if not question or not question.strip():
        return "Please enter a question.", "", pd.DataFrame()

    try:
        response = business_copilot_query(question.strip())
        sql = response.get("sql") or ""
        result = response.get("result")
        error = response.get("error")

        if error:
            return f"Query failed: {error}", sql, pd.DataFrame()
        if result is None:
            return "No results returned.", sql, pd.DataFrame()

        return f"Success · {len(result)} row(s) returned", sql, result
    except Exception as exc:
        return f"Unexpected error: {exc}", "", pd.DataFrame()


with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate",
        neutral_hue="slate"
    ),
    css=CUSTOM_CSS,
    title="AI Business Copilot"
) as demo:
    gr.HTML("""
    <div id="app-header">
      <div style="font-size:12px;letter-spacing:2px;font-weight:700">
        AI BUSINESS INTELLIGENCE
      </div>
      <h1>AI Business Copilot</h1>
      <p>Turn natural-language questions into useful business insights.</p>
    </div>
    """)

    with gr.Row(equal_height=False):
        with gr.Column(scale=1, min_width=220):
            with gr.Group(elem_id="sidebar"):
                gr.Markdown("## Workspace")
                gr.Markdown(
                    "🔵 **AI Analyst**\n\n"
                    "🗄️ Data Explorer\n\n"
                    "📋 SQL Inspector\n\n"
                    "---\n\n"
                    "### Connected source\n"
                    "**Olist Ecommerce**\n\n"
                    "`SQLite · Read-only`\n\n"
                    "### Model\n"
                    "`Qwen2.5-3B-Instruct`"
                )

        with gr.Column(scale=4, min_width=320):
            with gr.Group(elem_id="main-panel"):
                gr.Markdown("## Ask your data")
                gr.Markdown(
                    "Ask a question in plain English. Review the SQL and results."
                )
                question = gr.Textbox(
                    label="Business question",
                    placeholder="e.g. How many orders were delivered?",
                    lines=2
                )
                gr.Examples(
                    examples=[
                        ["How many orders are there in the database?"],
                        ["How many orders were delivered?"],
                        ["What is the average payment value?"],
                        ["Show the 5 states with the most customers."]
                    ],
                    inputs=question
                )
                run_button = gr.Button(
                    "✦ Generate insight",
                    variant="primary",
                    elem_id="run-button"
                )

            status = gr.Textbox(
                label="Execution status",
                interactive=False
            )
            with gr.Group(elem_id="main-panel"):
                gr.Markdown("## SQL Inspector")
                sql_output = gr.Code(label="Generated SQL", language="sql")
            with gr.Group(elem_id="main-panel"):
                gr.Markdown("## Query results")
                result_output = gr.Dataframe(
                    label="Returned data",
                    interactive=False
                )

            run_button.click(
                fn=run_copilot_ui,
                inputs=question,
                outputs=[status, sql_output, result_output]
            )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
