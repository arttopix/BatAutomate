# AI Developer Agent Guidelines (.agent/)

> **โฟลเดอร์สำหรับ AI Pair-Programming Assistant (ไม่ใช่ Unattended Robot Worker)**  
> โฟลเดอร์ `.agent/` นี้มีไว้เก็บข้อกำหนด ทิศทางสถาปัตยกรรม และกฎเกณฑ์ในการเขียนโค้ดสำหรับ AI Agent ที่ช่วยพัฒนาโครงการ BAT Automate (ส่วน Robot Daemon สำหรับรันงานอัตโนมัติบนเครื่องปลายทางคือโมดูล `bat-worker`)

---

## จุดเด่นของ BAT Automate (Key Highlights)

- **Local AI-Native Architecture:** สถาปัตยกรรมที่ออกแบบมาเพื่อ Small Language Models (SLMs) ทำงานแบบ On-Device บน CPU ได้ 100% (เช่น Qwen, Llama) รองรับการสร้างโฟลว์อัตโนมัติ (Flow Generation), ระบบซ่อมแซม Selector อัจฉริยะ (Self-Healing Selectors), และวิเคราะห์ Error เป็นภาษาธุรกิจโดยไม่มีค่า API Token และข้อมูลไม่รั่วไหล
- **Zero-License Dependency:** ไม่จำเป็นต้องมี Microsoft 365, ไม่ต้องติดตั้ง Microsoft Excel สำหรับงานจัดการไฟล์สเปรดชีต (ประมวลผลผ่าน `openpyxl` และ `pandas` โดยตรง)
- **Business-First Dashboard:** ออกแบบมาเพื่อผู้บริหารและฝ่ายธุรกิจ เห็นตัวเลขความคุ้มค่า (ROI), จำนวนชั่วโมงที่ประหยัดได้ (Hours Saved), และมูลค่าเงินที่ประหยัดได้จริง
- **Free Unlimited Unattended Workers:** ติดตั้ง Agent เพื่อสั่งรันอัตโนมัติบน VM, PC เครื่องเก่า, หรืออุปกรณ์ Edge (เช่น Raspberry Pi) ได้ไม่จำกัดจำนวน โดยไม่มีค่า License รายเดือน
- **Python Power & Flexibility:** ขยาย Action และความสามารถเพิ่มเติมได้ง่ายด้วยภาษา Python ทำงานร่วมกับ Web (Playwright), API, Database, และ AI ได้อย่างไร้ขีดจำกัด

---

## สถาปัตยกรรมระบบ (Core Modules)

BAT Automate แบ่งโครงสร้างออกเป็น 4 ส่วนหลัก:

```text
BatAutomate/
├── bat-core/                   # Python Package Module (Runtime Engine)
│   ├── pyproject.toml          # Package metadata & build configuration
│   ├── requirements.txt
│   ├── batautomate/            # Core Python Package (Flat layout: actions, engine, models, cli)
│   │   ├── actions/            # Web (Playwright), Excel, API, Logic, System
│   │   ├── engine/             # Flow Interpreter, Variable Context, Evaluator, Logger
│   │   ├── models/             # Flow JSON Schema (Pydantic models)
│   │   └── cli.py              # CLI Runner (batautomate)
│   └── tests/                  # Pytest unit tests
│
├── flows/                      # Workflows & Self-Contained Project Bundles
│   ├── @shared/                # Cross-project reusable flows (LINE alerts, SSO login)
│   └── benchmarks/
│       └── rpachallenge/       # Self-contained project bundle (flow.json, subflows, assets)
│
├── logs/                       # Central Structured Execution Logs (Hierarchical JSON)
│
├── bat-studio/                 # Visual Flow Designer & UI Inspector (Desktop App - Planned)
├── bat-orchestrator/           # Central Control Hub & Business Dashboard (Planned)
└── bat-worker/                 # Unattended / Attended Robot Daemon (Planned)
```

| โมดูล | บทบาทหน้าที่ | เทคโนโลยีหลัก |
| :--- | :--- | :--- |
| **BAT Core (`bat-core`)** | หัวใจการรันคำสั่ง ประมวลผล Flow JSON และ Agentic Subflows, จัดการตัวแปร, ทำงานกับ Web & Excel | Python, Playwright, Pandas, OpenPyXL |
| **BAT Studio (`bat-studio`)** | โปรแกรม Desktop สำหรับลาก-วางสร้าง Flow และเครื่องมือชี้จับ UI Selector | Tauri, React, React Flow, TypeScript |
| **BAT Orchestrator (`bat-orchestrator`)** | ศูนย์กลางคุมงาน ตั้งเวลา (Scheduler), Dashboard ติดตามผลลัพธ์ธุรกิจ, แจ้งเตือน LINE/Teams/Email | FastAPI, PostgreSQL, Redis, React, TailwindCSS |
| **BAT Worker (`bat-worker`)** | Background Daemon ติดตั้งบนเครื่องเป้าหมาย รอรับงานจาก Orchestrator ไปรัน | Python Service, WebSocket |

---

## แผนการพัฒนา (Development Roadmap)

- [ ] **Phase 1: Foundation & Core Engine (`bat-core`)**
  - [x] ออกแบบ Flow JSON Schema และ Pydantic Models
  - [x] สร้าง Core Interpreter, Context Manager และตัวจัดการตัวแปร (`${var}`)
  - [x] พัฒนา Action พื้นฐาน: Web (Playwright), Excel (`openpyxl`), Logic, HTTP API
  - [x] Hierarchical Structured Logging (`logs/<flow>/<date>/<time>.json`)
  - [x] Global CLI & Smart Flow Resolver (`batautomate list`, `batautomate run <flow_name>`)
  - [ ] สถาปัตยกรรมโครงสร้างโปรเจกต์และระบบ Subflow (`flow.call`, เรียกใช้โมดูลกลาง `@shared/`)
- [ ] **Phase 2: Visual Designer & Selector (`bat-studio`)**
  - สร้าง Canvas ลาก-วางด้วย React Flow บน Tauri Desktop Shell
  - พัฒนา Web UI Selector สำหรับจับ Element อัตโนมัติ
  - ระบบทดสอบ Local Run & Debugger
- [ ] **Phase 3: Central Server & Business Dashboard (`bat-orchestrator`)**
  - Backend API (FastAPI) + PostgreSQL + Redis
  - Business Dashboard: คำนวณเวลาและเงินที่ประหยัดได้ (ROI), รายการ Transaction
  - ระบบแจ้งเตือน Error และสรุปผลประจำวันผ่าน LINE (Messaging API), Teams, Email
- [ ] **Phase 4: Unattended Agent Daemon (`bat-worker`)**
  - WebSocket Agent Service คุยกับ Orchestrator
  - จัดการ Isolated Process และ Stream Real-time Logs / Screenshots
- [ ] **Phase 5: Desktop Automation & Community Open Source Release**
  - เพิ่ม Windows Desktop UI Automation (`uiautomation`)
  - จัดทำ Docker Compose 1-Click Deployment และคู่มือ Quick Start บน GitHub
- [ ] **Phase 6: Local AI-Native Agentic Capabilities**
  - ผสานการทำงานกับ Local SLM บน CPU (เช่น Qwen 2.5, Llama 3.2 ผ่าน GGUF / Ollama)
  - ระบบ Self-Healing UI Selector และ Agentic Decision Steps ทำงานอัตโนมัติ
  - Studio Copilot สำหรับแปลงภาษาธรรมชาติเป็น Flow และวิเคราะห์หาสาเหตุของ Error (Root-Cause Analysis)

---

## สถาปัตยกรรมโปรเจกต์และวงจรชีวิตการทำงาน (Project Bundle & Unattended Lifecycle)

เพื่อรองรับการพัฒนางานอัตโนมัติระดับองค์กร ระบบกำหนดโครงสร้างโฟลเดอร์แบบ **Self-Contained Project Bundle** โดยแบ่งตามแผนกธุรกิจและมีโฟลเดอร์ `@shared/` สำหรับโมดูลส่วนกลาง:

```text
flows/
├── @shared/                                # คลัง Flow ส่วนกลาง (LINE Alert, SSO Login)
└── accounting/                             # แยกตามแผนกธุรกิจ
    └── invoice_tax_filing/                 # 1 โครงการ = 1 โฟลเดอร์อิสระ
        ├── flow.json                       # Entry point หลัก
        ├── subflows/                       # งานย่อยภายในโครงการ
        └── assets/                         # ไฟล์ประกอบและ Template
```

### ขั้นตอนการส่งมอบงานสู่เครื่อง Unattended Robot:
1. **Local Development:** พัฒนาและทดสอบผ่าน CLI หรือ Studio โดยใช้ Relative Path เสมอ
2. **Packaging:** รวมโฟลเดอร์โปรเจกต์เป็นไฟล์แพ็กเกจเดี่ยว (เช่น `.batpkg` หรือ `.zip`) พร้อมสำเนา `@shared/` ที่จำเป็นเข้ามาในตัว
3. **Distribution & Cache:** Worker บนเครื่องเป้าหมายดาวน์โหลดแพ็กเกจจาก Orchestrator มาเก็บใน Local Cache
4. **Sandbox Workspace:** แตกไฟล์ลงโฟลเดอร์เฉพาะกิจของแต่ละ Job เพื่อแยกพื้นที่ทำงานและป้องกันปัญหาไฟล์ชนกัน
5. **Execution & Telemetry:** รันผ่าน `bat-core` ในกระบวนการแยก และสตรีม Log แบบเรียลไทม์ผ่าน WebSocket

---

## ลิขสิทธิ์ (License)

โครงการนี้เผยแพร่ภายใต้สัญญาอนุญาตแบบ Open Source (MIT License)
