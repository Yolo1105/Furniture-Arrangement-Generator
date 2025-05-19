import imageio
import matplotlib.pyplot as plt

def save_gif_from_frames(frames, filename="output/ppo_run.gif", fps=2):
    if frames:
        imageio.mimsave(filename, frames, fps=fps)
        print(f"🎞️ GIF saved to: {filename}")
    else:
        print("⚠️ No frames to save as GIF.")

def debug_plot(layout, save_path=None):
    """
    可视化当前家具布局（仅支持2D简图）
    layout: List of furniture dicts with keys: x, y, w, h, type
    """
    fig, ax = plt.subplots()
    for item in layout:
        rect = plt.Rectangle(
            (item['x'], item['y']),
            item['width'],
            item['height'],
            linewidth=1,
            edgecolor='black',
            facecolor='lightblue',
            alpha=0.6
        )
        ax.add_patch(rect)
        ax.text(
            item['x'] + item['width'] / 2,
            item['y'] + item['height'] / 2,
            item['type'],
            ha='center',
            va='center',
            fontsize=8
        )

    ax.set_aspect('equal')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    plt.title("Furniture Layout")
    if save_path:
        plt.savefig(save_path)
        print(f"📸 Layout saved to {save_path}")
    else:
        plt.show()