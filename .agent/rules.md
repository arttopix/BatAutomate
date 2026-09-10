# 📜 BAT Automate - Project Rules & Guidelines (.agent/rules.md)

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
4. **Local AI & Privacy Ready:**
   - การเพิ่มความสามารถด้าน AI ต้องมุ่งเน้น **Small Language Models (SLM)** ที่รันบน **CPU** ในเครื่องได้ (เช่น Qwen 2.5, Llama 3.2 ผ่าน `llama-cpp-python` / `onnxruntime`) เพื่อความปลอดภัยของข้อมูลและไม่มีค่า API Token

---

## 2. ข้อกำหนดทางเทคนิคแต่ละโมดูล (Module Stack Standards)

| โมดูล | เทคโนโลยีที่กำหนด | กฎเกณฑ์ที่ต้องปฏิบัติตาม |
| :--- | :--- | :--- |
| **`bat-core`** | Python 3.10+, Playwright, OpenPyXL, Pandas, Pydantic | • ต้องเป็นอิสระจาก GUI (Headless-ready)<br>• ออกแบบ Action ในลักษณะ Plugin Architecture (`BaseAction`)<br>• มีระบบประเมินตัวแปร `${var}` ที่ปลอดภัย |
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

