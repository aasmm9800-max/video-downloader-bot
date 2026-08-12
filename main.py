import os
import telebot
import yt_dlp
import requests
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
    port = int(os.environ.get("PORT", 8080)) 
    server = HTTPServer(("0.0.0.0", port), DummyServer)
    server.serve_forever()

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

    # معالجة خاصة وصارمة لروابط يوتيوب لتفادي حظر سيرفر Render
    if "youtube.com" in url or "youtu.be" in url:
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            payload = {
                "url": url,
                "videoQuality": "480",  # جودة متوازنة لضمان عدم تخطي حد الـ 50 ميجا الخاص بتليجرام
                "downloadMode": "video"
            }
            
            # استدعاء منصة العبور الخارجي لتخطي الحظر
            api_url = "https://api.cobalt.tools/api/json"
            response = requests.post(api_url, json=payload, headers=headers, timeout=15)
            response_data = response.json()

            if "url" in response_data:
                video_download_url = response_data["url"]
                filename = "youtube_video.mp4"
                
                # سحب الفيديو إلى السيرفر مؤقتاً لإرساله كملف أصيل
                video_file = requests.get(video_download_url, stream=True)
                with open(filename, 'wb') as f:
                    for chunk in video_file.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
                
                with open(filename, 'rb') as video:
                    bot.send_video(message.chat.id, video, reply_to_message_id=message.id)
                
                if os.path.exists(filename):
                    os.remove(filename)
                    
                bot.delete_message(message.chat.id, msg.message_id)
                return  # إنهاء العملية بنجاح لليوتيوب والتحول للانتظار التالي
        except Exception as e:
            print(f"فشلت الخطة أ لليوتيوب، سيتم الانتقال الاحتياطي: {e}")

    # الخطة العامة لبقية المنصات (تيك توك، انستقرام، إلخ)
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
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
