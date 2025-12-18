__all__ = [
    'color_palettes',
    'color_cyclers',
    'color_iters',
    'set_color_cycler',
    'set_mpl_latex_style',
    'PiecewiseLinearNorm',
    'remove_repeated_legend',
    'filter',
    'bar_plot_compare',
    'plot_dictionary_2d',
    'plot_complex_3d_bar',
    'plot_complex_hinton',
]


import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D 
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Rectangle
from matplotlib.axes import Axes
from matplotlib import rcParams
from cycler import cycler
from itertools import cycle
import matplotlib.cm as cm

from typing import Dict, List, Tuple

from chencrafts.toolbox.data_processing import nd_interpolation

# color cyclers
color_palettes = dict(
    PGL = [
        "#0c2e6d", "#b63566", "#91adc2", "#e9c2c3", "#AEB358"],
    green_to_red = [
        "#001219", "#005f73", "#0a9396", "#94d2bd", "#e9d8a6", 
        "#ee9b00", "#ca6702", "#bb3e03", "#9b2226"],
    sunset = [
        "#F8B195", "#F67280", "#C06C84", "#6C5B7B", "#355C7D"],
    hotel_70s = [
        "#448a9a", "#fb9ab6", "#e1cdd1", "#e1b10f", "#705b4c"],
    blue_to_red = [
        "#e63946", "#a8dadc", "#457b9d", "#a7bb40", "#3d1645"],
    colorblind_1 = [    # from https://arxiv.org/abs/2107.02270
        "#3f90da", "#ffa90e", "#bd1f01", "#832db6", "#94a4a2", 
        "#a96b59", "#e76300", "#b9ac70", "#717581", "#92dadd",],
    C2QA = [
        '#007A86', '#F9B211', '#A12731', '#78C0E0', '#4A0E4E'
    ],
)
color_cyclers = dict([
    (key, cycler(color = color_palettes[key])) for key in color_palettes
])
color_iters = dict([
    (key, cycle(color_palettes[key])) for key in color_palettes
])
def set_color_cycler(
    cycler_name: str | List[str]
):
    """
    Available cycler names: 
    PGL, green_to_red, sunset, hotel_70s, blue_to_red, colorblind_1, C2QA
    """
    if isinstance(cycler_name, str):
        mpl.rcParams["axes.prop_cycle"] = color_cyclers[cycler_name]
        plt.rcParams["axes.prop_cycle"] = color_cyclers[cycler_name]
    elif isinstance(cycler_name, list):
        mpl.rcParams["axes.prop_cycle"] = cycler(color = cycler_name)
        plt.rcParams["axes.prop_cycle"] = cycler(color = cycler_name)
        
def set_mpl_latex_style():
    """
    Sets Matplotlib rcParams to use LaTeX rendering for consistent fonts
    in both math expressions and normal text, matching LaTeX's default
    (Computer Modern).
    
    Note: This requires a LaTeX installation on your system.
    """
    mpl.rcParams.update({
        'text.usetex': True,
        # Optional: Specify font family, but with usetex=True, LaTeX handles it
        'font.family': 'serif',
        'font.serif': ['Computer Modern'],
        # You can add more if needed, e.g., for sans-serif or monospace
        'font.sans-serif': ['Computer Modern Sans Serif'],
        'font.monospace': ['Computer Modern Typewriter'],
    })
    # Optionally, add LaTeX packages to preamble if needed, e.g.:
    mpl.rcParams['text.latex.preamble'] = r"""
\usepackage{amsmath}
\usepackage{amssymb}
"""
    
def remove_repeated_legend(ax=None):
    """remove repeated legend"""
    if ax is None:
        ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())

def filter(c, filter_name):
    if filter_name in ["translucent", "trans"]:
        r, g, b, a = c
        return [r, g, b, a * 0.2]
    elif filter_name in ["emphsize", "emph"]:
        r, g, b, a = c
        factor = 3
        return [r ** factor, g ** factor, b ** factor, a]

# class Cmap():
#     def __init__(
#         self, 
#         upper: float, 
#         lower: float = 0, 
#         cmap_name="rainbow"
#     ):
#         self.upper = upper
#         self.lower = lower
#         self.cmap_name = cmap_name

#         self.cmap = colormaps[self.cmap_name]
#         self.norm = plt.Normalize(self.lower, self.upper)
#         self.mappable = plt.cm.ScalarMappable(norm=self.norm, cmap=self.cmap)
    
#     def __call__(self, val):
#         # return self.mappable.cmap(val)
#         return self.cmap(self.norm(val))
# useless now, can be simply replaced by plt.cm.get_cmap(cmap_name)


class PiecewiseLinearNorm:
    def __init__(
        self, 
        value_list: List[float] | np.ndarray,
        color_list: List[float] | np.ndarray,
        clip: bool = False, 
    ):
        assert len(value_list) == len(color_list), "value_list and color_list must have the same length."
        
        # Sorting the lists based on the value_list
        sorted_indices = np.argsort(value_list)
        self.value_list = np.array(value_list)[sorted_indices]
        self.color_list = np.array(color_list)[sorted_indices]
        self.clip = clip

    def __call__(self, value: float) -> float:
        if self.clip:
            if value < self.value_list[0]:
                return self.color_list[0]
            elif value > self.value_list[-1]:
                return self.color_list[-1]
        
        return np.interp(value, self.value_list, self.color_list)

    def inverse(self, color: float) -> float:
        return np.interp(color, self.color_list, self.value_list)


def bar_plot_compare(
    var_list_dict: Dict[str, np.ndarray],
    x_ticks: List = None,
    ax = None,
    figsize = None, 
    dpi = None,
    x_tick_rotation = 45, 
):
    """
    The var_list_dict should be {labels: a series of value to compare}. 

    Note: such function can be realized in pandas by DataFrame.plot(kind="bar")
    """
    # plot 
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)

    x_len = len(x_ticks)
    for key, val in var_list_dict.items():
        assert len(x_ticks) == len(val), (f"x_lables should have the same length with"
        f"the data to be plotted, exception occurs for {key}")

    compare_num = len(var_list_dict)
    plot_width = 1 / (compare_num + 1)
    plot_x = np.linspace(0, x_len-1, x_len) + 0.5 * plot_width
    
    for i, (key, val) in enumerate(var_list_dict.items()):
            
        ax.bar(
            x = plot_x + i * plot_width, 
            height = val,
            width = plot_width,
            align = "edge",
            label = key
        )
            
        ax.set_xticks(plot_x + plot_width * compare_num / 2)
        ax.set_xticklabels(
            x_ticks, 
            rotation=x_tick_rotation, 
            rotation_mode="anchor", 
            horizontalalignment="right", 
            verticalalignment="top", 
            fontsize=rcParams["axes.labelsize"]
        )

        ax.legend()

def plot_dictionary_2d(
    dict: Dict[str, np.ndarray], 
    xy_mesh: List[np.ndarray],
    xy_label: List[str] = ["", ""], 
    single_figsize = (3, 2.5), 
    cols = 3, 
    place_a_point: Tuple[float, float] = tuple(),     # plot a point in the figure
    show_value = False,                   # plot the number number near the destination of the trajectory  
    slc = slice(None),                            # slice the value stored in the dictionary before any processing
    slc_2d = slice(None),  # for zooming in the plots
    contour_levels = 0,
    cmap = "viridis",
    vmin = None,
    vmax = None,
    dpi = 150,
    save_filename = None,
):
    """
    Plot a grid of 2D color meshes from a dictionary of data arrays.

    This function creates a multi-panel figure where each panel corresponds to a key-value pair
    in the input dictionary. Each value is plotted as a 2D color mesh using the provided X and Y
    meshes. Optional features include adding contours, marking a specific point, displaying
    interpolated values at that point, and saving the figure.

    Parameters
    ----------
    dict : Dict[str, np.ndarray]
        Dictionary where keys are strings (used as subplot titles) and values are 2D numpy arrays
        to be plotted.
    xy_mesh : List[np.ndarray]
        List of two 2D numpy arrays representing the X and Y meshes for the plots.
    xy_label : List[str], optional
        Labels for the x and y axes, by default ["", ""].
    single_figsize : tuple, optional
        Size of each individual subplot, by default (3, 2.5).
    cols : int, optional
        Number of columns in the subplot grid, by default 3.
    place_a_point : Tuple[float, float], optional
        Coordinates (x, y) of a point to mark on each plot (white scatter point), by default ().
        If provided, the point is added to every subplot.
    show_value : bool, optional
        If True and `place_a_point` is provided, interpolate and display the value at that point
        on the plot, by default False.
    slc : slice, optional
        Slice to apply to the data arrays and meshes before processing, by default slice(None).
    slc_2d : slice, optional
        Additional 2D slice for zooming into the meshes and data, by default slice(None).
    contour_levels : int, optional
        Number of contour levels to add to each plot (using `contour`), by default 0 (no contours).
        Contours are skipped if the data has zero standard deviation.
    cmap : str, optional
        Colormap for the pcolormesh, by default "viridis".
    vmin : float, optional
        Minimum value for the colormap scaling, by default None (auto-scaled).
    vmax : float, optional
        Maximum value for the colormap scaling, by default None (auto-scaled).
    dpi : int, optional
        Dots per inch for the figure, by default 150.
    save_filename : str, optional
        If provided, save the figure to this file path, by default None (no save).

    Notes
    -----
    - The number of rows in the subplot grid is automatically calculated based on the number of
      dictionary items and the `cols` parameter.
    - If contouring fails (e.g., no contours found), an IndexError is caught and printed.
    - Plotting errors (e.g., ValueError or IndexError due to shape mismatches) are caught and
      printed with details.
    - Interpolation for `show_value` uses `scipy.interpolate.interpn` (assumed via `nd_interpolation`).
    - Ensure the shapes of meshes and data arrays are compatible after slicing.

    """

    rows = np.ceil(len(dict) / cols).astype(int)
    fig, axs = plt.subplots(rows, cols, figsize=(cols*single_figsize[0], rows*single_figsize[1]), dpi=dpi)

    X_mesh, Y_mesh = xy_mesh
    X_mesh, Y_mesh = X_mesh[slc][slc_2d], Y_mesh[slc][slc_2d]
    x_name, y_name = xy_label

    ax_row, ax_col = 0, 0
    for key, full_value in dict.items():
        if rows == 1:
            ax: Axes = axs[ax_col]
        else:
            ax: Axes = axs[ax_row, ax_col]
        value = full_value[slc][slc_2d]

        # base value
        try:
            cax = ax.pcolormesh(X_mesh, Y_mesh, value, vmin=vmin, vmax=vmax, cmap=cmap)
        except (ValueError, IndexError):
            print("Error, Value to be plotted has the shape", value.shape, ", key: ", key)
        # except TypeError:
        #     print("TypeError, key: ", key, "value: ", value, "X, Y mesh", X_mesh, Y_mesh)
        fig.colorbar(cax, ax=ax)

        # contour
        if contour_levels > 0 and np.std(value) > 1e-14:
            try:
                CS = ax.contour(X_mesh, Y_mesh, value, cmap="hsv", levels=contour_levels)
                ax.clabel(CS, inline=True, fontsize=7)
                # fig.colorbar(cax_cont, ax=ax)
            except IndexError as err: # usually when no contour is found\
                print(f"In {key}, except IndexError: {err}")
                pass

        # trajectory
        if place_a_point != ():
            px, py = place_a_point
            ax.scatter(px, py, c="white", s=8)
            if show_value:
                interp = nd_interpolation(
                    [X_mesh, Y_mesh],
                    value
                )
                val = interp(px, py)
                if np.abs(val) >= 1e-2 and np.abs(val) < 1e2: 
                    text = f"  {val:.3f}"
                else:
                    text = f"  {val:.1e}"
                ax.text(px, py, text, ha="left", va="center", c="white", fontsize=7)

        # labels 
        ax.set_title(key)
        ax.set_xlabel(x_name)
        ax.set_ylabel(y_name)
        ax.grid()

        ax_col += 1
        if ax_col % cols == 0:
            ax_col = 0
            ax_row += 1

    plt.tight_layout()

    if save_filename is not None:
        plt.savefig(save_filename)

    plt.show()

def plot_complex_3d_bar(
    complex_data: np.ndarray, 
    max_val: float | None = None, 
    min_val: float | None = None,
    ax: Axes3D | None = None, 
    cmap: str = 'hsv', 
    labels_x: List[str] | None = None, 
    labels_y: List[str] | None = None, 
    alpha: float = 0.8, 
    bar_width: float = 0.7, 
    show_colorbar: bool = True,
    show_gridlines: bool = True, 
    bar_edge_color: str ='black', 
    bar_edge_width: float = 0.5,
):
    """
    Create a 3D bar plot for visualizing a complex 2D array with improved handling.
    
    Parameters:
    -----------
    complex_data : 2D ndarray of complex numbers
        The complex data to visualize
    max_val : float, optional
        The maximum absolute value for scaling. If None, uses the maximum magnitude in the data
    ax : matplotlib.axes.Axes, optional
        The 3D axes on which to draw the plot. If None, creates a new figure with 3D axes
    cmap : str or matplotlib.colors.Colormap, optional
        Colormap to use for phase representation
    labels_x : list or None
        Labels for the x-axis
    labels_y : list or None
        Labels for the y-axis
    title : str or None
        Title for the plot
    alpha : float
        Transparency of the bars
    bar_width : float
        Width of the bars (0 to 1)
    show_colorbar : bool
        Whether to show a colorbar for phase
    show_gridlines : bool
        Whether to show gridlines on the plot
    bar_edge_color : str or None
        Color for bar edges (None for no edges)
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure containing the 3D bar plot
    ax : matplotlib.axes.Axes
        The 3D axes containing the bar plot
    """
    
    # Get magnitude and phase
    magnitude = np.abs(complex_data)  # Ensure we use absolute value
    phase = np.angle(complex_data)
    
    # Set up the figure and axes
    if ax is None:
        fig = plt.figure(figsize=(10, 8))
        ax: Axes3D = fig.add_subplot(111, projection='3d') # type: ignore
    else:
        fig = ax.figure
    
    # Determine maximum value for scaling
    if max_val is None:
        max_val = magnitude.max()
    
    # Create meshgrid for x and y coordinates
    nrows, ncols = complex_data.shape
    _x_pos = np.arange(ncols)
    _y_pos = np.arange(nrows)
    _xx_pos, _yy_pos = np.meshgrid(_x_pos, _y_pos)
    x_pos = _xx_pos.flatten()
    y_pos = _yy_pos.flatten()
    z_pos = np.zeros_like(x_pos)
    
    # Flatten magnitude and phase for plotting
    magnitudes = magnitude.flatten()
    phases = phase.flatten()
    plot_magnitudes = magnitudes.copy()
    if min_val is not None:
        mask = plot_magnitudes >= min_val
        # Filter all arrays based on mask
        x_pos = x_pos[mask]
        y_pos = y_pos[mask]
        z_pos = z_pos[mask]
        plot_magnitudes = plot_magnitudes[mask]
        phases = phases[mask]
        
        if len(x_pos) == 0:
            return fig, ax
        
    if max_val is not None:
        plot_magnitudes[plot_magnitudes > max_val] = max_val
    
    # Create colormap for phase
    norm = Normalize(vmin=-np.pi, vmax=np.pi)
    cmap_obj = mpl.colormaps[cmap]
    colors = cmap_obj(norm(phases))
    
    # Bar dimensions
    dx = dy = bar_width * np.ones_like(z_pos)
    
    # # Sort indices by x, y position to plot from back to front
    # # This helps with occlusion problems
    # indices = list(range(len(x_pos)))
    # indices.sort(key=lambda i: (-x_pos[i], y_pos[i]))  # Sort by distance from viewing point
    
            
    # Create bar with edgecolor parameter for clear outlines
    bar = ax.bar3d(
        x_pos-dx/2, y_pos-dy/2, z_pos,
        dx, dy, plot_magnitudes, 
        color=colors, alpha=alpha, shade=True,
        edgecolor=bar_edge_color, linewidth=bar_edge_width,
        zsort="max"
    )
     
    # Add overflow indicators
    for idx in np.ndindex(x_pos.shape):
        x, y, z = x_pos[idx], y_pos[idx], z_pos[idx]
        real_mag, plot_mag, phi = magnitudes[idx], plot_magnitudes[idx], phases[idx]
        if real_mag > max_val:
            # Create vertices for the top face
            verts = [
                (x-dx[idx]/2, y-dy[idx]/2, max_val),
                (x+dx[idx]/2, y-dy[idx]/2, max_val),
                (x+dx[idx]/2, y+dy[idx]/2, max_val),
                (x-dx[idx]/2, y+dy[idx]/2, max_val)
            ]

            # Create a polygon collection for the top face
            poly = Poly3DCollection(
                [verts], alpha=0.0, linewidth=bar_edge_width, 
            )
            poly.set_facecolor('white')  # Base color
            poly.set_hatch('//////')       # Diagonal hatching
            ax.add_collection3d(poly)
            
            # Add text marker for exact value
            ax.text(x, y, max_val*1.1, f"{real_mag:.3f}", 
                    ha='center', va='bottom', color=bar_edge_color, 
                    # fontweight='bold', 
                    fontsize=9)
    
    # Set axis labels
    if labels_x is not None:
        ax.set_xticks(np.arange(ncols))
        ax.set_xticklabels(labels_x)
    else:
        ax.set_xticks(np.arange(ncols))
    
    if labels_y is not None:
        ax.set_yticks(np.arange(nrows))
        ax.set_yticklabels(labels_y)
    else:
        ax.set_yticks(np.arange(nrows))
    
    # Set axis limits with extra space for overflow indicators
    ax.set_xlim(-0.5, ncols-0.5)
    ax.set_ylim(-0.5, nrows-0.5)
    ax.set_zlim(0, max_val * 1.1)  # Extra headroom for overflow indicators
    
    # Reverse y-axis to match matrix orientation
    ax.set_ylim(nrows-0.5, -0.5)
    
    # Set view angle to show bars more clearly
    ax.view_init(elev=30, azim=225)
    
    # Show or hide gridlines
    if not show_gridlines:
        ax.grid(False)
    
    # Add colorbar for phase
    if show_colorbar:
        sm = plt.cm.ScalarMappable(cmap=cmap_obj, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, pad=0.1, aspect=30)
        cbar.set_ticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
        cbar.set_ticklabels([r'$-\pi$', r'$-\pi/2$', r'$0$', r'$\pi/2$', r'$\pi$'])
    
    return fig, ax

def plot_complex_hinton(
    complex_data: np.ndarray, 
    max_val: float | None = None, 
    ax: Axes | None = None, 
    cmap: str = 'hsv', 
    labels_x: List[str] | None = None, 
    labels_y: List[str] | None = None, 
    grid_color: str = 'gray', 
    title: str | None = None, 
    fontsize_factor: float = 0.7, show_colorbar: bool = True):
    """
    Create a Hinton diagram for visualizing a complex 2D array.
    
    Parameters:
    -----------
    complex_data : 2D ndarray of complex numbers
        The complex data to visualize
    max_val : float, optional
        The maximum absolute value for scaling. If None, uses the maximum magnitude in the data
    ax : matplotlib.axes.Axes, optional
        The axes on which to draw the diagram. If None, creates a new figure
    cmap : str or matplotlib.colors.Colormap, optional
        Colormap to use for phase representation
    labels_x : list or None
        Labels for the x-axis
    labels_y : list or None
        Labels for the y-axis
    grid_color : str
        Color for the grid outlines
    title : str or None
        Title for the plot
    fontsize_factor : float
        Factor to adjust font size of text annotations
    show_colorbar : bool
        Whether to show a colorbar for phase
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        The figure containing the Hinton diagram
    ax : matplotlib.axes.Axes
        The axes containing the Hinton diagram
    """    
    # Get magnitude and phase
    magnitude = np.abs(complex_data)
    phase = np.angle(complex_data)
    
    # Set up the figure and axes
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    else:
        fig = ax.figure
    
    # Determine maximum value for scaling
    if max_val is None:
        max_val = magnitude.max()
    
    # Get dimensions
    nrows, ncols = complex_data.shape
    
    # Draw grid outlines first
    ax.set_xlim(-0.5, ncols - 0.5)
    ax.set_ylim(-0.5, nrows - 0.5)
    
    # Plot grid lines
    for i in range(nrows + 1):
        ax.axhline(i - 0.5, color=grid_color, linestyle='-', linewidth=0.5)
    for j in range(ncols + 1):
        ax.axvline(j - 0.5, color=grid_color, linestyle='-', linewidth=0.5)
    
    # Create colormap for phase
    norm = Normalize(vmin=-np.pi, vmax=np.pi)
    cmap_obj = cm.get_cmap(cmap)
    
    # Draw squares
    for i in range(nrows):
        for j in range(ncols):
            # Get magnitude and phase for this element
            mag = magnitude[i, j]
            phi = phase[i, j]
            
            # Skip drawing if magnitude is negligible
            if mag < 1e-3 * max_val:
                continue
            elif mag > max_val:
                plot_mag = max_val
            else:
                plot_mag = mag
            
            # Size of square is proportional to magnitude (normalized to max_val)
            size = 0.85 * (plot_mag / max_val)**(1/2)
            
            # Color based on phase
            color = cmap_obj(norm(phi))
            
            # Center of the grid cell
            center_x, center_y = j, nrows - 1 - i  # Flip y-axis to match matrix orientation
            
            # Add rectangle centered in the grid cell
            rect = Rectangle(
                (center_x - size/2, center_y - size/2),
                size, size,
                facecolor=color,
                edgecolor='black',
                linewidth=0.5
            )
            ax.add_patch(rect)
            
            # Add magnitude text for significant values
            if plot_mag > 0.01 * max_val:
                fontsize = fontsize_factor * size * 10
                text_color = 'white' if sum(color[:3])/3 < 0.5 else 'black'
                ax.text(center_x, center_y, f'{mag:.3f}',
                        ha='center', va='center', color=text_color,
                        fontsize=fontsize)
    
    # Set labels
    if labels_x is not None:
        ax.set_xticks(range(ncols))
        ax.set_xticklabels(labels_x)
    else:
        ax.set_xticks([])
        
    if labels_y is not None:
        ax.set_yticks(range(nrows))
        ax.set_yticklabels(labels_y[::-1])  # Reverse to match the display order
    else:
        ax.set_yticks([])
    
    # Add colorbar for phase
    if show_colorbar:
        sm = plt.cm.ScalarMappable(cmap=cmap_obj, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, label='Phase')
        cbar.set_ticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
        cbar.set_ticklabels([r'$-\pi$', r'$-\pi/2$', r'$0$', r'$\pi/2$', r'$\pi$'])
    
    # Add title
    if title:
        ax.set_title(title)
    
    ax.set_aspect('equal')
    plt.tight_layout()
    
    return fig, ax