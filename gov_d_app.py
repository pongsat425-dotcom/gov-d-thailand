import streamlit as st
import google.generativeai as genai
import pandas as pd
git config --global user.email "pongsat425@gmail.com"
git config --global user.name "pongsat425-dotcom"
git init
git add gov_d_app.py requirements.txt
git commit -m "First upload from server"
git branch -M main
git remote add origin https://github.com/pongsat425-dotcom/gov-d-thailand
git push -u origin main
# --- ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="Gov-D: ศูนย์ข้อมูลภาครัฐอัจฉริยะ",
    page_icon="🏛️",
    layout="wide"
)

# --- ส่วนตั้งค่า API (ใส่ Key ของคุณที่นี่) ---
# เพื่อความปลอดภัยในการนำเสนอจริง ควรซ่อน Key ไว้ใน secrets
api_key = st.sidebar.text_input("🔑 ใส่ Gemini API Key ของคุณที่นี่:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

# --- ข้อมูลจำลอง (Mock Data) สำหรับฟีเจอร์ติดตามโครงการ ---
mock_projects = pd.DataFrame({
    "ชื่อโครงการ": ["สร้างสะพานข้ามแยก A", "ขุดลอกคลอง B", "Digital Wallet 10,000", "ปรับปรุงสวนสาธารณะ C"],
    "งบประมาณ (ล้านบาท)": [150, 45, 500000, 20],
    "ความคืบหน้า": ["80%", "100%", "กำลังพิจารณา", "30%"],
    "สถานะ": ["ล่าช้าเล็กน้อย", "เสร็จสิ้น", "รอประกาศ", "ตามแผน"],
    "หน่วยงาน": ["กรมทางหลวง", "กรมชลประทาน", "กระทรวงการคลัง", "กทม."]
})

# --- ส่วนติดต่อผู้ใช้ (UI) ---
st.title("🏛️ Gov-D (Government Digital Dialogue)")
st.caption("ระบบประชาสัมพันธ์และช่วยเหลือประชาชนอัจฉริยะระดับชาติ")

# เมนูเลือกฟีเจอร์
menu = st.sidebar.radio("เลือกบริการ:", ["🤖 พูดคุยกับ Gov-AI", "🏗️ ติดตามโครงการรัฐ", "⚖️ ที่ปรึกษากฎหมาย"])

# --- ฟีเจอร์ 1: Chatbot (General Q&A) ---
if menu == "🤖 พูดคุยกับ Gov-AI":
    st.header("💬 สอบถามข้อมูล/ตรวจสอบข่าวลือ")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # แสดงประวัติแชท
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # รับคำถามจาก User
    if prompt := st.chat_input("พิมพ์คำถามของคุณที่นี่... (เช่น ข่าวแจกเงินจริงไหม?)"):
        if not api_key:
            st.warning("กรุณาใส่ API Key ก่อนใช้งานครับ")
            st.stop()
            
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI ตอบกลับ
        with st.chat_message("assistant"):
            with st.spinner("Gov-AI กำลังตรวจสอบข้อมูลจากฐานข้อมูลภาครัฐ..."):
                try:
                    # System Prompt เพื่อคุมคาแรคเตอร์
                    system_instruction = """
                    คุณคือ 'Gov-AI' ผู้ช่วยอัจฉริยะของรัฐบาลไทย
                    หน้าที่: ตอบคำถามประชาชนด้วยภาษาที่สุภาพ เข้าใจง่าย และถูกต้องแม่นยำ
                    ถ้าเป็นเรื่องสิทธิประโยชน์ ให้แนะนำขั้นตอนที่ชัดเจน
                    ถ้าเป็นข่าวลือ ให้เตือนด้วยความระมัดระวัง
                    ตอบสั้นกระชับ ไม่เยิ่นเย้อ
                    """
                    full_prompt = f"{system_instruction}\n\nUser: {prompt}"
                    response = model.generate_content(full_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")

# --- ฟีเจอร์ 2: Project Tracker (Transparency) ---
elif menu == "🏗️ ติดตามโครงการรัฐ":
    st.header("🏗️ ตรวจสอบโครงการภาครัฐ")
    st.write("ตรวจสอบความโปร่งใสและความคืบหน้าโครงการต่างๆ")
    
    # ค้นหาโครงการ
    search_query = st.text_input("ค้นหาชื่อโครงการ หรือ หน่วยงาน")
    
    if search_query:
        # กรองข้อมูล (Filter Mock Data)
        filtered_df = mock_projects[mock_projects['ชื่อโครงการ'].str.contains(search_query) | mock_projects['หน่วยงาน'].str.contains(search_query)]
        st.dataframe(filtered_df, use_container_width=True)
        
        # ให้ AI วิเคราะห์ข้อมูลโครงการที่เจอ
        if not filtered_df.empty and api_key:
            if st.button("🤖 ให้ AI วิเคราะห์สถานะโครงการนี้"):
                project_info = filtered_df.to_string()
                analysis_prompt = f"วิเคราะห์สถานะโครงการนี้ให้ประชาชนเข้าใจง่ายๆ สั้นๆ ว่าน่ากังวลไหม: {project_info}"
                response = model.generate_content(analysis_prompt)
                st.info(response.text)
    else:
        st.dataframe(mock_projects, use_container_width=True)

# --- ฟีเจอร์ 3: Legal Simplifier (Law Assistant) ---
elif menu == "⚖️ ที่ปรึกษากฎหมาย":
    st.header("⚖️ แปลภาษากฎหมายเป็นภาษาชาวบ้าน")
    
    law_text = st.text_area("วางข้อความกฎหมาย หรือ สัญญา ที่คุณไม่เข้าใจที่นี่:", height=150)
    
    if st.button("แปลให้เข้าใจง่าย") and api_key:
        with st.spinner("AI ทนายความกำลังอ่านเอกสาร..."):
            simplifier_prompt = f"""
            ช่วยสรุปข้อกฎหมายต่อไปนี้ให้เป็นภาษาชาวบ้านที่เข้าใจง่ายที่สุด
            - บอกว่าสิทธิของเขาคืออะไร
            - ต้องทำอะไรบ้าง
            - มีข้อควรระวังอะไร
            
            ข้อความกฎหมาย: {law_text}
            """
            response = model.generate_content(simplifier_prompt)
            st.success("✅ คำสรุปจาก AI:")
            st.markdown(response.text)
