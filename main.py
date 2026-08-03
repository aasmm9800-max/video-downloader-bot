import os
import telebot
import yt_dlp

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
    
    # التحقق من أن المرسل هو رابط فعلي
    if "http" not in url:
        bot.reply_to(message, "الرجاء إرسال رابط فيديو صحيح أولاً.")
        return

    # إرسال رسالة انتظار للمستخدم
    msg = bot.reply_to(message, "جاري معالجة الرابط وتحميل الفيديو... انتظر لحظة ⏳")

    # إعدادات أداة التحميل لتنزيل أفضل جودة بصيغة mp4 وبحجم مناسب للتليجرام
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # استخراج البيانات وتحميل الملف
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # إرسال الفيديو للمستخدم داخل المحادثة
            with open(filename, 'rb') as video:
                bot.send_video(message.chat.id, video, reply_to_message_id=message.id)
            
            # مسح الملف من السيرفر فوراً بعد إرساله للحفاظ على المساحة
            if os.path.exists(filename):
                os.remove(filename)
                
            # حذف رسالة الانتظار القديمة
            bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        # في حال حدوث أي خطأ في الرابط أو النظام
        bot.edit_message_text(f"عذراً، تعذر تحميل الفيديو. تأكد من أن الحساب العام أو أن الرابط مدعوم.\n\nوصف الخطأ التقني: {str(e)[:100]}", message.chat.id, msg.message_id)

# تشغيل البوت بشكل مستمر
print("البوت يعمل الآن بنجاح...")
bot.infinity_polling()
