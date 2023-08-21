import telebot as tb

from django.http import HttpResponse

from .bot import Bot

'''
def webhook_handler(request):
    if request.method == 'POST':
        json_str = request.body.decode('UTF-8')
        update = tb.types.Update.de_json(json_str)
        Bot.instance.process_new_updates([update])
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=405)
'''
