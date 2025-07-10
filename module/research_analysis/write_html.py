import os
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np

def save_dataframe_and_plots_to_html(df_dict: dict, plot_dict: dict, term_code="", kind_analysis="", filename=""):
    if not filename:
        filename = f"{term_code}_summary_output.html".strip("_")

    folder_name = f"{term_code}_{kind_analysis}_analysis_visualization".strip("_")
    output_dir = os.path.join(os.getcwd(), folder_name)
    os.makedirs(output_dir, exist_ok=True)

    html_path = os.path.join(output_dir, filename)
    if os.path.exists(html_path):
        os.remove(html_path)

    html_content = "<html><head><title>Summary Output</title></head><body>"
    html_content += f"<h1>DataFrame Previews ({term_code}, {kind_analysis})</h1>"

    # Display up to 10 records or a summary if not a DataFrame
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
            else:  # scalar like int, float, str
                html_content += f"<p><code>{repr(obj)}</code></p>"
        except Exception as e:
            html_content += f"<p>Error rendering data: {e}</p>"

    # Render plots as base64 images
    html_content += "<h1>Plots</h1>"
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

    html_content += "</body></html>"

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Only HTML output saved to: {html_path}")


# Helper to handle figures
def extract_figures(obj):
    if isinstance(obj, list) and all(isinstance(t, tuple) and len(t) == 2 for t in obj):
        return {name: fig for name, fig in obj}
    elif hasattr(obj, "savefig"):  # single matplotlib figure
        return {"figure": obj}
    else:
        return {}  # or raise error/log warning
    

# import os
# import pandas as pd
# import matplotlib.pyplot as plt

# def save_dataframe_and_plots_to_html(df_dict: dict, plot_dict: dict, term_code="", kind_analysis="", filename=""):
#     # Use default filename if not provided
#     if not filename:
#         filename = f"{term_code}_summary_output.html".strip("_")

#     # Create the output directory with dynamic name
#     folder_name = f"{term_code}_{kind_analysis}_analysis_visualization".strip("_")
#     output_dir = os.path.join(os.getcwd(), folder_name)
#     os.makedirs(output_dir, exist_ok=True)

#     html_path = os.path.join(output_dir, filename)

#     html_content = "<html><head><title>Summary Output</title></head><body>"
#     html_content += f"<h1>DataFrame Previews ({term_code}, {kind_analysis})</h1>"

#     # Save top 10 rows of each DataFrame
#     for name, df in df_dict.items():
#         try:
#             df_head = df.head(10)
#             df_filename = f"{term_code}_{name}.csv".strip("_")
#             df_path = os.path.join(output_dir, df_filename)
#             df.to_csv(df_path, index=False)

#             html_table = df_head.to_html(index=False)
#             html_content += f"<h2>{name}</h2>{html_table}<br>"
#         except Exception as e:
#             html_content += f"<h2>{name}</h2><p>Error rendering DataFrame: {e}</p><br>"

#     # Save each plot (must be a matplotlib Figure)
#     html_content += "<h1>Plots</h1>"
#     for name, fig in plot_dict.items():
#         if hasattr(fig, "savefig"):
#             try:
#                 img_filename = f"{term_code}_{name}.png".strip("_")
#                 img_path = os.path.join(output_dir, img_filename)
#                 fig.savefig(img_path, bbox_inches="tight")
#                 plt.close(fig)
#                 html_content += f'<h2>{name}</h2><img src="{img_filename}" width="800"><br>'
#             except Exception as e:
#                 html_content += f"<h2>{name}</h2><p>Error saving plot: {e}</p><br>"
#         else:
#             html_content += f"<h2>{name}</h2><p>❌ Skipped: Not a matplotlib Figure object.</p><br>"

#     html_content += "</body></html>"

#     # Write the HTML file
#     with open(html_path, 'w', encoding='utf-8') as f:
#         f.write(html_content)

#     print(f"✅ All outputs saved to: {output_dir}")
