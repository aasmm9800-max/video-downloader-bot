import os
import telebot
import yt_dlp
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- قسم السيرفر الوهمي لإرضاء منصة Render ---
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("البوت يعمل بنجاح!".encode('utf-8'))

def run_dummy_server():
    # Render يرسل رقم المنفذ تلقائياً في المتغير PORT
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    print(f"السيرفر الوهمي يعمل الآن على المنفذ: {port}")
    server.serve_forever()

# تشغيل السيرفر الوهمي في الخلفية (Thread) حتى لا يعطل البوت
Thread(target=run_dummy_server, daemon=True).start()
# --------------------------------------------

# ربط البوت بالتوكن الخاص بك
BOT_TOKEN = "8867252042:AAGOS4yOWBWRzdLelPes1wNv2-3f5zRPpNo"
bot = telebot.TeleBot(BOT_TOKEN)

# رسالة الترحيب عند بدء تشغيل البوت
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! 🚀\nأرسل لي رابط أي فيديو من (تيك توك، إنستغرام، يوتيوب، فيسبوك، أو سناب شات) وسأقوم بتحميله وإرساله لك فوراً.")

# استقبال الروابط ومعالجتها
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    
    if "http" not in url:
        bot.reply_to(message, "الرجاء إرسال رابط فيديو صحيح أولاً.")
        return

    msg = bot.reply_to(message, "جاري معالجة الرابط وتحميل الفيديو... انتظر لحظة ⏳")

    # إعدادات أداة التحميل لتنزيل أفضل جودة بصيغة mp4 وبحجم مناسب للتليجرام
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['tv', 'web_embedded']  # التنكر كشاشة ذكية وفيديو مدمج لتجاوز الحظر الصارم
            }
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            with open(filename, 'rb') as video:
                bot.send_video(message.chat.id, video, reply_to_message_id=message.id)
            
            if os.path.exists(filename):
                os.remove(filename)
                
            bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"عذراً، تعذر تحميل الفيديو. تأكد من أن الحساب العام أو أن الرابط مدعوم.\n\nوصف الخطأ التقني: {str(e)[:100]}", message.chat.id, msg.message_id)

# تشغيل البوت بشكل مستمر
print("البوت يعمل الآن بنجاح...")
bot.infinity_polling()
