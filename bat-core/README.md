# bat-core

Execution Runtime Engine and Standard Action Libraries for BAT Automate RPA Platform.

## Directory Structure

```text
bat-core/
├── pyproject.toml          # Project configuration & dependencies
├── requirements.txt        # Package dependencies list
├── README.md               # Documentation
├── bat_core/               # Core Python Package
│   ├── __init__.py
│   ├── cli.py              # CLI Runner
│   ├── models/             # Flow & Execution Models (Pydantic)
│   │   ├── __init__.py
│   │   ├── flow.py
│   │   └── context.py
│   ├── engine/             # Flow Interpreter & Evaluator Engine
│   │   ├── __init__.py
│   │   ├── interpreter.py
│   │   ├── evaluator.py
│   │   └── logger.py
│   └── actions/            # Action Libraries & Registry
│       ├── __init__.py
│       ├── base.py
│       ├── registry.py
│       ├── logic.py
│       ├── data_excel.py
│       ├── web_playwright.py
│       └── http_api.py
├── examples/               # Sample Flow JSON files
│   └── sample_flow.json
└── tests/                  # Unit Tests
    └── test_engine.py
```

---

## คู่มือการใช้งานและการสั่งรันคำสั่ง (CLI Execution Guide)

โมดูล `bat-core` สามารถสั่งรันกระบวนการอัตโนมัติ (RPA Flow) ผ่าน Command Line Interface (CLI) ได้ดังนี้:

### 1. การติดตั้งแบบ Editable (สำหรับการพัฒนา)

ติดตั้ง Package และ Dependencies ในสภาพแวดล้อม Python:
```powershell
pip install -e .
```

### 2. รูปแบบคำสั่งการรันและ Smart Flow Resolver

เมื่อติดตั้ง Package แล้ว สามารถเรียกใช้คำสั่งสากล `batautomate` ได้ทันที โดยระบบมี **Smart Flow Resolver** ที่ช่วยค้นหาไฟล์ Flow ให้อัตโนมัติโดยไม่ต้องระบุ Path ยาวๆ:

- **ตรวจสอบเวอร์ชันและข้อมูลสภาพแวดล้อม (Version & Environment Info):**
  ```powershell
  batautomate version
  # หรือ
  batautomate --version
  ```

- **ติดตั้งเบราว์เซอร์ Playwright สำหรับ Web Automation:**
  ```powershell
  batautomate install-browsers
  ```
  *(หรือปล่อยให้ระบบดาวน์โหลดอัตโนมัติเมื่อสั่งรัน Web Flow ในครั้งแรก)*

- **ค้นหาและแสดงรายการ Flow ทั้งหมดในเครื่อง (เหมือน `ollama list`):**
  ```powershell
  batautomate list
  ```

- **สั่งรัน Flow ด้วยชื่อสั้น (Smart Flow Resolver):**
  ```powershell
  batautomate run rpachallenge
  batautomate run sample
  ```
  *(ระบบจะทำการค้นหาชื่อไฟล์อัตโนมัติจากโฟลเดอร์ปัจจุบัน, `flows/`, `examples/`, และ `~/.batautomate/flows/` โดยผู้ใช้ไม่จำเป็นต้องพิมพ์ `.json` หรือ Path เต็ม)*

- **หรือสั่งรันผ่าน Full Path โดยตรง:**
  ```powershell
  batautomate run examples/sample_flow.json
  ```

### 3. ตัวเลือกและพารามิเตอร์เสริม (CLI Options)

- **`--vars` (Override / Inject Variables):** ส่งค่าตัวแปรจากภายนอกเข้าไปใน Flow รูปแบบ JSON String
  ```powershell
  python -m bat_core.cli run examples/sample_flow.json --vars "{\"target_url\": \"https://httpbin.org/get\"}"
  ```

- **`--log-dir` (Save Execution Logs):** กำหนดไดเรกทอรีสำหรับบันทึกไฟล์ JSON Execution Log
  ```powershell
  python -m bat_core.cli run examples/sample_flow.json --log-dir "./logs"
  ```

### 4. การรันชุดทดสอบ (Unit Testing)

ทดสอบความถูกต้องของระบบและ Action ทั้งหมด:
```powershell
python -m pytest tests/
```

---

## มาตรฐานโครงสร้างการจัดเก็บ Log (Logging Architecture Standards)

ระบบ `bat-core` ออกแบบการจัดเก็บประวัติการทำงานในรูปแบบ **Structured JSON Log** เพื่อรองรับทั้งการตรวจสอบของผู้ดูแลระบบ (Human Monitor) และการประมวลผลของ AI Monitoring:

### 1. โครงสร้างโฟลเดอร์แบบแบ่งลำดับชั้น (Hierarchical Partitioning)

เพื่อความสะดวกในการ Filter ค้นหาตามชื่องานและช่วงเวลา:

```text
logs/
├── rpa_challenge_solver/               # แยกโฟลเดอร์ตามชื่อ Flow
│   └── 2026-09-10/                     # แยกโฟลเดอร์ตาม วันที่รัน (YYYY-MM-DD)
│       ├── 205243_success.json         # ชื่อไฟล์: [เวลา]_[สถานะ].json
│       └── 213111_success.json
└── invoice_tax_filing/
    └── 2026-09-11/
        ├── 083000_success.json
        └── 091500_failed.json          # ไฟล์ Error มองเห็นและคัดแยกได้ทันที
```

### 2. โครงสร้างข้อมูล JSON Log (Schema Highlights)

- **`flow_name` & `start_time`:** ข้อมูลระบุชื่องานและเวลาเริ่มต้น (ISO 8601)
- **`metrics`:** ข้อมูลสรุปภาพรวมทางธุรกิจ เช่น จำนวน Step สำเร็จ/ล้มเหลว, เวลารวม, ชั่วโมงที่ประหยัดได้ (Hours Saved)
- **`variables` (State Snapshot):** ภาพถ่ายข้อมูลตัวแปรล่าสุดในระบบ (กรองตัวแปรเทคนิคภายในอย่าง `__playwright_*` ออกอัตโนมัติ)
- **`step_results`:** ประวัติการประมวลผลย่อยทีละ Step ระบุ Action, ระยะเวลาหน่วยวินาที, Output และรายละเอียด Error แยกประเภท `Technical` หรือ `Business`


