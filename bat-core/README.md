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

### 2. รูปแบบคำสั่งการรันพื้นฐาน

รันผ่านสคริปต์ Python Module:
```powershell
python -m bat_core.cli run examples/sample_flow.json
```

หรือรันผ่านคำสั่ง CLI สั้น (เมื่อทำการติดตั้ง Package แล้ว):
```powershell
bat-core run examples/sample_flow.json
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

