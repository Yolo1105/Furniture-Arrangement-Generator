from core.config_loader import ConfigLoader
from generation.wfc_generator import WFCGenerator
from visualization.layout_plot import plot_layout

def main():
    room = ConfigLoader.get_room_config()
    layout = WFCGenerator(room).generate()
    plot_layout(layout, room["width"], room["height"],
                save_path="output/debug_layout.png",
                title="Debug Layout")

if __name__ == "__main__":
    main()
