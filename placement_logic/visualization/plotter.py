# visualization/plotter.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

def visualize_layout(layout, room_config, violations=None, heatmap_data=None, resolution=0.5):
    """
    增强版布局可视化工具
    :param layout: 家具布局列表
    :param room_config: 房间配置字典
    :param violations: 违规家具对列表 [(item1, item2), ...]
    :param heatmap_data: 热力图数据 {(x, y): count}
    :param resolution: 热力图网格分辨率（米）
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_title("Furniture Layout Visualization")
    ax.set_xlim(0, room_config["width"])
    ax.set_ylim(0, room_config["height"])
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.grid(True, linestyle='--', alpha=0.5)

    # 绘制热力图背景
    if heatmap_data:
        # 创建网格坐标
        x_bins = int(room_config["width"] / resolution) + 1
        y_bins = int(room_config["height"] / resolution) + 1
        x = np.linspace(0, room_config["width"], x_bins)
        y = np.linspace(0, room_config["height"], y_bins)
        X, Y = np.meshgrid(x, y)

        # 初始化热力图矩阵
        heatmap = np.zeros((y_bins, x_bins))
        for (xi, yi), count in heatmap_data.items():
            x_idx = int(xi / resolution)
            y_idx = int(yi / resolution)
            if 0 <= x_idx < x_bins and 0 <= y_idx < y_bins:
                heatmap[y_idx, x_idx] = count

        # 绘制热力图
        norm = Normalize(vmin=0, vmax=np.max(heatmap))
        cmap = plt.get_cmap("YlOrRd")
        im = ax.pcolormesh(X, Y, heatmap, cmap=cmap, norm=norm, alpha=0.3)
        plt.colorbar(im, ax=ax, label="Adjustment Frequency")

    # 家具颜色映射
    color_map = {
        "bed": "#9E77D0",
        "sofa": "#6DCE87",
        "table": "#C4A484",
        "chair": "#6C8EBF",
        "wardrobe": "#A9A9A9",
        "tv_stand": "#D4A798",
        "coffee_table": "#D6B85A",
        "bookshelf": "#7E7E7E",
        "desk": "#B8B8B8",
        "shoe_cabinet": "#5E5E5E"
    }

    # 绘制所有家具
    for item in layout:
        # 确定样式
        edge_color = "#FF3333" if self._is_violation_item(item, violations) else "#333333"
        line_width = 2 if self._is_violation_item(item, violations) else 1
        
        # 绘制家具
        rect = patches.Rectangle(
            (item.x, item.y), item.width, item.height,
            linewidth=line_width, edgecolor=edge_color,
            facecolor=color_map.get(item.type.value, "#DDDDDD"),
            alpha=0.9
        )
        ax.add_patch(rect)
        
        # 添加文字标签
        ax.text(item.x + item.width/2, item.y + item.height/2,
                f"{item.type.value}\n{item.width}x{item.height}",
                ha='center', va='center', 
                color='white', fontsize=8)

    # 绘制违规连接线
    if violations:
        for item1, item2 in violations:
            # 计算中心点
            x1 = item1.x + item1.width/2
            y1 = item1.y + item1.height/2
            x2 = item2.x + item2.width/2
            y2 = item2.y + item2.height/2
            
            # 绘制连接线
            ax.plot([x1, x2], [y1, y2], color='#FF3333', linewidth=1.5, linestyle=':')
            
            # 添加端点标记
            ax.plot(x1, y1, marker='o', markersize=8, 
                    markerfacecolor='none', markeredgecolor='#FF3333')
            ax.plot(x2, y2, marker='o', markersize=8,
                    markerfacecolor='none', markeredgecolor='#FF3333')

    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()

def _is_violation_item(self, item, violations):
    """检查家具是否涉及违规"""
    if not violations:
        return False
    for pair in violations:
        if item in pair:
            return True
    return False

def create_heatmap_data(optimization_history, room_config, resolution=0.5):
    """
    生成热力图数据
    :param optimization_history: 优化过程历史记录 [[布局1], [布局2], ...]
    :param room_config: 房间配置
    :param resolution: 网格分辨率（米）
    """
    heatmap = {}
    for layout in optimization_history:
        for item in layout:
            # 跟踪中心点移动
            center_x = item.x + item.width/2
            center_y = item.y + item.height/2
            grid_x = round(center_x / resolution) * resolution
            grid_y = round(center_y / resolution) * resolution
            heatmap[(grid_x, grid_y)] = heatmap.get((grid_x, grid_y), 0) + 1
    return heatmap

# 示例使用
if __name__ == "__main__":
    from core.furniture import Furniture
from core.room import Room
    from core.config_loader import sample_room
    
    # 创建测试布局
    test_layout = [
        Furniture(2, 3, 1.8, 2.0, "bed"),
        Furniture(5, 2, 1.5, 0.8, "desk"),
        Furniture(5.5, 3, 0.5, 0.5, "chair")
    ]
    
    # 模拟违规数据
    violations = [(test_layout[0], test_layout[2])]
    
    # 模拟热力图数据
    optimization_history = [test_layout] * 5  # 假设优化过程
    heatmap = create_heatmap_data(optimization_history, sample_room())
    
    # 可视化
    visualize_layout(test_layout, sample_room(), 
                    violations=violations, 
                    heatmap_data=heatmap)