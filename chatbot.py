import json
import os
from dotenv import load_dotenv
import gradio as gr
from groq import Groq

# تحميل المتغيرات من pass.env
load_dotenv("pass.env", override=True)

# 1. بيانات الجدول والأرقام
DATA_JSON = """
{
  "seniors_3_schedule": [
    {"day": "يوم السبت", "location": "فاروس 2 الهانوفيل", "time": "09:00 AM"},
    {"day": "يوم الأحد", "location": "انفينتي الورديان", "time": "09:00 AM"},
    {"day": "يوم الثلاثاء", "location": "عبد المقصود الدخيلة", "time": "09:00 AM"},
    {"day": "يوم الثلاثاء", "location": "سنتر لطفي الورديان", "time": "05:30 PM"},
    {"day": "يوم الأربعاء", "location": "فاروس 1 الهانوفيل", "time": "05:30 PM"},
    {"day": "يوم الخميس", "location": "عبد المقصود البيطاش", "time": "09:00 AM"},
    {"day": "يوم الجمعة", "location": "عبد الغفار الورديان", "time": "08:00 AM"}
  ],
  "seniors_2_schedule": [
    {"day": "يوم السبت", "location": "أكاديمية فاروس 2", "time": "01:00 PM"},
    {"day": "يوم الأحد", "location": "سنتر انفينتي", "time": "01:00 PM"},
    {"day": "يوم الاثنين", "location": "سنتر لطفي", "time": "09:00 AM"},
    {"day": "يوم الثلاثاء", "location": "عبد المقصود الدخيلة", "time": "01:00 PM"},
    {"day": "يوم الخميس", "location": "عبد المقصود البيطاش", "time": "02:00 PM"},
    {"day": "يوم الجمعة", "location": "سنتر عبد الغفار", "time": "02:00 PM"}
  ],
  "contacts": [
    {"category": "استفسارات الأونلاين", "contact_person": "مس هنا", "phone": "01277568941"},
    {"category": "استفسارات الكتب", "contact_person": "مس روان", "phone": "+20 122 308 4534"},
    {"category": "استفسارات أخرى", "contact_person": "مس أميرة", "phone": "01271381459"}
  ]
}
"""

schedule_data = json.loads(DATA_JSON)

api_key = os.getenv("api") or os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")
client = Groq(api_key=api_key)

SYSTEM_PROMPT = f"""
أنت مساعد آلي ذكي لمراكز وحصص اللغة الإنجليزية.
مهمتك الرد على استفسارات الطلاب وأولياء الأمور بدقة بناءً على البيانات التالية فقط:

{json.dumps(schedule_data, ensure_ascii=False, indent=2)}

قواعد الرد:
1. اجعل الرد بأسلوب لطيف ومنظم مع استخدام الإيموجي المناسب.
2. إذا سأل الطالب عن مواعيد 3 ثانوي استخدم بيانات `seniors_3_schedule`.
3. إذا سأل عن مواعيد 2 ثانوي استخدم بيانات `seniors_2_schedule`.
4. لو السؤال عن التواصل أو الأونلاين أو الكتب، اعطه اسم الشخص المسؤول ورقم الهاتف الموضح في `contacts`.
5. لو المعلومة غير موجودة في البيانات، أبلغه بلطف أنك لا تملك هذه المعلومة واطلب منه التواصل مع "مس أميرة" على رقمها الموضح للاستفسار.
"""

# #4. دالة الشات المعالجة للنصوص
def chat_with_bot(user_message, history):
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        for item in history:
            if isinstance(item, dict):
                content = item.get("content", "")
                if isinstance(content, list):
                    content = " ".join([str(c.get("text", "")) if isinstance(c, dict) else str(c) for c in content])
                messages.append({
                    "role": item.get("role", "user"),
                    "content": str(content)
                })
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                messages.append({"role": "user", "content": str(item[0])})
                messages.append({"role": "assistant", "content": str(item[1])})
            
        messages.append({"role": "user", "content": str(user_message)})

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            temperature=0.3
        )
        
        res_content = response.choices[0].message.content
        if isinstance(res_content, list):
            res_content = " ".join([str(c.get("text", "")) if isinstance(c, dict) else str(c) for c in res_content])
            
        return str(res_content)
    except Exception as e:
        print(f"Error details: {e}")
        return f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {str(e)}"

demo = gr.ChatInterface(
    fn=chat_with_bot,
    title="🎓 مساعد مواعيد واستفسارات الحصص",
    description="اسأل عن مواعيد 2 ثانوي، 3 ثانوي، أماكن السناتر، أو أرقام التواصل!",
    examples=[
        "ايه مواعيد 3 ثانوي في الورديان؟",
        "عايز رقم مس هنا للأونلاين",
        "مواعيد 2 ثانوي يوم الثلاثاء فين؟"
    ]
)

if __name__ == "__main__":
    demo.launch(share=True)