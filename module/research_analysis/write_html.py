import os
import pandas as pd
import matplotlib.pyplot as plt

def save_dataframe_and_plots_to_html(output_dir, df_dict: dict, plot_dict: dict, filename="summary_output.html"):
    os.makedirs(output_dir, exist_ok=True)
    html_path = os.path.join(output_dir, filename)

    html_content = "<html><head><title>Summary Output</title></head><body>"
    html_content += "<h1>DataFrame Previews</h1>"

    # Save top 10 rows of each DataFrame
    for name, df in df_dict.items():
        try:
            df_head = df.head(10).to_html(index=False)
            html_content += f"<h2>{name}</h2>{df_head}<br>"
        except Exception as e:
            html_content += f"<h2>{name}</h2><p>Error rendering DataFrame: {e}</p><br>"

    # Save each plot (must be a matplotlib Figure)
    html_content += "<h1>Plots</h1>"
    for name, fig in plot_dict.items():
        if hasattr(fig, "savefig"):
            try:
                img_path = os.path.join(output_dir, f"{name}.png")
                fig.savefig(img_path, bbox_inches="tight")
                plt.close(fig)
                html_content += f'<h2>{name}</h2><img src="{name}.png" width="800"><br>'
            except Exception as e:
                html_content += f"<h2>{name}</h2><p>Error saving plot: {e}</p><br>"
        else:
            html_content += f"<h2>{name}</h2><p>❌ Skipped: Not a matplotlib Figure object.</p><br>"

    html_content += "</body></html>"

    # Write the HTML file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Output saved to: {html_path}")
