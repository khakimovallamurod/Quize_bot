from telegram.ext import Updater, CommandHandler, MessageHandler,CallbackQueryHandler, Application, filters, ConversationHandler
from config import get_token
import handlears


def main():
    TOKEN = get_token()

    dp = Application.builder().token(TOKEN).build()
    
    dp.add_handler(CommandHandler('start', handlears.start))

    #Admin
    admin_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('create', handlears.admin_creat_test)],
        states={
            handlears.T_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlears.ask_testID)],
            handlears.T_FILE: [MessageHandler(filters.Document.ALL & ~filters.COMMAND, handlears.ask_testFILE)], 
            handlears.T_ANS: [MessageHandler(filters.Document.TXT & ~filters.COMMAND, handlears.ask_testANSWER)],
        },
        fallbacks=[CommandHandler('cancel', handlears.cancel)]
    )
    #User
    user_test_handler = ConversationHandler(
        entry_points=[CommandHandler('tests', handlears.tests_command)],
        states={
            handlears.T_SEND: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlears.send_user_test)],
            handlears.T_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlears.user_test_check)],
        },
        fallbacks=[CommandHandler('cancel', handlears.cancel)]
    )
    # Admin get result
    admin_get_results = ConversationHandler(
        entry_points=[CommandHandler('results', handlears.admin_get_results)],
        states={
            handlears.RES_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlears.get_results_user)],
        },
        fallbacks=[CommandHandler('cancel', handlears.cancel)]
    )
    dp.add_handler(admin_conv_handler)
    dp.add_handler(user_test_handler)
    dp.add_handler(admin_get_results)
    dp.run_polling()


if __name__ == '__main__':
    main()  
    