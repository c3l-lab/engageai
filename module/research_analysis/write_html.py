import os
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np

def save_dataframe_and_plots_to_html(df_dict: dict = None, plot_dict: dict = None,
                                     term_code="", kind_analysis="", filename=""):

    # ✅ Default filename: e.g., 2405_gradegroup_submission_summary_analysis_visualization.html
    if not filename:
        base_name = f"{kind_analysis}_analysis_visualization".strip("_")
        filename = f"{term_code}_{base_name}.html".strip("_")

    # ✅ Folder name based only on kind_analysis (e.g., gradegroup_submission_summary_analysis_visualization)
    folder_name = f"{kind_analysis}_analysis_visualization".strip("_")
    output_dir = os.path.join(os.getcwd(), folder_name)
    os.makedirs(output_dir, exist_ok=True)  # Create folder only once if it doesn’t exist

    html_path = os.path.join(output_dir, filename)
    if os.path.exists(html_path):
        os.remove(html_path)

    html_content = "<html><head><title>Summary Output</title></head><body>"
    html_content += f"<h1>DataFrame Previews ({term_code}, {kind_analysis})</h1>"

    # ✅ Handle df_dict safely
    if df_dict:
        for name, obj in df_dict.items():
            try:
                html_content += f"<h2>{name}</h2>"
                if isinstance(obj, pd.DataFrame):
                    html_content += obj.head(10).to_html(index=False)
                elif isinstance(obj, pd.Series):
                    html_content += obj.head(10).to_frame().to_html()
                elif isinstance(obj, (np.ndarray, list)):
                    preview = pd.DataFrame(obj).head(10)
                    html_content += preview.to_html(index=False)
                elif isinstance(obj, dict):
                    preview = pd.DataFrame(list(obj.items()), columns=["Key", "Value"]).head(10)
                    html_content += preview.to_html(index=False)
                else:
                    html_content += f"<p><code>{repr(obj)}</code></p>"
            except Exception as e:
                html_content += f"<p>Error rendering data: {e}</p>"
    else:
        html_content += "<p>❗ No dataframes provided.</p>"

    # ✅ Handle plot_dict safely
    html_content += "<h1>Plots</h1>"
    if plot_dict:
        for name, fig in plot_dict.items():
            if hasattr(fig, "savefig"):
                try:
                    buf = BytesIO()
                    fig.savefig(buf, format='png', bbox_inches='tight')
                    plt.close(fig)
                    buf.seek(0)
                    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
                    html_content += f'<h2>{name}</h2><img src="data:image/png;base64,{image_base64}" width="800"><br>'
                except Exception as e:
                    html_content += f"<h2>{name}</h2><p>Error rendering plot: {e}</p><br>"
            else:
                html_content += f"<h2>{name}</h2><p>❌ Skipped: Not a matplotlib Figure object.</p><br>"
    else:
        html_content += "<p> No plots provided in this section.</p>"

    html_content += "</body></html>"

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML saved at: {html_path}")



# import os
# import pandas as pd
# import matplotlib.pyplot as plt
# import base64
# from io import BytesIO
# import numpy as np

# def save_dataframe_and_plots_to_html(df_dict: dict = None, plot_dict: dict = None,
#                                      term_code="", kind_analysis="", filename=""):
#     # Use default filename if not provided
#     if not filename:
#         filename = f"{term_code}_summary_output.html".strip("_")

#     folder_name = f"{term_code}_{kind_analysis}_analysis_visualization".strip("_")
#     output_dir = os.path.join(os.getcwd(), folder_name)
#     os.makedirs(output_dir, exist_ok=True)

#     html_path = os.path.join(output_dir, filename)
#     if os.path.exists(html_path):
#         os.remove(html_path)

#     html_content = "<html><head><title>Summary Output</title></head><body>"
#     html_content += f"<h1>DataFrame Previews ({term_code}, {kind_analysis})</h1>"

#     # ✅ Handle df_dict safely
#     if df_dict:
#         for name, obj in df_dict.items():
#             try:
#                 html_content += f"<h2>{name}</h2>"
#                 if isinstance(obj, pd.DataFrame):
#                     html_content += obj.head(10).to_html(index=False)
#                 elif isinstance(obj, pd.Series):
#                     html_content += obj.head(10).to_frame().to_html()
#                 elif isinstance(obj, (np.ndarray, list)):
#                     preview = pd.DataFrame(obj).head(10)
#                     html_content += preview.to_html(index=False)
#                 elif isinstance(obj, dict):
#                     preview = pd.DataFrame(list(obj.items()), columns=["Key", "Value"]).head(10)
#                     html_content += preview.to_html(index=False)
#                 else:  # scalar like int, float, str
#                     html_content += f"<p><code>{repr(obj)}</code></p>"
#             except Exception as e:
#                 html_content += f"<p>Error rendering data: {e}</p>"
#     else:
#         html_content += "<p>❗ No dataframes provided.</p>"

#     # ✅ Handle plot_dict safely
#     html_content += "<h1>Plots</h1>"
#     if plot_dict:
#         for name, fig in plot_dict.items():
#             if hasattr(fig, "savefig"):
#                 try:
#                     buf = BytesIO()
#                     fig.savefig(buf, format='png', bbox_inches='tight')
#                     plt.close(fig)
#                     buf.seek(0)
#                     image_base64 = base64.b64encode(buf.read()).decode('utf-8')
#                     html_content += f'<h2>{name}</h2><img src="data:image/png;base64,{image_base64}" width="800"><br>'
#                 except Exception as e:
#                     html_content += f"<h2>{name}</h2><p>Error rendering plot: {e}</p><br>"
#             else:
#                 html_content += f"<h2>{name}</h2><p>❌ Skipped: Not a matplotlib Figure object.</p><br>"
#     else:
#         html_content += "<p> No plots provided in this section.</p>"

#     html_content += "</body></html>"

#     with open(html_path, 'w', encoding='utf-8') as f:
#         f.write(html_content)

#     print(f"✅ Only HTML output saved to: {html_path}")


# # Helper to handle figures
# def extract_figures(obj):
#     if isinstance(obj, list) and all(isinstance(t, tuple) and len(t) == 2 for t in obj):
#         return {name: fig for name, fig in obj}
#     elif hasattr(obj, "savefig"):  # single matplotlib figure
#         return {"figure": obj}
#     else:
#         return {}  # or raise error/log warning
    

