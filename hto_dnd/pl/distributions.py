import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

def _set_ylim(ax, xmin=1):
    if xmin is None:
        return ax
    cutoff = 0
    lines = ax.get_lines()
    for i in range(len(lines)):
        x_data, y_data = lines[i].get_data()
        y_sub = y_data[x_data > xmin]
        if len(y_sub) == 0:
            continue
        cutoff = max(cutoff, max(y_sub))
    ax.set_ylim(0, cutoff * 1.1)
    return ax

def _symmetric_log1p(x):
    return np.sign(x) * np.log1p(np.abs(x))

def _format(x):
    if np.expm1(x) < 1000:
        return f"{np.expm1(x):.0f}"
    elif np.expm1(x) < 1000000:
        return f"{np.expm1(x) / 1000:.0f}K"
    else:
        return f"{np.expm1(x) / 1000000:.0f}M"

def plot_distributions_log(
    adata, ax=None,
    layer=None,
    cmap="tab20",
    title="",
    xmin=None,
    remove_legend=False,
    params_legend={},
    **kwargs
):
    # defaults
    defaults_legend = {
        "title": "Hashtags",
        "bbox_to_anchor": (1.05, 1),
        "loc": "upper left",
    }
    params_legend = {**defaults_legend, **params_legend}

    # prep data
    df_long = adata.to_df(layer).melt()
    df_long.loc[:, "value_log"] = _symmetric_log1p(df_long.value)
    df_long.head()

    # plot
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(8, 3))

    # kde log
    ax = sns.kdeplot(
        df_long,
        hue="variable",
        x="value_log",
        palette=cmap,
        ax=ax,
        **kwargs
    )
    ax = _set_ylim(ax, xmin=xmin)
    ax.set_title(title)
    ax.yaxis.set_ticks([])
    ax.set_ylabel("")
    ax.set_xlabel("Logged Antibody Count")

    # ticks in raw counts
    log_ticks = _symmetric_log1p([-100000, -1000, -10, -1, 0, 1, 10, 100, 1000, 10000, 100000])  # Replace with dynamic range if needed
    ax.xaxis.set_major_locator(ticker.FixedLocator(log_ticks))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: _format(x)))

    if remove_legend:
        ax.get_legend().remove()
    else:
        handles = ax.get_legend().legend_handles
        labels = [t._text for t in ax.get_legend().texts]
        ax.legend(handles, labels, **params_legend)

    return ax
