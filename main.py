import telebot
from telebot import types
import re
import sqlite3
import time

token = '2024824075:AAHdI1SLHgO_eJUCxO0kAnEWa4H6XGu2R9I'  # Токен для подключения бота
bot = telebot.TeleBot(token)  # создание сессии с ботом

db=sqlite3.connect('server.db',check_same_thread=False)
sql = db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS users (
    id TEXT,
    student TEXT,
    praise TEXT,
    time TEXT
)""")
db.commit()


@bot.message_handler(commands=['start'])  # отправка сообщений на команду начало
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)  # создать кнопочки и указать размер
    markup.row('Добавить ученика')
    markup.row('Добавить часы')
    markup.row('Удалить ученика')
    markup.row('Заработок')
    bot.send_message(message.chat.id, "Привет,чем могу помочь?", reply_markup=markup)

@bot.message_handler(commands=['student']) #need remake
def send_student(message):
    id=message.chat.id
    ans=""
    sql_print = """select student,praise,time from users where id = ?"""
    sql.execute(sql_print, (id,))
    info = sql.fetchall()
    for i in range(0, len(info)):
        string=info[i]
        ans += str(str(string[0]) +' цена '+ str(string[1])+ ' кол-во занятий '+ str(string[2])+'\n')
    bot.send_message(id,ans)

@bot.message_handler(regexp='Добавить ученика')# получение данных об учениках
def add_student(message):
    msg1 = bot.send_message(message.chat.id,
                            "Введите имя,фамилию ученика и стоимость одного занятия")
    bot.register_next_step_handler(msg1, add_st)

def add_st(message):
    id=message.chat.id
    name_cost=message.text #имя студента+цена
    name=" ".join(re.findall("[а-яА-Я]+",name_cost)) #find name
    cost=" ".join(re.findall("\d+$",name_cost))  #find cost
    sql_find = """select * from users where id = ? and student = ?"""
    info = sql.execute(sql_find, (id, name,))
    #print(info.fetchone())
    if info.fetchone() is None:
        sql.execute("INSERT INTO users VALUES (?,?,?,?)", (str(id), name, max(cost,"0"), '0'))
    else:
        bot.send_message(id,"Такой студет уже есть. Изменена стоимость занятия")
        sql_update = """Update users set praise = ? where id = ? and student = ?"""
        base = (max(cost,"0"), id, name)
        sql.execute(sql_update, base)
    db.commit()  #


@bot.message_handler(regexp='Добавить часы')# отправка сообщений на команду начало
def add_student(message):
    msg2 = bot.send_message(message.chat.id,
                            "Введите имя,фамилию ученика и сколько занятий было")
    bot.register_next_step_handler(msg2, col_h)

def col_h(message):
    id=message.chat.id
    name_time = message.text
    name=" ".join(re.findall("[а-яА-Я]+",name_time))
    time=" ".join(re.findall("\d+$",name_time))
    sql_find = """select * from users where id = ? and student = ?"""
    info = sql.execute(sql_find, (id,name,))
    sql_update="""Update users set time = ? where id = ? and student = ?"""
    base=(time,id,name)
    sql.execute(sql_update,base)
    db.commit()


@bot.message_handler(regexp='Удалить ученика')
def del_student(message):
    msg3 = bot.send_message(message.chat.id,
                                "Введите имя,фамилию ученика которого нужно удалить")
    bot.register_next_step_handler(msg3,del_st)

def del_st(message):
    id = message.chat.id
    name = message.text
    sql_find = """select * from users where id = ? and student = ?"""
    sql.execute(sql_find, (id, name,))
    sql_delete = """DELETE from users where id = ? and student = ?"""
    sql.execute(sql_delete, (id, name,))
    db.commit()

@bot.message_handler(regexp='Заработок')
def price(massage):
    id=massage.chat.id
    sql_money = """select praise,time from users where id = ?"""
    sql.execute(sql_money, (id,))
    money=0
    info=sql.fetchall()
    result = time.localtime()
    if result.tm_mday == 1:
        send_student(massage)
        sql_update_month = """Update users set time = ?"""
        base = ('0')
        sql.execute(sql_update_month, base)
    for i in range(0,len(info)):
        col=info[i]
        money+=int(col[0])*int(col[1])
    bot.send_message(id,"Заработок: в месяце "+ str(time.localtime().tm_mon)+" заработок "+ str(money))




bot.polling(none_stop=True, interval=0)