import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Tuple, Optional


def plot_quadrilaterals(
    all_coords: List[List[Tuple[float, float]]],
    colors: Optional[List[str]] = None,
    alpha: float = 0.5,
) -> None:
    """
    Plots multiple quadrilaterals given their coordinates.

    Args:
        all_coords (List[List[Tuple[float, float]]]):
            A list where each element is a list of four (x, y) tuples defining a quadrilateral.
        colors (Optional[List[str]]):
            A list of colors for the quadrilaterals. If None, a default color will be used.
        alpha (float):
            Transparency of the quadrilaterals.
    """
    # Create a figure and axis
    fig, ax = plt.subplots()

    # Iterate over the quadrilateral coordinates and plot each
    for i, coords in enumerate(all_coords):
        if len(coords) != 4:
            raise ValueError(
                f"Quadrilateral {i + 1} does not have exactly four points."
            )

        # Set color for the current quadrilateral
        color = colors[i] if colors and i < len(colors) else "blue"

        # Create a Polygon patch and add it to the plot
        polygon = patches.Polygon(coords, closed=True, color=color, alpha=alpha)
        ax.add_patch(polygon)

        # Plot the vertices
        x_coords, y_coords = zip(*coords)
        ax.plot(
            x_coords + (x_coords[0],), y_coords + (y_coords[0],), linewidth=0.1, color="black"
        )

    # Set limits for better visualization
    all_x = [x for quad in all_coords for x, _ in quad]
    all_y = [y for quad in all_coords for _, y in quad]
    x_min, x_max = min(all_x) - 1, max(all_x) + 1
    y_min, y_max = min(all_y) - 1, max(all_y) + 1
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Add grid and labels
    ax.grid(True)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("CLASS Readings Overlap")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")

    # Show the plot
    plt.show()


if __name__ == "__main__":
    # Example usage
    quadrilaterals: List[List[Tuple[float, float]]] = [
        [(1, 1), (4, 1), (3, 3), (1, 4)],  # Quadrilateral 1
        [(5, 5), (8, 5), (7, 8), (5, 7)],  # Quadrilateral 2
        [(2, 6), (5, 6), (4, 9), (2, 8)],  # Quadrilateral 3
    ]
    colors: List[str] = ["red", "green", "orange"]  # Colors for each quadrilateral

    plot_quadrilaterals(quadrilaterals, colors=colors, alpha=0.7)
