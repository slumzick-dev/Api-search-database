# Data Breach Search API

API สำหรับค้นหาข้อมูลจากฐานข้อมูลที่รั่วไหล (Data Breach Database)
ออกแบบมาเพื่อการตรวจสอบความปลอดภัย การวิเคราะห์ข้อมูล และงานด้าน Cybersecurity

⚠️ คำเตือนทางกฎหมาย (Legal Warning)
โปรเจกต์นี้จัดทำขึ้นเพื่อการศึกษา การวิจัย และการป้องกันด้านความปลอดภัยเท่านั้น
ห้ามนำไปใช้ในทางที่ผิดกฎหมาย ผู้ใช้งานต้องรับผิดชอบต่อการใช้งานทั้งหมด


## คุณสมบัติ (Features)

- ค้นหาข้อมูลจากฐานข้อมูลที่รั่วไหล
- REST API ทำงานรวดเร็วด้วย FastAPI
- รองรับการ Export ข้อมูล
- ค้นหาแบบหลายเงื่อนไข (Multi Match)
- รองรับการใช้งานทั้ง Local และ VPS


## เทคโนโลยีที่ใช้ (Tech Stack)

- Python 3.8+
- FastAPI
- Uvicorn
- RESTful API


## การติดตั้ง (Installation)

pip install -r requirements.txt


## การรันเซิร์ฟเวอร์ (Run Server)

โหมดพัฒนา (Development)

uvicorn api_server_v2:app --reload

เข้าถึงได้ที่
http://127.0.0.1:8000


โหมด Multi Match

uvicorn api_server_v2_multi_match:app --reload


โหมด Production / VPS

uvicorn api_server_v2_multi_match:app --host 0.0.0.0 --port 8000


## วิธีใช้งาน API (API Usage)

ตรวจสอบสถานะ API

GET /

ตัวอย่าง
http://127.0.0.1:8000


ค้นหาข้อมูล (Search)

GET /search

พารามิเตอร์
- q : คำค้นหา (domain / email / keyword)
- limit : จำนวนผลลัพธ์สูงสุด

ตัวอย่าง
http://127.0.0.1:8000/search?q=facebook.com&limit=100


Export ข้อมูล

GET /export

พารามิเตอร์
- q : คำค้นหา
- mode : รูปแบบข้อมูล (เช่น raw)
- d : ตัวเลือกเพิ่มเติม

ตัวอย่าง
http://127.0.0.1:8000/export?q=facebook.com&mode=raw&d=0


## ตัวอย่างการใช้งาน (Use Cases)

- ตรวจสอบว่าโดเมนหรืออีเมลมีข้อมูลรั่วไหลหรือไม่
- ใช้ในงาน Incident Response
- งานด้าน Cybersecurity (Red Team / Blue Team)
- วิเคราะห์ข้อมูลจาก Data Breach เพื่อเพิ่มความปลอดภัย


## ข้อจำกัดและความรับผิดชอบ

- ห้ามใช้เพื่อการละเมิดสิทธิ์หรือกฎหมาย
- ใช้เพื่อการศึกษาและการป้องกันเท่านั้น
- ผู้ใช้งานต้องปฏิบัติตามกฎหมายของประเทศตนเอง


## ช่องทางติดต่อ (Contact)

YouTube
slumzick
https://www.youtube.com/@slumzick

Facebook
https://www.facebook.com/slumsick

Telegram (Developer Group)
https://t.me/slumzick_dev

หมายเหตุด้านความปลอดภัย
สำหรับประเด็นด้านความปลอดภัย กรุณาติดต่อผ่าน Telegram โดยตรง
และหลีกเลี่ยงการเผยแพร่ข้อมูลสำคัญในที่สาธารณะ


## ผู้พัฒนา (Author)

Slumzick Team
โฟกัสด้าน Cybersecurity, Data Analysis และ Security Research


## License

MIT License
โปรดดูรายละเอียดเพิ่มเติมในไฟล์ LICENSE
