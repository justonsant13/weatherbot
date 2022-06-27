import telebot
import json
import requests as req
from geopy import geocoders
import datetime as dt

#main variables
TOKEN = "5505212365:AAFY2yZLiFyHnDxNvqOOupmaFGM5VxTBevg"
bot = telebot.TeleBot(TOKEN)
token_yandex = "0de4a2b2-b300-4b85-8ef9-aa78e4769bb2"
location = []
city = ''
n = 0

def geo_pos(city: str):
    geolocator = geocoders.Nominatim(user_agent="telebot")
    latitude = str(geolocator.geocode(city).latitude)
    longitude = str(geolocator.geocode(city).longitude)
    return latitude, longitude


def yandex_weather_fact(latitude, longitude, token_yandex: str):
    url_yandex = f'https://api.weather.yandex.ru/v2/forecast/?lat={latitude}&lon={longitude}&[lang=ru_RU]'
    yandex_req = req.get(url_yandex, headers={'X-Yandex-API-Key': token_yandex}, verify=False)
    conditions = {'clear': 'ясно', 'partly-cloudy': 'малооблачно', 'cloudy': 'облачно с прояснениями',
                  'overcast': 'пасмурно', 'drizzle': 'морось', 'light-rain': 'небольшой дождь',
                  'rain': 'дождь', 'moderate-rain': 'умеренно сильный', 'heavy-rain': 'сильный дождь',
                  'continuous-heavy-rain': 'длительный сильный дождь', 'showers': 'ливень',
                  'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег', 'snow': 'снег',
                  'snow-showers': 'снегопад', 'hail': 'град', 'thunderstorm': 'гроза',
                  'thunderstorm-with-rain': 'дождь с грозой', 'thunderstorm-with-hail': 'гроза с градом'
                  }
    wind_dir = {'nw': 'северо-западное', 'n': 'северное', 'ne': 'северо-восточное', 'e': 'восточное',
                'se': 'юго-восточное', 's': 'южное', 'sw': 'юго-западное', 'w': 'западное', 'с': 'штиль'}  
           
    yandex_json = json.loads(yandex_req.text)
    pogoda = dict()
    yandex_json['fact']['condition'] = conditions[yandex_json['fact']['condition']]
    yandex_json['fact']['wind_dir'] = wind_dir[yandex_json['fact']['wind_dir']]   
    pogoda['humidity']= yandex_json['fact']['humidity']
    pogoda['feels_like']= yandex_json['fact']['feels_like']
    pogoda['temp']= yandex_json['fact']['temp']
    pogoda['condition']=yandex_json['fact']['condition']
    pogoda['wind_dir']=yandex_json['fact']['wind_dir']
    pogoda['pressure_mm']=yandex_json['fact']['pressure_mm']
    pogoda['wind_speed']=yandex_json['fact']['wind_speed']
    
    return pogoda


def yandex_weather_forecast(latitude, longitude, token_yandex: str,n: int):
    url_yandex = f'https://api.weather.yandex.ru/v2/forecast/?lat={latitude}&lon={longitude}&[lang=ru_RU]'
    yandex_req = req.get(url_yandex, headers={'X-Yandex-API-Key': token_yandex}, verify=False)
    conditions = {'clear': 'ясно', 'partly-cloudy': 'малооблачно', 'cloudy': 'облачно с прояснениями',
                  'overcast': 'пасмурно', 'drizzle': 'морось', 'light-rain': 'небольшой дождь',
                  'rain': 'дождь', 'moderate-rain': 'умеренно сильный', 'heavy-rain': 'сильный дождь',
                  'continuous-heavy-rain': 'длительный сильный дождь', 'showers': 'ливень',
                  'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег', 'snow': 'снег',
                  'snow-showers': 'снегопад', 'hail': 'град', 'thunderstorm': 'гроза',
                  'thunderstorm-with-rain': 'дождь с грозой', 'thunderstorm-with-hail': 'гроза с градом'
                  }
    wind_dir = {'nw': 'северо-западное', 'n': 'северное', 'ne': 'северо-восточное', 'e': 'восточное',
                'se': 'юго-восточное', 's': 'южное', 'sw': 'юго-западное', 'w': 'западное', 'с': 'штиль'}  
          
    yandex_json = json.loads(yandex_req.text)
    pogoda = dict()
    yandex_json['forecasts'][n]['parts']['day']['condition'] = conditions[yandex_json['fact']['condition']]
    yandex_json['forecasts'][n]['parts']['day']['wind_dir'] = wind_dir[yandex_json['fact']['wind_dir']]
    
    pogoda['humidity'] = yandex_json['forecasts'][n]['parts']['day']['humidity']
    pogoda['feels_like']= yandex_json['forecasts'][n]['parts']['day']['feels_like']
    pogoda['temp']= yandex_json['forecasts'][n]['parts']['day']['temp_avg']
    pogoda['temp_min']= yandex_json['forecasts'][n]['parts']['day']['temp_min']
    pogoda['temp_max']= yandex_json['forecasts'][n]['parts']['day']['temp_max']
    pogoda['condition']=yandex_json['forecasts'][n]['parts']['day']['condition']
    pogoda['wind_dir']=yandex_json['forecasts'][n]['parts']['day']['wind_dir']
    pogoda['pressure_mm']=yandex_json['forecasts'][n]['parts']['day']['pressure_mm']
    pogoda['wind_speed']=yandex_json['forecasts'][n]['parts']['day']['wind_speed']
    
    return pogoda


@bot.message_handler(commands=['Погода на завтра'])
def weather_now_handler(message):
    if len(location) == 0:
        msg = bot.send_message(message.chat.id, 'Мне нужно определить вашу локацию. Собщите мне ваш город')
        bot.register_next_step_handler(msg, geoAsk)
    else:
        bot.send_message(message.chat.id, 'Ваш город: ' + city)
        w=yandex_weather_fact(location[0], location[1], token_yandex)
        newline = '\n'
        bot.send_message(message.chat.id,  f'Докладываю текущую погоду в городе {city}: {newline}'
                                                f'темпертура  {w["temp"]}С, {newline}'
                                                f'ощущается как  {w["feels_like"]}С, {newline}'
                                                f'облачность и осадки - {w["condition"]}, {newline}'
                                                f'направление ветра {w["wind_dir"]} - {w["wind_speed"]} м/с, {newline}'
                                                f'давление - {w["pressure_mm"]} мм рт.ст.,{newline} '
                                                f'влажность - {w["humidity"]} %.{newline}'
                                                )                       
    
@bot.message_handler (commands= ['Погода на сегодня'])
def weather_0_handler(message):
    global n
    n = 0
    msg = bot.send_message(message.chat.id, 'Посмотрим прогноз на Yandex Погода')
    bot.register_next_step_handler(msg, weather_ask)    
    

@bot.message_handler(commands=['Погода на завтра'])
def weather_1_handler(message):
    global n
    n = 1
    msg = bot.send_message(message.chat.id, 'Посмотрим прогноз на Yandex Погода')
    bot.register_next_step_handler(msg, weather_ask)    

@bot.message_handler(commands=['Погода на послезавтра'])
def weather_2_handler(message):
    global n
    n = 2
    msg = bot.send_message(message.chat.id, 'Посмотрим прогноз на Yandex Погода')
    bot.register_next_step_handler(msg,weather_ask)

@bot.message_handler(commands=['Погода на 3 день'])
def weather_3_handler(message):
    global n
    n = 3
    msg = bot.send_message(message.chat.id, 'Посмотрим прогноз на Yandex Погода')
    bot.register_next_step_handler(msg, weather_ask)

def weather_ask(message):    
    #дата прогноза
    d = dt.date.today()
    dp = d + dt.timedelta(n)
    m = {1:'января',2:'февраля',3:'марта',4:'апреля',5:'мая',6:'июня',7:'июля',8:'августа',9:'сентября',10:'октября',11:'ноября',12:'декабря'}
    sd = f'{dp.day} {m[dp.month]}'
    if len(city) == 0:
        bot.send_message(message.chat.id, 'Мне нужно определить вашу локацию. Собщите мне ваш город')
        bot.register_next_step_handler(message, geoAsk)
    else:
        #bot.send_message(message.chat.id, 'Ваш город: ' + city)
        w=yandex_weather_forecast(location[0], location[1], token_yandex,n)
        newline = '\n'
        if n ==0:
            s=f'на сегодня, {sd}'
        elif n==1:
            s=f'на завтра, {sd}'
        elif n==2:
            s=f'на послезавтра, {sd}'
        else:
            s=f'на {sd}'
        bot.send_message(message.chat.id,  f'Докладываю погоду {s} в городе {city}: {newline}'
                                           f'темпертура  {w["temp"]}С, {newline}'
                                           f'ощущается как  {w["feels_like"]}С, {newline}'
                                           f'облачность и осадки - {w["condition"]}, {newline}'
                                           f'направление ветра {w["wind_dir"]} - {w["wind_speed"]} м/с, {newline}'
                                           f'давление - {w["pressure_mm"]} мм рт.ст.,{newline} '
                                           f'влажность - {w["humidity"]} %.{newline}'
                                           ) 
    
@bot.message_handler(commands=['city'])
def city_handler(message):
    msg = bot.send_message(message.chat.id, 'Нужно определить вашу локацию. Собщите мне ваш город')
    bot.register_next_step_handler(msg, geoAsk)

def geoAsk(message):
    global city
    city = message.text
    global location 
    location = geo_pos(city)
    bot.send_message(message.chat.id, str(location))
    bot.send_message(message.chat.id, 'Теперь я знаю вашу локацию, можно спрашивать и о погоде')
    

@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text.lower()
    chat_id = message.chat.id
    if text == "привет":
        bot.send_message(chat_id, 'Привет, я погодный бот.')
    elif text == "как погода?" or text == "как погода" or text =="покажи погоду":
        bot.send_message(chat_id, 'Задайте в меню и задайте свой город командой city, а потом выберите команду weather')
    else:
        bot.send_message(chat_id, 'Простите, я вас не понял :(')

@bot.message_handler(content_types=['photo'])
def photp_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Милая картинка, но я больше по погоде')

bot.polling()