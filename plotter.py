import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math

def plot_room(room, ax=None, show=True, save_path=None):
    """
    Plot the room and all furniture within it.
    
    Args:
        room: Room object containing dimensions and furniture
        ax: Optional matplotlib axis to plot on
        show: Whether to show the plot immediately
        save_path: Optional path to save the plot image
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))

    # Draw each piece of furniture
    for furniture in room.furniture:
        draw_furniture(furniture, ax)
    
    # Set plot properties
    ax.set_xlim(0, room.width)
    ax.set_ylim(0, room.height)
    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_title(f'Room Layout ({room.width}x{room.height})')
    ax.set_xlabel('Width (m)')
    ax.set_ylabel('Length (m)')
    
    # Add a legend showing furniture types
    furniture_types = sorted(set(str(f.type) for f in room.furniture))

    legend_elements = []
    for f_type in furniture_types:
        # Find a furniture of this type to get its color
        for f in room.furniture:
            if f.type == f_type:
                legend_elements.append(
                    patches.Patch(facecolor=f.color, edgecolor='black', label=f_type)
                )
                break
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, 1))
    
    if save_path:
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.tight_layout()
        plt.show()
    
    return ax

def draw_furniture(furniture, ax):
    """
    Draw a furniture item, including its bounding box if rotated.
    
    Args:
        furniture: Furniture object to draw
        ax: Matplotlib axis to draw on
    """
    # Calculate center for rotation
    center_x = furniture.x + furniture.width / 2
    center_y = furniture.y + furniture.height / 2

    # Create a rectangle for the furniture
    rect = patches.Rectangle(
        (furniture.x, furniture.y), furniture.width, furniture.height,  # ✅ Use 'height' instead
        angle=np.degrees(furniture.rotation),
        linewidth=1, edgecolor='black', facecolor='grey'
    )
    ax.add_patch(rect)
    
    # Add furniture label
    ax.text(center_x, center_y, furniture.type, 
            ha='center', va='center', fontsize=8, 
            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))
    
    # Draw bounding box for rotated furniture
    if furniture.rotation != 0:
        bb = get_bounding_box(furniture)
        rect = patches.Rectangle(
            (bb['x'], bb['y']), bb['width'], bb['length'],
            linewidth=1, edgecolor='red', linestyle='--', facecolor='none'
        )
        ax.add_patch(rect)
        
        # Draw corners for better visualization
        corners = get_corners(furniture)
        for corner in corners:
            ax.plot(corner[0], corner[1], 'ro', markersize=3)

def get_bounding_box(furniture):
    """
    Calculate the bounding box for the furniture, accounting for rotation.
    
    Args:
        furniture: Furniture object
        
    Returns:
        Dictionary with x, y, width, and length of the bounding box
    """
    if furniture.rotation == 0:
        return {
            'x': furniture.x,
            'y': furniture.y,
            'width': furniture.width,
            'length': furniture.length
        }
    else:
        # For rotated furniture, we need to calculate the corners
        corners = get_corners(furniture)
        min_x = min(corner[0] for corner in corners)
        max_x = max(corner[0] for corner in corners)
        min_y = min(corner[1] for corner in corners)
        max_y = max(corner[1] for corner in corners)
        
        return {
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x,
            'length': max_y - min_y
        }
        
def get_corners(furniture):
    """
    Get the four corners of the furniture after rotation.
    
    Args:
        furniture: Furniture object
        
    Returns:
        List of (x, y) tuples for each corner
    """
    # Center point of rotation
    cx = furniture.x + furniture.width / 2
    cy = furniture.y + furniture.length / 2
    
    # Half dimensions
    hw = furniture.width / 2
    hl = furniture.length / 2
    
    # Original corners relative to center
    corners_rel = [
        (-hw, -hl),  # bottom-left
        (hw, -hl),   # bottom-right
        (hw, hl),    # top-right
        (-hw, hl)    # top-left
    ]
    
    # Apply rotation to each corner
    cos_rot = math.cos(furniture.rotation)
    sin_rot = math.sin(furniture.rotation)
    
    # Rotated corners in absolute coordinates
    corners = []
    for rx, ry in corners_rel:
        # Rotate point
        new_rx = rx * cos_rot - ry * sin_rot
        new_ry = rx * sin_rot + ry * cos_rot
        
        # Translate back to absolute coordinates
        corners.append((cx + new_rx, cy + new_ry))
    
    return corners
