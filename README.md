# Blackcutter ⚔️ (WIP)

A high-performance 2D action game engine built in Python utilizing **Entity-Component-System (ECS)** architecture, procedural inverse kinematics (IK) animation, and a custom spatial data editor.

---

## 🌟 Highlights & Architecture

* **Entity-Component-System (ECS):** Built on top of `esper`, enabling clean decoupling of state data from processing logic.
* **Procedural Inverse Kinematics (2-Bone IK):** Dynamic stickmanoid skeleton animations that automatically adjust to velocity, terrain, and stride vectors without relying on frame-by-frame sprite sheets.
* **Spatial Data Level Editor:** Integrated standalone Pygame level editor (`map_builder.py`) with support for real-time zooming, panning, rotated collision boundaries, trigger zones, and entity placements with JSON exports.
* **Resource & Scene Management:** Dynamic scene loading, automatic background scaling, texture caching, and modular system processors.

---

## 📁 Repository Structure

```text
├── main.py                     # Primary game entry point & game loop
├── map_builder.py              # Visual Spatial Data Map Editor tool
├── components/
│   ├── dataclasses.py          # Pure ECS Components (Position, Velocity, Stickmanoid, etc.)
│   ├── engineproc.py           # ECS Processors (Rendering, Physics, IK, Input)
│   ├── scenesys.py             # Level data parser and scene manager
│   ├── res_mngr.py             # Asset lifecycle manager (Images, Fonts, Sounds)
│   ├── eventsys.py             # Decoupled Observer event system
│   └── utils.py                # Mathematical helpers & 2-bone IK solver
└── assets/
    ├── levels/                 # Map textures and JSON scene layouts
    ├── images/                 # Texture assets
    └── sounds/                 # Audio assets
```

---

## 🚀 Getting Started

### Prerequisites

* **Python 3.9+**
* Dependencies:
  * `pygame`
  * `esper`
  * `PyOpenGL` (optional / system rendering extensions)

Install dependencies via `pip`:

```bash
pip install pygame esper PyOpenGL
```

---

## 🎮 Running the Game

Execute `main.py` from the root directory:

```bash
python main.py
```

### Controls
* **Q / D:** Move Left / Right
* **Z / S:** Move Up / Down

---

## 🗺️ Spatial Data Map Editor

To design levels, export collision boundaries, or place entities visually:

```bash
python map_builder.py
```

### Editor Controls

| Input | Action |
| :--- | :--- |
| **`1` / `2` / `3`** | Switch Mode (Collider / Area / Entity) |
| **Left Click + Drag** | Draw bounding boxes or place entity targets |
| **Middle Click / Right Click + Drag** | Pan viewport |
| **Scroll Wheel** | Zoom In / Out |
| **Shift + Scroll Wheel** | Rotate active collider/area bounding box |
| **Ctrl + Scroll Wheel** | Adjust rotation snapping increment |
| **Ctrl + S** | Export map layout to `arena_map.json` |
| **Ctrl + Z** | Undo last placed item |

---

## ⚙️ Core Technical Details

### 2-Bone IK Solver (`utils.py` & `engineproc.py`)

The procedural stickmanoid physics processor uses the **Law of Cosines** to compute knee and joint placements in real time based on player movement vectors and step strides:

$$\cos(\theta) = \frac{l_1^2 + d^2 - l_2^2}{2 \cdot l_1 \cdot d}$$

```python
# Procedural 2-Bone IK Execution
knee_pos = utils.solve_2bone_ik(
    root_x, root_y, 
    foot_target_x, foot_target_y, 
    thigh_length, shin_length, 
    bend_dir=1
)
```

---

## 🛠️ Roadmap

- [x] Core ECS Architecture (`esper`)
- [x] Procedural 2-Bone IK Limb Rendering
- [x] Basic AABB Physics & Collision Detection
- [x] Level/Spatial Map Editor with JSON Exporter
- [ ] Combat Mechanics & Hurtboxes
- [ ] OpenGL Shader Pipeline Integration
- [ ] AI Behavior Trees for Enemies

---

## 📜 License

This project is licensed under the MIT License. Developed by **GuestTox**.
