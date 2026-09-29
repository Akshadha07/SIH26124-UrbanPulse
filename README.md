# AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet

**Smart India Hackathon 2026 Prototype**  
**Problem Statement:** SIH26124 | **Theme:** Smart Automation | **Category:** Software  
**Problem Statement Owner:** Bharat Electronics Limited (BEL)  
**Default Prototype City:** Vadodara, Gujarat  
**Core Pipeline:** $\text{OBSERVE} \longrightarrow \text{DETECT} \longrightarrow \text{CONFIRM} \longrightarrow \text{PRIORITIZE} \longrightarrow \text{ACT} \longrightarrow \text{VERIFY}$

---

## 1. Problem

Municipalities and Urban Local Bodies (ULBs) face critical challenges in maintaining road safety, monitoring air quality, responding to monsoon urban flooding, and managing transit congestion:
- **High Infrastructure Costs**: Deploying thousands of stationary CCTV cameras, dedicated air quality stations (CAAQMS), and fixed IoT telemetry nodes across a city requires massive capital expenditure.
- **Coverage Blind Spots**: Fixed sensors only observe discrete intersections; over 85% of urban arterial and secondary road networks remain unmonitored.
- **Lag-Prone & Reactive Maintenance**: Cities rely heavily on manual citizen grievances filed days or weeks after potholes, waterlogging, or road degradation occur.
- **Network Bandwidth Overload**: Continuous 24/7 high-definition video streaming from hundreds of fixed cameras places prohibitive demands on municipal networks, cloud bandwidth, and storage.

---

## 2. Solution

Instead of wiring the city with costly stationary sensors, this platform transforms the **existing public transport bus fleet into a distributed mobile sensing network**.

Public buses already traverse every key arterial corridor, ward, and junction in Vadodara every single day at **zero incremental travel cost**. By equipping buses with a low-cost, ruggedized sensing and edge AI kit, the vehicle autonomously:
1. **Observes** road surfaces, vibration signals, air quality, water accumulation, and interior passenger crowding.
2. **Detects** defects and hazards locally on-device using lightweight vision models and signal-processing anomaly detectors (YOLO-nano, IMU peak filter, water reflection analysis).
3. **Uploads** only compact, structured event observations over 4G/5G M2M cellular links (strictly no continuous raw video transmission).
4. **Fuses** multi-modal and multi-bus detections on the backend to eliminate false positives, score dynamic repair priorities, and trigger rapid emergency escalations.
5. **Enables Action** through digital municipal work order dispatch and disaster management alerts.
6. **Autonomously Verifies** repairs when subsequent buses naturally drive over the site during routine scheduled transit.

---

## 3. Cost Comparison

> **Important Disclosure**:  
> All figures presented below are **illustrative planning estimates, not an official procurement quotation** or verified government procurement prices. They are derived from standard smart-city industry benchmarks for a Tier-2 Indian city (Vadodara: ~300 sq. km, ~1,200 km road network) to demonstrate the economic logic of reusing an existing bus fleet as mobile sensing infrastructure.

### Detailed Assumptions Table

| Parameter | Traditional Fixed Infrastructure | Mobile Bus Fleet Sensing (Our Solution) |
| :--- | :--- | :--- |
| **Monitored Fleet / Node Count** | 800 fixed CCTV poles & 35 CAAQMS stations | 100 municipal buses covering 1,200 km transit routes |
| **Unit Hardware & Sensor Cost** | CCTV + Pole + Enclosure: ₹75,000 – ₹1,25,000/site<br/>CAAQMS Station: ₹1.00 Cr – ₹1.50 Cr/station | Ruggedized Edge Kit (Camera, IMU, Solid-State AQI, NavIC/GPS, Compute): ₹30,000 – ₹50,000/bus |
| **Civil Works, Trenching & Power** | Dedicated utility power drops, fiber trenching, right-of-way permissions: ₹5.00 Cr – ₹10.00 Cr | ₹0.00 (Zero civil works; draws power from existing bus 12V/24V electrical harness) |
| **Installation & Retrofit** | Civil foundation, mast erection, alignment: ₹1.50 Cr – ₹2.50 Cr | Bus depot retrofit & calibration: ₹5,000 – ₹10,000/bus (₹0.05 Cr – ₹0.10 Cr total) |
| **Bandwidth & Connectivity (3 Years)** | Dedicated high-bandwidth leased lines for continuous video streaming: ₹4.50 Cr – ₹9.00 Cr | Compact M2M 4G/5G data SIMs (< 2 KB/event structured telemetry): ₹0.20 Cr – ₹0.30 Cr |
| **Maintenance Contracts (3 Years)** | Cleaning stationary optics, pole repairs, calibration visits: ₹6.00 Cr – ₹10.00 Cr | Centralized depot-level sensor inspection during routine bus service: ₹0.15 Cr – ₹0.25 Cr |
| **Citywide Road Coverage** | Static: < 15% of road length (fixed intersection viewcones) | Dynamic: > 90% of arterial & feeder roads traversed repeatedly daily |
| **Illustrative 3-Year TCO** | **₹58.00 Cr – ₹93.00+ Crores (Midpoint: ~₹70 Cr)** | **₹0.70 Cr – ₹1.15 Crores (Midpoint: ~₹0.9 Cr)** |

### Economic Rationale: Near-Zero Marginal Deployment Cost
The buses already consume fuel, follow fixed routes, and are staffed by transit operators. The incremental expenditure is strictly limited to the modular sensing kit, achieving **~98% cost reduction** compared to installing a dedicated physical citywide fixed sensor network.

---

## 4. Hardware & Deployment Alignment (BEL)

### Indigenous Hardware Architecture
The edge sensor kit is **designed to accommodate indigenously manufactured electronics and components**, positioning **Bharat Electronics Limited (BEL)** as a natural potential hardware manufacturing and integration partner for large-scale municipal deployment:
- **Modular Edge Kit**: Designed around an industrial, automotive-grade compute module (ARM/NPU SBC), forward optical camera, high-precision MEMS 3-axis accelerometer/gyroscope, solid-state gas/particulate sensors, and 4G/5G M2M cellular uplink.
- **NavIC (IRNSS) Integration**: Designed to accommodate India's indigenous NavIC satellite positioning receiver for sovereign, highly accurate geo-tagging without exclusive reliance on foreign GNSS constellations.
- **Ruggedized Enclosure**: Specifiable to IP67 ingress protection and vibration-damped automotive standards suitable for Indian road conditions.

*(Note: BEL is the Problem Statement owner for SIH26124; this platform is architecturally aligned to enable indigenous manufacturing and integration, without claiming an existing contractual procurement commitment).*

### Deployment Options & Data Sovereignty
The platform architecture is **not cloud-first by necessity**. To ensure complete data sovereignty and keep sensitive municipal infrastructure data within government control, the system supports:
1. **Government-Hosted Infrastructure**: State Data Centres (e.g., Gujarat State Data Centre - GSDC) or National Informatics Centre (NIC Cloud / MeghRaj).
2. **On-Premise Deployment**: Municipal Corporation Integrated Command and Control Centres (ICCC).
3. **Indigenous / Private Cloud**: Sovereign private cloud environments complying with MeitY guidelines.
4. **Public Cloud**: Optional deployment model for rapid scaling or multi-region prototyping.

---

## 5. Core Features

- **Multi-Modal AI Sensor Fusion**: Cross-correlates optical camera defect detections with IMU z-axis vibration shockwaves ($> 1.8g$) to eliminate false positives caused by shadows, paint markings, and lighting glare.
- **Multi-Bus Consensus Engine**: Merges detections from multiple independent buses passing the same geographic coordinate within ~35m into a single canonical incident.
- **Dynamic Priority Index**: Ranks incidents automatically based on:
  $$\text{Priority} = (\text{Severity} \times 0.40) + (\text{Frequency} \times 0.25) + (\text{Corridor Tier} \times 0.20) + (\text{Multi-Modal Confirmed} \times 0.15)$$
- **Road Health Score**: Derived intelligence metric for road segments evaluating historical hazard frequency, IMU roughness index (IRI equivalent), and repeat-failure rates for preventive municipal maintenance.
- **Autonomous Resolution Verification Loop**: Tracks post-repair bus runs. If subsequent buses traverse the repaired location without registering vibration shocks or visual defects, the work order auto-transitions to `VERIFIED_CLOSED`.
- **Live Vadodara Transit & Occupancy Tracking**: Visualizes bus positions with real-time heading and AI-estimated passenger crowding levels (Low, Medium, High, Overcrowded).
- **Spatial AQI Heatmap**: Interpolates mobile PM2.5 readings across Vadodara to identify environmental pollution corridors.
- **Multilingual Citizen Mobile App**: Fully localized in **English, Hindi (हिंदी), and Gujarati (ગુજરાતી)**.
- **Citizen Contribution Feedback Loop**: The system avoids storing raw device identifiers and uses an internal one-way hashed identifier (`device_id_hash`) for lightweight anonymous report continuity, displaying "Issues you reported that got fixed" without gamification or leaderboards.

---

## 6. Waterlogging Early Warning

During monsoon downpours, the platform leverages the existing on-bus sensor kit (camera surface reflections + IMU wheel drag/rolling resistance) to evaluate real-time water accumulation at **zero extra hardware cost**.

### Severity Scale & Escalation Path
- **Observation Scale**: `NORMAL` (0.0), `MINOR` (1.0), `MODERATE` (2.0), `SEVERE` (3.0–3.9), `CRITICAL` ($\ge 4.0$).
- **Emergency Escalation**: When severity reaches `CRITICAL` ($\ge 4.0$ or water depth $> 15\text{ cm}$):
  $$\text{Bus Sensors} \longrightarrow \text{Edge Observation} \longrightarrow \text{WATERLOGGING\_CRITICAL} \longrightarrow \text{Emergency Alert} \longrightarrow \mathbf{DISASTER\_MGMT\_OFFICER}$$
- **Emergency Fast-Path Workflow**: Bypasses the normal road-repair work order queue and directly triggers high-priority alerts to the **Disaster Management Officer**.

### Alert Delivery: Prototype vs. Production
- **Prototype Architecture**:
  - Disaster Management Dashboard receives instant real-time alerts via WebSocket (`/ws/live`).
  - Citizen Mobile App receives high-urgency in-app route warnings via live poll/stream from `/api/v1/incidents`.
- **Production Roadmap**:
  - Government-approved mobile push infrastructure (e.g. FCM / APNs / National Disaster Management Authority emergency broadcast) will deliver background push notifications to commuter devices.

---

## 7. Open Data API

In alignment with National Data Sharing and Accessibility Policy (NDSAP) and open-government principles, the platform provides a public, read-only, rate-limited API namespace (`/api/v1/public/`):
- `GET /api/v1/public/hazards/summary`: Aggregated hazard counts by ward and road corridor.
- `GET /api/v1/public/aqi/summary`: 24-hour spatial air quality averages and citywide pollution trends.
- `GET /api/v1/public/road-health/summary`: Anonymized road health scores and surface roughness ratings across transit routes.

### Strict Privacy Guarantee
- Exposes **strictly anonymized aggregate data**.
- Contains **zero Personally Identifiable Information (PII)**: no citizen names, phone numbers, email addresses, device identifiers, or raw complaint texts.
- Citizen report identities and internal `device_id_hash` values are **never exposed** through the public API.
- Designed for urban researchers, civic-tech developers, universities, and regional planning authorities.

---

## 8. Scalability Roadmap

The platform features a modular, multi-tenant architecture designed for seamless phased expansion:

```text
Phase A: Vadodara Pilot (20–30 Buses)
  └── High-density corridors (Sayajigunj, Alkapuri, Makarpura, Waghodia Road)
  └── Ground-truth sensor validation & integration with Vadodara Smart City ICCC

Phase B: State-Wide Municipal Fleets (1,000+ Buses)
  └── Expansion across Ahmedabad (AMTS/BRTS), Surat (Sitilink), and Rajkot (RMTS)
  └── Unified State Urban Development Department dashboard hosted on Gujarat SDC

Phase C: Pan-India Municipal Intelligence Platform
  └── Deployable across any Indian municipality operating a public transport fleet
  └── Standardized, mass-produced BEL-compatible edge hardware kits
```

---

## 9. Architecture

### Explicit End-to-End AI Pipeline
The platform separates raw sensor measurements from AI observations and fused incidents:

$$\text{RAW SENSOR INPUT} \longrightarrow \text{AI / SIGNAL DETECTION} \longrightarrow \text{STRUCTURED OBSERVATIONS} \longrightarrow \text{SPATIO-TEMPORAL CLUSTERING} \longrightarrow \text{MULTI-MODAL FUSION} \longrightarrow \text{MULTI-BUS CONFIRMATION} \longrightarrow \text{FUSED INCIDENT} \longrightarrow \text{PRIORITY / ESCALATION} \longrightarrow \text{ACTION} \longrightarrow \text{VERIFICATION}$$

### Modular AI Subsystem Architecture (`backend/app/ai/`)
```text
backend/app/ai/
├── detection/         # Computer vision road hazard detection (YOLO-nano on camera frames)
├── anomaly/           # IMU vibration shock detection & AQI environmental anomaly detection
├── waterlogging/      # Water surface reflection & rolling resistance severity estimation
├── fusion/            # Spatio-temporal clustering (35m radius), multi-modal & multi-bus confirmation
├── priority/          # Multi-factor dynamic priority scoring
└── prediction/        # Road health score calculation & degradation intelligence
```

### Three-Layer Deployment Topology
1. **Layer 1: Mobile Edge Sensing (On-Bus Fleet)**
   - Bus sensors (forward camera, 3-axis IMU, solid-state AQI, NavIC/GPS, door counter).
   - Generates raw sensor evidence (`is_simulated = true` for prototype).
   - 4G/5G structured JSON uplink.
2. **Layer 2: Shared Backend & Urban Intelligence Engine**
   - FastAPI REST API & WebSocket broadcast hub.
   - AI Detection, Anomaly, and Fusion subsystems.
   - Waterlogging fast-path & autonomous verification engine.
   - SQLite for zero-config local run; PostgreSQL 16 + PostGIS 3.4 for production.
3. **Layer 3: Application Interfaces**
   - **Municipal Command Center (Web)**: React + Vite + Tailwind CSS + Leaflet GIS.
   - **Citizen Mobile App**: Flutter (Multilingual: EN, HI, GU).
   - **Open Data Consumers**: Public REST endpoints for researchers and civic agencies.

---

## 10. Database

The database enforces a clean normalized pipeline:

$$\mathbf{RawSensorEvent} \longrightarrow \mathbf{AIObservation} \longrightarrow \mathbf{IncidentObservationLink} \longrightarrow \mathbf{FusedIncident} \longrightarrow \mathbf{WorkOrder} \longrightarrow \mathbf{VerificationAudit}$$

### Key Entity Model
- `Bus`: Fleet vehicle registry with hardware kit versions and depot assignments.
- `BusLiveState`: Real-time coordinates, speed, heading, and crowd occupancy.
- `RawSensorEvent`: Discrete sensor evidence emitted by on-bus sensors (`bus_id`, `raw_camera_ref`, `accel_x`, `accel_y`, `accel_z`, `gyro_z`, `raw_water_level`, `pm2_5`, `lat`, `lon`, `timestamp`, `is_simulated`).
- `AIObservation`: Structured detection emitted by AI models (`observation_type`, `hazard_class`, `confidence`, `bounding_box`, `signal_features`, `severity_score`, `model_name`, `model_version`, `evidence_ref`, `lat`, `lon`, `timestamp`, `is_simulated`).
- `FusedIncident`: Canonical city issue synthesized by fusion engine (`incident_type`, `lat`, `lon`, `address_hint`, `severity`, `waterlogging_severity`, `confidence`, `is_confirmed`, `status`, `priority_score`).
- `IncidentObservationLink`: Association mapping connecting multiple `AIObservation` records to a single `FusedIncident`.
- `RoadSegment`: Street network segments with geometry, corridor name, and traffic tier.
- `RoadHealthScore`: Derived road intelligence metric (health score 0–100, roughness index, defect density).
- `WorkOrder`: Municipal repair dispatch with contractor tracking and SLA milestones.
- `VerificationAudit`: Automatic post-repair pass-by validation results.
- `User`: Roles include `ADMIN`, `MUNICIPAL_OFFICER`, `DISASTER_MGMT_OFFICER`, `CONTRACTOR`, `CITIZEN`.
- `CitizenReportIdentity`: Internal hashed identity (`device_id_hash`, `verified_report_count`) for report continuity without raw identifier retention.
- `CitizenReport`: Crowdsourced issues correlated with sensor incidents.

---

## 11. API

All core endpoints are versioned under `/api/v1/`:

### Ingestion & Simulation
- `POST /api/v1/ingest/event`: Ingest single raw edge sensor event (`is_simulated = true/false`, `simulation_run_id`).
- `POST /api/v1/ingest/batch`: Ingest batched raw sensor stream from bus upload.
- `POST /api/v1/ingest/telemetry`: Update bus GPS position, speed, heading, passenger count (emitted every ~5s by default via `SIMULATION_INTERVAL_SECONDS = 5.0`).
- `POST /api/v1/simulate/scenario/{name}`: Trigger preset simulation scenarios (e.g. `monsoon_flood`, `pothole_cluster`).
- `POST /api/v1/simulate/reset`: Resets fleet state, clears/archives simulated records for the active `simulation_run_id` without deleting real non-simulated data, and generates a fresh `simulation_run_id`.

### Incidents & Disaster Alerts
- `GET /api/v1/incidents`: List incidents with filters (`incident_type`, `status`, `priority`, `severity_min`).
- `GET /api/v1/incidents?incident_type=WATERLOGGING_CRITICAL&priority=EMERGENCY`: Canonical filter for emergency flood alerts.
- `GET /api/v1/incidents/waterlogging-alerts`: Convenience / read-optimized endpoint for the Disaster Management view.
- `GET /api/v1/incidents/{incident_id}`: Incident details and metrics.
- `GET /api/v1/incidents/{incident_id}/evidence`: Underlying AI observations and raw sensor evidence linked to incident.
- `PATCH /api/v1/incidents/{incident_id}/status`: Transition incident status.

### Fleet & Environment
- `GET /api/v1/fleet/live`: Real-time locations, bearings, speeds, and crowd status for all buses.
- `GET /api/v1/fleet/{bus_id}`: Single bus telemetry and recent detections.
- `GET /api/v1/fleet/routes`: Pre-configured Vadodara transit routes.
- `GET /api/v1/aqi/live`: Recent mobile AQI points across Vadodara.
- `GET /api/v1/aqi/grid`: Spatial grid cells (interpolated PM2.5/AQI values for heatmap rendering).

### Citizen & Public Open Data
- `POST /api/v1/citizen/report`: Submit crowdsourced civic issue with photo, category, and GPS.
- `GET /api/v1/citizen/activity`: Retrieve citizen's verified report count using internal `device_id_hash` (`device_id_hash` is an internal backend identifier and is never exposed publicly).
- `GET /api/v1/public/hazards/summary`: Anonymized hazard aggregates by ward/corridor.
- `GET /api/v1/public/aqi/summary`: Anonymized 24h spatial air quality trends.
- `GET /api/v1/public/road-health/summary`: Road segment roughness and health ratings.

### WebSocket
- `/ws/live`: Real-time broadcast stream with envelope `{"event_type": "...", "timestamp": "...", "data": {...}}`.
  - Supported event types: `bus_moved`, `incident_detected`, `incident_confirmed`, `work_order_updated`, `verification_completed`, `waterlogging_alert`.

---

## 12. Running Locally

### Backend & Ingestion API
```bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.

### Municipal Dashboard
```bash
# 1. Navigate to dashboard
cd dashboard

# 2. Install packages & run Vite dev server
npm install
npm run dev
```
Dashboard will be available at `http://localhost:5173`.

### Docker Compose (Full Stack)
```bash
docker compose up --build
```

---

## 13. Demo Mode (SIH Evaluation Flow)

The prototype includes an automated demonstration runner showcasing the entire **OBSERVE $\rightarrow$ DETECT $\rightarrow$ CONFIRM $\rightarrow$ PRIORITIZE $\rightarrow$ ACT $\rightarrow$ VERIFY** lifecycle.

> **Sensor Evidence vs. AI Conclusions Principle**:  
> The deterministic simulator generates **raw sensor evidence, NOT final AI conclusions**. It emits raw camera frame references and raw 3-axis IMU acceleration waveforms, rather than artificial hardcoded labels like `pothole_detected = true`. The AI models must independently process this evidence to make detections.

### End-to-End Evaluation Sequence:
1. **Raw Sensor Simulation (Observe)**: The deterministic simulator runs 12 buses along Vadodara routes emitting raw sensor data (`is_simulated = true`):
   - Camera simulation $\rightarrow$ raw camera frame/image references
   - IMU simulation $\rightarrow$ continuous raw 3-axis acceleration waveforms ($a_x, a_y, a_z$)
   - Environmental simulation $\rightarrow$ raw PM2.5, PM10, CO2 sensor readings
   - Water accumulation simulation $\rightarrow$ raw water reflection index and wheel rolling resistance
2. **AI & Signal Detection (Detect)**:
   - Camera simulation $\rightarrow$ camera frame/image $\rightarrow$ YOLO-nano CV model $\rightarrow$ structured pothole detection observation (`AIObservation`)
   - IMU simulation $\rightarrow$ 3-axis waveform $\rightarrow$ IMU anomaly detector $\rightarrow$ vibration shock anomaly observation (`AIObservation` with peak $a_z = 2.7g$)
   - Environmental stream $\rightarrow$ AQI anomaly detector flags localized particulate spike
3. **Spatio-Temporal Clustering & Multi-Modal Fusion (Confirm)**:
   - Spatio-temporal clustering groups AI observations within a 35m spatial radius and 10-minute window
   - Camera detection + IMU anomaly $\rightarrow$ Multi-Modal Sensor Fusion $\rightarrow$ eliminates false positives (e.g., road shadows or painted markings lack IMU shock)
   - Multi-bus corroboration elevates the cluster into a single canonical `CONFIRMED` `FusedIncident`
4. **Priority Scoring & Emergency Escalation (Prioritize)**:
   - Dynamic priority scoring ranks confirmed defects ($Severity \times Recurrence \times Corridor\,Tier$)
   - Monsoon Emergency Path: Heavy rainfall generates water reflection and drag signals evaluated as `waterlogging_severity = CRITICAL` at Akota Underpass $\rightarrow$ triggers immediate emergency WebSocket alert to `DISASTER_MGMT_OFFICER` (bypassing normal pothole repair queues)
5. **Municipal Work Order Dispatch (Act)**:
   - Municipal officer issues a digital Work Order to the VMC Roads division for confirmed road defects
6. **Autonomous Resolution Verification (Verify)**:
   - Contractor completes the repair $\rightarrow$ subsequent buses naturally traverse the repaired site during routine scheduled transit $\rightarrow$ IMU detector registers zero vertical shock and CV model detects no defect $\rightarrow$ incident auto-transitions to `VERIFIED_CLOSED`
7. **Citizen Feedback Loop & Open Civic Data**:
   - Citizen activity endpoint confirms repair resolution, incrementing `verified_report_count = 1` for the reporting device
   - Subsequent requests to the public aggregate endpoint (`/api/v1/public/hazards/summary`) reflect the updated aggregate
## Municipal Command Center Web Application (Phase 3)

The Phase 3 Command Center is built with React 19, Vite, TypeScript, Tailwind CSS, Leaflet, and Recharts. It connects to the FastAPI backend and streams live fleet events over WebSockets.

### Running the Dashboard

1. **Install dependencies** (if not already installed):
   `ash
   cd dashboard
   npm install --legacy-peer-deps
   `

2. **Environment configuration**:
   Ensure dashboard/.env exists:
   `env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   VITE_WS_URL=ws://localhost:8000/ws/live
   `

3. **Start the development server**:
   `ash
   npm run dev
   `
   Open [http://localhost:5173](http://localhost:5173) in your browser.

4. **Production Build**:
   `ash
   npm run build
   `

### Command Center Pages
- /dashboard: High-density municipal telemetry map, top 6 real KPIs, corridor road health rating, live WebSocket telemetry log, and SIH demonstration controls.
- /fleet: Live interactive map tracking all 12 transit buses with heading, speed, passenger occupancy, and corridor filtering.
- /incidents: Filterable and sortable road defect registry with AI confidence, corroboration count, and priority ranking.
- /incidents/:id: Deep forensic viewer displaying raw CV bounding boxes, 3-axis accelerometer waveform metrics, multi-sensor agreement badges, and life-cycle resolution dispatch.
- /emergency: Dedicated Disaster Management Command console for rapid response to critical urban waterlogging and hydroplaning hazards.
- /road-health: Segment-level pavement roughness (IRI) and defect density comparisons across all 6 monitored Vadodara transit corridors.
- /work-orders: Municipal repair dispatch workflow with autonomous transit bus pass-by verification audits.
