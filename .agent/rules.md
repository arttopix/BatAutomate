# BAT Automate - Project Rules & Guidelines (.agent/rules.md)

ไฟล์นี้เก็บกฎระเบียบ ข้อกำหนดทางสถาปัตยกรรม (Architecture Decisions) และแนวทางการพัฒนาสำหรับโครงการ **BAT Automate** เพื่อให้ AI Agent และทีมนักพัฒนาปฏิบัติตามอย่างเคร่งครัด

---

## 1. วิสัยทัศน์และเป้าหมายหลัก (Core Vision & Principles)

1. **Open-Source & Free Forever:** 
   - ระบบ Core, Studio, Orchestrator และ Worker ต้องเป็น Open-source ไม่มีระบบคิดเงินตามจำนวนบอท
2. **Zero-License Dependency สำหรับ Office:**
   - การจัดการไฟล์ Excel (`.xlsx`, `.csv`) ต้องทำผ่านไลบรารีระดับไฟล์ เช่น `openpyxl` หรือ `pandas` เสมอ
   - **ห้าม** บังคับให้เครื่องผู้ใช้หรือ Worker ต้องมี Microsoft 365 หรือติดตั้งโปรแกรม Microsoft Excel
3. **Business-First Mindset:**
   - ระบบ Telemetry, Logging และ Dashboard ต้องเก็บข้อมูลในมุมมองธุรกิจ (จำนวน Transaction, Hours Saved, Cost Saved) เสมอ ไม่ใช่เก็บเฉพาะ Technical Stack Trace
4. **Local AI-Native & Agentic Architecture:**
   - ออกแบบสถาปัตยกรรมระบบตั้งแต่ระดับรากฐานให้เป็น **Local AI-Native**: มุ่งเน้นการประมวลผล On-Device ผ่าน **Small Language Models (SLM)** ที่รันบน **CPU** ในเครื่องได้ 100% (เช่น Qwen, Llama ผ่าน `llama-cpp-python`, ONNX, หรือ Ollama)
   - ผสานการทำงานแบบไฮบริดระหว่าง **Deterministic Flow Execution** (รันตามเงื่อนไขแม่นยำ 100%) และ **Agentic Autonomy** (เช่น Self-Healing Selectors, Smart Data Extraction, Autonomous Decision Steps) โดยไม่มีค่า API Token ภายนอกและข้อมูลภายในองค์กรปลอดภัยสูงสุด
5. **Sponsorship & Donation Roadmap:**
   - ในอนาคตมีแผนเปิดรับเงินบริจาคและผู้สนับสนุน (GitHub Sponsors, Open Collective, Buy Me a Coffee) เพื่อความยั่งยืนของโครงการ แต่ในระยะนี้ (Phase ปัจจุบัน) **ยังไม่เปิดรับ** ให้มุ่งเน้นการพัฒนา Core และ Feature หลักก่อน

---

## 2. ข้อกำหนดทางเทคนิคแต่ละโมดูล (Module Stack Standards)

| โมดูล | เทคโนโลยีที่กำหนด | กฎเกณฑ์ที่ต้องปฏิบัติตาม |
| :--- | :--- | :--- |
| **`bat-core`** | Python 3.10+, Playwright, OpenPyXL, Pandas, Pydantic | • ต้องเป็นอิสระจาก GUI (Headless-ready)<br>• ออกแบบ Action ในลักษณะ Plugin Architecture (`BaseAction`)<br>• มีระบบประเมินตัวแปร `${var}` ที่ปลอดภัย<br>• รองรับสถาปัตยกรรม Project Bundle (`flow.json`, `subflows/`, `assets/`) และ Action `flow.call` เพื่อเรียก Subflow และ `@shared/` |
| **`bat-studio`** | Desktop App ด้วย **Tauri + React + React Flow** | • ตัว Canvas เขียนด้วย React Component มาตรฐาน เพื่อให้นำไปเปิดบน Web Orchestrator ในอนาคตได้<br>• ตัวจับ UI (Selector) ต้องสร้าง Selector หลายชั้น (XPath, Text, Id, CSS) เพื่อความเสถียร |
| **`bat-orchestrator`** | FastAPI, PostgreSQL, Redis, React Dashboard | • รองรับการแจ้งเตือนงานสำเร็จและ Error ไปที่ **LINE (Messaging API)** เป็นอันดับแรก ตามด้วย Teams และ Email<br>• มี Dashboard คำนวณ ROI สำหรับผู้บริหาร |
| **`bat-worker`** | Python Daemon / Windows Service, WebSocket | • ติดตั้งบนเครื่องเป้าหมายเพื่อรอรับงานจาก Orchestrator ผ่าน WebSocket<br>• มีระบบถ่าย Screenshot และสตรีม Log เรียลไทม์เมื่อเกิด Error |

---

## 3. มาตรฐานการจัดการข้อผิดพลาด (Exception Standards)

ในการเขียน Action หรือ Flow ต้องแยกประเภท Error ออกเป็น 2 กลุ่มเสมอ:
1. **Technical Exception (ข้อผิดพลาดเชิงเทคนิค):**
   - เช่น Network Timeout, เว็บล่ม, Selector หาไม่เจอหลัง Retry แล้ว
   - ผู้รับผิดชอบ: RPA Developer
2. **Business Exception (ข้อผิดพลาดเชิงธุรกิจ):**
   - เช่น ยอดเงินในใบเสร็จไม่ตรง, ข้อมูลใน Excel ไม่ครบถ้วน, รหัสลูกค้าถูกระงับ
   - ผู้รับผิดชอบ: แผนกธุรกิจ / ผู้ใช้งาน (แสดงภาพและสถานะชัดเจนบน Dashboard และ LINE)

---

## 4. กฎการทำงานร่วมกับผู้ใช้ (User Collaboration Rules)

- สอบถามหรืออธิบายพิมพ์เขียว (Blueprint) ให้ผู้ใช้เห็นภาพก่อนเริ่มลงมือเขียนโค้ดชุดใหญ่เสมอ
- ก่อนรันคำสั่ง Terminal หรือ Shell ใดๆ ต้องแน่ใจว่าได้รับอนุญาตจากผู้ใช้ หรืออธิบายเป้าหมายของคำสั่งนั้นอย่างชัดเจน
- หากมีการเพิ่มหรือเปลี่ยนแปลงกฎใหม่ ให้อัปเดตเข้ามาที่ไฟล์ `.agent/rules.md` นี้อย่างต่อเนื่อง

---

## 5. กฎด้านรูปแบบเนื้อหาและการสร้างไฟล์ (Formatting & Content Rules)

- **No Emojis:** ไม่ต้องใส่ emoji หรือสัญลักษณ์ไอคอนรูปอารมณ์ลงในโค้ด, Markdown, เอกสาร, ไฟล์ หรือเนื้อหาที่สร้างขึ้นทุกชนิด
- **Execution Documentation Required:** ทุกโมดูลที่สร้างขึ้น ต้องจัดทำคู่มือการใช้งานและการสั่งรันคำสั่ง (CLI / Execution Guide) ไว้ใน README.md ของโมดูลนั้นๆ อย่างครบถ้วน
- **CLI Standard Commands:** เครื่องมือ CLI ของระบบต้องรองรับคำสั่งพื้นฐานเสมอ: `version` (เช็คเลขเวอร์ชัน, Python, OS), `list` (แสดงรายการ Flow), และ `run <flow>` (Smart Flow Resolver)

---

## 6. ข้อกำหนดการเตรียมความพร้อมสำหรับ AI / LLM ในอนาคต (Future LLM & AI Readiness Standards)

เพื่อให้ระบบพร้อมเชื่อมต่อกับ LLM ใน Phase ถัดไปได้อย่างไร้รอยต่อ โดยไม่ต้องรื้อโค้ดแกนกลาง:

1. **Structured Error Telemetry:**
   - ทุกครั้งที่เกิด Error ตัว Engine ต้องบันทึกบริบท (Context) รอบข้างอย่างละเอียดในรูปแบบ JSON เสมอ (เช่น URL หน้าเว็บ, Selector ที่หาไม่เจอ, แถวข้อมูลใน Excel, และพาทภาพ Screenshot) เพื่อให้ LLM สามารถอ่านและวิเคราะห์หาสาเหตุที่แท้จริง (Root Cause) ได้ทันที
2. **Event Hooks & Callback Interface:**
   - ตัว `bat-core` (Interpreter) ต้องเตรียม Event Hooks เช่น `on_step_error`, `on_flow_complete` เพื่อให้โมดูล AI Monitoring ในอนาคตสามารถเข้ามาดักฟังและส่งข้อความแจ้งเตือนได้โดยไม่ต้องแก้ไขโค้ดของ Core
3. **Decoupled AI Service (แยกโมดูลอิสระ):**
   - โมดูล AI Copilot และ LLM Monitoring ต้องทำงานในลักษณะ Add-on / Sidecar Service แยกจาก `bat-core` เสมอ เพื่อให้ Core Engine ยังคงความเร็ว เบา และรันได้โดยไม่ต้องติดตั้งโมเดลขนาดใหญ่
4. **Local SLM on CPU First:**
   - การนำโมเดลภาษามาใช้เป็นตัวช่วย Monitor ต้องมุ่งเน้น Small Language Models (เช่น Qwen 2.5 หรือ Llama 3.2 ขนาด 1B - 3B) ผ่านระบบ Quantization (GGUF / ONNX) ที่ประมวลผลบน CPU ได้ 100% เพื่อไม่ให้มีค่าใช้จ่าย API Token และปลอดภัยต่อข้อมูลภายในองค์กร

---

## 7. แผนการพัฒนาระบบบันทึกประวัติการทำงาน (Logging Architecture Roadmap)

1. **Auto-Generate Default Clean JSON Log (ดำเนินการแล้ว):**
   - ทุกครั้งที่สั่งรัน Flow ตัว Engine ต้องสร้างโฟลเดอร์ `logs/` และบันทึกไฟล์ Structured JSON Log (`log_YYYYMMDD_HHMMSS.json`) อัตโนมัติ โดยทำการกรองตัวแปรภายในระบบ (`__*`) ออก เพื่อให้ไฟล์สะอาด พร้อมสำหรับทั้งการตรวจสอบของมนุษย์และการอ่านของ AI
2. **Central WebSocket Log Streaming (Phase 3 - bat-orchestrator):**
   - ส่งสตรีม Log แบบ Real-time จาก Worker ผ่าน WebSocket ไปยัง Orchestrator เพื่อบันทึกลง PostgreSQL และนำไปพล็อตกราฟ Business Dashboard
3. **LLM Error Diagnosis & Instant Alert (Phase AI Integration):**
   - เมื่อมี Step ที่เกิด Error ให้นำบล็อกข้อมูล JSON ของข้อผิดพลาดนั้น ส่งให้โมเดลภาษาช่วยวิเคราะห์และสรุปผลเป็นภาษาธุรกิจส่งแจ้งเตือนเข้า LINE ทันที



