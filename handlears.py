from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, ContextTypes
import keyboards
import db



T_ID, T_FILE, T_ANS = range(3)
# User TEST Check
T_SEND, T_CHECK = range(2)
# Admin TEST Result
RES_ID = range(1)

async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    if db.is_admin(user.id):
        await update.message.reply_text(
            text=f"""Assalomu aleykum {user.full_name}. Siz ushbu botda admin huqudiga egasiz. Botga test qo'shish /create va natija olish /results""",
        )
    else:
        if db.user_search(chat_id=user.id) is None:
            
            db.register(
                chat_id=user.id,
                fullname=user.full_name,
                username=user.username
            )
        await update.message.reply_text("Test bajarish uchun /tests commandasini yuboring!")


async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text('Amalyot bajarilmadi!')
    return ConversationHandler.END

# User test check
async def tests_command(update: Update, context: CallbackContext):
    await update.message.reply_text("TEST KODI ni yuboring:")
    return T_SEND

async def send_user_test(update: Update, context: CallbackContext):
    test_id = update.message.text.strip()
    user = update.message.from_user
    if not db.is_admin(user.id):
        test_data = db.get_testid(test_id=test_id)
        if test_data != []:
            await update.message.reply_document(test_data[0]['file_path'], caption=f"""Testning javoblarini yuboring.
Maskur ✍️ Test kodi: {test_id}.\nNamuna: {test_id}*a:b:a:d.....Samarkand:1991-yil.(Ortiqcha belgilar va bosh joy bo'lmasligi kerak)""")
            return T_CHECK
        else:
            await update.message.reply_text(f"❌ Ushbu test kodi mavjud emas, tekshirib ko'ring.")
            return T_SEND

async def user_test_check(update: Update, context: CallbackContext):
    user_answers_data = update.message.text.strip()
    user_id = update.message.from_user.id

    result = db.check_user_test(test_answer=user_answers_data, chat_id=str(user_id))
    user_data = db.user_search(chat_id=str(user_id))

    if isinstance(result, str):
        if result == "error_testid":
            await update.message.reply_text(
                "❌ Xatolik!\nTestni yuborishda xato qildingiz.\n"
                "Format: <test_kodi>*<javoblar> bo'lishi shart.\nMasalan: 12*a:b:c:d"
            )
            return T_CHECK
        
        elif result == "test_not_found":
            await update.message.reply_text("❌ Test topilmadi. Test kodini tekshiring.")
            return T_CHECK

        elif result == "error_format_true":
            await update.message.reply_text("❌ Bazadagi test formatida xatolik mavjud. Administratorga murojaat qiling.")
            return T_CHECK

        elif result == "answer_length_error":
            await update.message.reply_text(
                "❌ Javoblar soni savollar soniga mos kelmadi!\n"
                "Siz javoblarni to‘liq yoki to‘g‘ri tartibda yubormadingiz."
            )
            return T_CHECK
        else:
            await update.message.reply_text("❌ Noma'lum xatolik yuz berdi.")
            return T_CHECK

    if result is None:
        await update.message.reply_text(
            "❌ Test javoblarini noto‘g‘ri formatda yubordingiz.\n"
            "Namunadagidek yuboring: <test_kodi>*a:b:c:d"
        )
        return T_CHECK

    correct = result["correct"]
    wrong = result["wrong"]
    score = result["score"]
    total_questions = result["total_questions"]

    await update.message.reply_text(f"""
👤 Ismingiz: {user_data['fullname']}
📘 Jami savollar soni: {total_questions}

✅ To‘g‘ri javoblar: {correct}
❌ Xato javoblar: {wrong}

⭐ Umumiy ball: {score}
""")
    return ConversationHandler.END

# Admin 
async def admin_creat_test(update: Update, context: CallbackContext):
    user = update.message.from_user
    if db.is_admin(user.id):
        await update.message.reply_text("TEST KODI ni yarating:")
        return T_ID
    else:
        await update.message.reply_text("❌ Siz admin emassiz!")
        return ConversationHandler.END

async def ask_testID(update: Update, context: CallbackContext):
    test_ID = update.message.text
    check_testID = db.get_testid(str(test_ID))
    if check_testID == []:
        context.user_data['testID'] = test_ID
        await update.message.reply_text("Iltimos, PDF formatida test faylini yuboring:")
        return T_FILE
    else:
        await update.message.reply_text("Siz yuborgan TEST KODI mavjud, iltimos yangi yarating:")
        return T_ID    

async def ask_testFILE(update: Update, context: CallbackContext):
    context.user_data['testFILE'] = update.message.document.file_id
    await update.message.reply_text("TEST Javoblarini yuboring txt formatda.\nNamuna: 1:a:10(1-savol raqam, a-javob, 10-ball)")
    return T_ANS

async def ask_testANSWER(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if document.mime_type == "text/plain":

        file = await document.get_file()
        file_bytes = await file.download_as_bytearray()
        context.user_data['testANSWER'] = file_bytes.decode("utf-8")

        user_id = update.message.from_user.id
        test_id = context.user_data['testID']
        file_path = context.user_data['testFILE']
        test_answer = context.user_data['testANSWER']
        if db.is_admin(user_id):
            db.save_pdf(
                test_id=test_id,
                file_path=file_path,
                test_answer=test_answer
            )
            await update.message.reply_document(file_path, caption=f"✅ Muvaffaqiyatli saqlandi.\nTEST KODI: {test_id}")
        else:
            await update.message.reply_text("❌ Siz admin emassiz!")

        return ConversationHandler.END
    else:
        await update.message.reply_text("Iltimos .txt fayl yuboring")
        return T_ANS


# Admin get  results
async def admin_get_results(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if db.is_admin(user_id):
        await update.message.reply_text("TEST KODI ni yuboring:")
        return RES_ID
    else:
        await update.message.reply_text("❌ Siz admin emassiz!")
        return ConversationHandler.END

async def get_results_user(update: Update, context: CallbackContext):
    test_ID = update.message.text
    user = update.message.from_user
    if db.is_admin(user.id):
        users_data = db.admin_get_result(str(test_ID))
        result_data = """"""
        if users_data!=[]:
            for idx, user_res in enumerate(users_data):
                if idx==0:
                    result_data += f"🥇 FIO: {user_res['fullname']}, Username: {user_res['username']}, To'g'ri: {user_res['true_total']}, Ball: {user_res['score']}\n"
                elif idx==1:
                    result_data += f"🥈 FIO: {user_res['fullname']}, Username: {user_res['username']}, To'g'ri: {user_res['true_total']}, Ball: {user_res['score']}\n"
                elif idx == 2:
                    result_data += f"🥉 FIO: {user_res['fullname']}, Username: {user_res['username']}, To'g'ri: {user_res['true_total']}, Ball: {user_res['score']}\n"
                else:
                    result_data += f"{idx+1}. FIO: {user_res['fullname']}, Username: {user_res['username']}, To'g'ri: {user_res['true_total']}, Ball: {user_res['score']}\n"
        else:
            result_data = "Siz yuborgan test kodida natijalar yo'q."
        await update.message.reply_text(result_data)
    else:
        await update.message.reply_text("❌ Siz admin emassiz!")
    return ConversationHandler.END