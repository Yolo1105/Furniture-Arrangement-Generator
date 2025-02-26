# **Project Overview**
The **furniture_placement** project is designed to **automatically arrange furniture** in a given room while adhering to logical constraints and spatial optimization. The system integrates **rule-based logic** and **optimization algorithms** to ensure an **efficient, aesthetic, and human-compatible** layout. The final arrangement can be **visualized** for user inspection.

---

furniture_placement/
├── core/                   # 核心数据结构和基础类
│   ├── __init__.py
│   ├── furniture.py        # 定义家具类型及其基本属性
│   ├── room.py             # 房间结构，定义空间约束和布局方法
│   ├── config_loader.py    # 读取家具和房间配置的工具
│
├── generation/             # 生成层：初始布局生成
│   ├── __init__.py
│   ├── factory.py          # 家具生成器，负责创建不同类型的家具实例
│   ├── initial_placer.py   # 负责生成初始的家具布局（基础放置策略）
│   ├── collision/          # 碰撞检测模块
│   │   ├── buffer_check.py  # 确保家具间的缓冲空间
│   │   ├── relation_rules.py # 处理家具之间的逻辑关系
│   └── strategies/         # 具体的家具放置策略
│       ├── bed_strategy.py
│       ├── table_strategy.py
│       ├── sofa_strategy.py
│       ├── chair_strategy.py
│       ├── wardrobe_strategy.py
│
├── rules/                  # 规则引擎层：修正逻辑关系
│   ├── __init__.py
│   ├── rule_engine.py      # 规则执行引擎，调用各类规则
│   ├── alignment.py        # 对齐规则（如床靠墙、桌子居中等）
│   ├── clearance.py        # 确保家具之间的间距合理
│   ├── position_rules.py   # 位置调整规则
│   ├── relation_rules.py   # 处理家具之间的相互关系
│   ├── evaluation.py       # 规则执行的评分机制
│
├── optimization/           # 优化层：微调布局质量
│   ├── __init__.py
│   ├── genetic/            # 遗传算法优化
│   │   ├── parallel_ga.py  # 并行遗传算法
│   │   └── crossover.py    # 交叉操作逻辑
│   ├── local_search.py     # 局部搜索算法，用于优化最终布局
│
├── evaluation/             # 评估层：计算布局得分
│   ├── __init__.py
│   ├── scorer.py           # 评分计算，例如空间利用率、视觉对齐等
│   ├── pathfinder.py       # A*路径检查，确保可行走区域
│
├── visualization/          # 可视化层
│   ├── __init__.py
│   ├── plotter.py          # 可视化家具布局
│
├── configs/                # 配置文件
│   ├── room_config.json    # 房间尺寸、家具布置的预设配置
│   ├── furniture_rules.json # 规则定义，例如允许的家具摆放方式
│
├── main.py                 # 主入口，调用各个模块进行布局计算
├── README.md               # 说明文档
├── requirements.txt        # 依赖包列表
└── .github/workflows/      # CI/CD 自动化测试配置


## **Directory Structure & Module Breakdown**
The project follows a **layered architecture** for clarity, modularity, and maintainability.

### **1. Core Data Structures (Core Layer)**
📂 `core/`  
> Defines fundamental data structures such as **furniture objects, room representation**, and **configuration utilities**.

| File | Description |
|------|------------|
| `furniture.py` | Defines the `Furniture` class, including attributes like size, type, and orientation. |
| `room.py` | Implements the `Room` class, managing room size, walls, and furniture placement constraints. |
| `config_loader.py` | Loads JSON configuration files containing room and furniture specifications. |

---

### **2. Generation Layer (Furniture Generation)**
📂 `generation/`  
> This layer is responsible for **furniture creation and initial placement**, ensuring no overlaps and a reasonable initial distribution.

| File | Description |
|------|------------|
| `factory.py` | A furniture factory that dynamically creates instances based on configuration. |
| `initial_placer.py` | Generates the **first-pass furniture layout**, avoiding collisions and basic constraints. |

#### **Furniture-Specific Placement Strategies**
📂 `generation/strategies/`  
Each furniture type follows different initial placement rules:
- `bed_strategy.py`: Aligns beds with walls or places them centrally.
- `table_strategy.py`: Ensures tables are placed optimally for accessibility.
- `sofa_strategy.py`: Considers TV placement and room flow.
- `chair_strategy.py`: Ensures chairs are positioned near tables.
- `wardrobe_strategy.py`: Places wardrobes against walls without blocking walkways.

#### **Collision Detection**
📂 `generation/collision/`  
- `buffer_check.py`: Ensures proper spacing between furniture to avoid clutter.
- `relation_rules.py`: Enforces logical placement relationships (e.g., chairs near tables, beds avoiding doors).

---

### **3. Rule-Based Adjustment (Rule Engine)**
📂 `rules/`  
> This layer **refines the layout** by applying logical and aesthetic rules to correct misplacements.

| File | Description |
|------|------------|
| `rule_engine.py` | The central rule-processing engine that applies all corrections. |
| `alignment.py` | Enforces alignment rules (e.g., furniture against walls or centered). |
| `clearance.py` | Ensures proper spacing for movement paths and clearances. |
| `position_rules.py` | Governs furniture-to-wall positioning constraints. |
| `relation_rules.py` | Adjusts logical furniture relationships (e.g., TV should face sofas). |

---

### **4. Optimization Layer**
📂 `optimization/`  
> Uses **Genetic Algorithms (GA)** and **Local Search Optimization** to fine-tune the furniture arrangement for maximum efficiency.

| File | Description |
|------|------------|
| `genetic/parallel_ga.py` | Parallelized Genetic Algorithm to refine furniture layouts. |
| `genetic/crossover.py` | Implements crossover operations in the Genetic Algorithm. |
| `local_search.py` | Applies a local search heuristic to make small, efficient adjustments. |

---

### **5. Evaluation Layer**
📂 `evaluation/`  
> Calculates a **fitness score** for the layout, evaluating spatial efficiency, walkability, and furniture alignment.

| File | Description |
|------|------------|
| `scorer.py` | Computes scores based on spatial utilization, alignment, and aesthetic quality. |
| `pathfinder.py` | Uses **A* pathfinding** to ensure movement areas are accessible. |

---

### **6. Visualization Layer**
📂 `visualization/`  
> Renders the final layout to **visually confirm** the furniture placement.

| File | Description |
|------|------------|
| `plotter.py` | Draws the **room layout and furniture arrangement** for visualization. |

---

### **7. Configuration Layer**
📂 `configs/`  
> Stores **room and furniture configuration files**, allowing easy customization.

| File | Description |
|------|------------|
| `room_config.json` | Defines **room dimensions, shapes, and wall positions**. |
| `furniture_rules.json` | Specifies **furniture placement rules**, such as **minimum spacing, rotation constraints**, etc. |

---

### **8. Main Program Entry**
📂 `main.py`
> The **main execution script** orchestrates the entire pipeline:
1. **Loads configurations** (`config_loader.py`).
2. **Generates an initial layout** (`generation/`).
3. **Refines layout using rules** (`rules/`).
4. **Optimizes placement** (`optimization/`).
5. **Evaluates the layout** (`evaluation/`).
6. **Visualizes results** (`visualization/`).

---

## **`requirements.txt`**
Here’s the list of dependencies required for the project:

```txt
numpy
scipy
matplotlib
shapely
networkx
opencv-python
jsonschema
pillow
pyyaml
```

If **Genetic Algorithm (GA) optimization** is required, also include:
```txt
deap  # Evolutionary computation framework
```

If `scipy.optimize` is sufficient for local adjustments, `deap` can be omitted.

---

## **Project Summary**
The **furniture_placement** project follows a **layered architecture**, breaking down the furniture arrangement process into:
1. **Generation Layer**: Creates an initial furniture arrangement while avoiding overlaps.
2. **Rule-Based Adjustment Layer**: Corrects placements using logical rules (e.g., chairs should be near tables).
3. **Optimization Layer**: Enhances layout quality through Genetic Algorithms and local search.
4. **Evaluation Layer**: Assesses the arrangement’s effectiveness.
5. **Visualization Layer**: Provides a graphical representation of the layout.

This **modular design** ensures **scalability, flexibility, and clarity**, making it applicable for **smart home planning, interior design, and automated space optimization**.