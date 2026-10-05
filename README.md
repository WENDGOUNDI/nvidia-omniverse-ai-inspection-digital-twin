# NVIDIA Omniverse AI Inspection Digital Twin

A manufacturing digital twin built with **NVIDIA Omniverse Kit, OpenUSD, and Python**.

The project simulates a conveyor-based quality inspection line where a product moves through a virtual production process, stops at an inspection station, receives an OK/NG result, changes color based on the result, and updates production statistics in real time.

The current inspection result is simulated randomly. A future version will replace this logic with a real AI computer vision model.

---

## Demo
#### Inspection with NG as result
<img width="1915" height="977" alt="Image" src="https://github.com/user-attachments/assets/e9b7cd30-c459-4f3e-8490-c87e6c9989b1" />

#### Inspection with OK as result
<img width="1917" height="1046" alt="Image" src="https://github.com/user-attachments/assets/96581eaa-2aca-445b-9e09-a5156458ebc6" />

#### Video demo
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/e72e8226-19f6-4c27-8cb1-96487483d4e8" />

---

## Features

- Custom NVIDIA Omniverse Kit application
- Custom Python Kit extension
- OpenUSD-based factory scene
- Procedural conveyor creation
- Conveyor rollers and side rails
- Moving product simulation
- Interactive `omni.ui` control panel
- Automatic inspection-zone detection
- Simulated OK / NG inspection
- Product color change based on inspection result
- Real-time production statistics
- Yield calculation
- Product reset
- Statistics reset

---

## Simulation Workflow

```text
Product Created
      ↓
Moves on Conveyor
      ↓
Inspection Station
      ↓
Stops for Inspection
      ↓
Random OK / NG Result
      ↓
OK → Green
NG → Red
      ↓
Statistics Updated
      ↓
Product Continues
```

---

## Current Inspection Logic

The current version uses a simulated inspection result:

```python
result = random.choice(["OK", "NG"])
```

Product states:

```text
Orange = Waiting for Inspection
Green  = OK
Red    = NG
```

The goal is to later replace the random decision with a real computer vision model.

---

## Production Statistics

The application tracks:

```text
Total Inspected
OK Count
NG Count
Yield %
```

Yield is calculated as:

```text
Yield = OK / Total Inspected × 100
```

---

## Technology Stack

- NVIDIA Omniverse Kit
- OpenUSD
- Python
- `omni.ext`
- `omni.ui`
- `omni.usd`
- `omni.kit.app`
- `pxr.UsdGeom`
- `pxr.Gf`

---

## Project Structure

```text
nvidia-omniverse-ai-inspection-digital-twin/
│
├── README.md
├── LICENSE
├── .gitignore
│
├── assets/
│   ├── demo.gif
│   └── demo.png
│
└── source/
    ├── apps/
    │   └── my_company.abdoul_digital_twin.kit
    │
    └── extensions/
        └── my_company.digital_twin.core/
            ├── config/
            │   └── extension.toml
            │
            └── my_company/
                └── digital_twin/
                    └── core/
                        ├── __init__.py
                        └── extension.py
```

---

## How It Works

### 1. Create the Factory

The factory scene is generated programmatically using OpenUSD.

It includes:

- Conveyor base
- Rollers
- Side rails
- Product
- Inspection station
- Simulated inspection camera

Example:

```python
UsdGeom.Xform.Define(
    stage,
    "/World/Factory"
)
```

---

### 2. Move the Product

The product moves along the X axis using the Omniverse update loop.

```python
self._product_x += self._speed * dt
```

The USD position is updated with:

```python
self._product_translate_op.Set(
    Gf.Vec3d(
        self._product_x,
        70.0,
        0.0
    )
)
```

---

### 3. Inspect the Product

When the product reaches the inspection station:

```python
if self._product_x >= self._inspection_x:
```

the product temporarily stops.

A random OK or NG result is generated.

The product then changes color and continues moving.

---

## Controls

The Omniverse UI includes:

```text
Create Factory
Start Conveyor
Stop Conveyor
Reset Product
Reset Statistics
```

It also displays:

```text
Simulation Status
Product Position
Inspection Result
Total Inspected
OK
NG
Yield
```

---

## Running the Project

This project is based on the NVIDIA Omniverse Kit App Template.

Clone the Kit App Template:

```bash
git clone https://github.com/NVIDIA-Omniverse/kit-app-template.git
```

Enter the directory:

```bash
cd kit-app-template
```

Copy the application and extension from this repository into the corresponding `source` folders.

Build the project:

```bash
./repo.sh build
```

Launch the application:

```bash
./repo.sh launch my_company.abdoul_digital_twin.kit
```

For Windows:

```powershell
.\repo.bat build
```

```powershell
.\repo.bat launch my_company.abdoul_digital_twin.kit
```

---

## Roadmap

### Completed

- [x] Custom Omniverse Kit application
- [x] Custom Python extension
- [x] OpenUSD factory scene
- [x] Conveyor simulation
- [x] Product movement
- [x] Inspection station
- [x] Simulated OK / NG inspection
- [x] Product color visualization
- [x] Production statistics
- [x] Yield calculation
- [x] Interactive UI

### Potential Next Steps

- [ ] Integrate a real AI defect detection model
- [ ] Add defect class and confidence score
- [ ] Add multiple products
- [ ] Add product IDs and traceability
- [ ] Add NG rejection mechanism
- [ ] Add inspection image display
- [ ] Store inspection results in a database
- [ ] Add sensor data
- [ ] Connect physical factory data to the digital twin
- [ ] Add predictive maintenance
- [ ] Add MES integration

---

## Future AI Integration

The current logic:

```python
result = random.choice(["OK", "NG"])
```

can later be replaced by a real AI pipeline:

```text
Camera Image
      ↓
Computer Vision Model
      ↓
Defect Detection
      ↓
Defect Class + Confidence
      ↓
OK / NG Decision
      ↓
Omniverse Digital Twin
```

Example future result:

```text
Part ID: A00124
Defect: Solder Bridge
Confidence: 97.6%
Decision: NG
```

Possible models include:

- YOLO
- CNN
- Vision Transformer
- Anomaly Detection
- Custom Manufacturing Defect Detection Models

---

## What I Learned

This project helped me learn:

- NVIDIA Omniverse Kit development
- Custom Kit extensions
- OpenUSD stages and prims
- USD transforms
- Procedural 3D scene creation
- `omni.ui`
- Omniverse update loops
- Event-driven simulation
- Manufacturing digital twin concepts
- AI inspection workflow integration

---

## Future Vision

The long-term goal is to evolve this project from a simulated inspection system into a real AI-powered manufacturing digital twin.

```text
Physical Factory
      │
      ├── Cameras
      ├── Sensors
      ├── PLC
      └── Machines
             │
             ▼
        AI / Data Layer
             │
             ▼
     NVIDIA Omniverse
        Digital Twin
             │
       ┌─────┴─────┐
       │           │
Visualization   Analytics
       │           │
       └─────┬─────┘
             ▼
       Factory Decisions
```

---

## Author

**Savadogo Abdoul**

Interests:

- Industrial AI
- Smart Manufacturing
- Computer Vision
- Digital Twin
- NVIDIA Omniverse
- OpenUSD
- Physical AI
- AI Agents
- Factory Automation

---

## License

This project is intended for learning, experimentation, and portfolio demonstration.

You can add an MIT License if you want to make the repository open source.
```
