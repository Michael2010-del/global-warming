
import telebot
import random
from telebot.types import BotCommand,InlineKeyboardMarkup, InlineKeyboardButton
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
# Инициализация бота
bot = telebot.TeleBot("Your Token")

#Настройка команд меню
bot.set_my_commands([
    BotCommand("start", "Запуск бота"),
    BotCommand("fact", "Отправляет рандомный экологический факт"),
    BotCommand("plastic", "Рассказывает про пластик"),
    BotCommand("battery", "Рассказывает про батарейки"),
    BotCommand("paper", "Рассказывает про бумагу"),
    BotCommand("metal", "Рассказывает про метал"),
    BotCommand("electronics", "Рассказывает про электронику"),
    BotCommand("glass", "Рассказывает про стекло"),
    BotCommand("organic", "Рассказывает про органику"),
    BotCommand("map", "Карта с местами куда ты сможешь сдать различный мусор"),
    BotCommand("challenge", "Ежедневные челленджи"),
    BotCommand("footprint", "Калькулятор углеродного следа"),
    BotCommand("stats", "Моя статистика и очки")
    
    
])



# Создание базы данных Flask-SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecobot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модели базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    score = db.Column(db.Integer, default=0)
    challenges_completed = db.Column(db.Integer, default=0)
    carbon_footprint = db.Column(db.Float, default=0)
    


# Создание таблиц
with app.app_context():
    db.create_all()

# Функции для работы с базой данных
def get_or_create_user(user_id, username, first_name, last_name):
    with app.app_context():
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            user = User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            db.session.add(user)
            db.session.commit()
        return user
def update_user_score(user_id, points):
    with app.app_context():
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            user.score += points
            user.challenges_completed += 1
            db.session.commit()

def update_carbon_footprint(user_id, footprint):
    with app.app_context():
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            user.carbon_footprint = footprint
            db.session.commit()
def get_user_stats(user_id):
    with app.app_context():
        user = User.query.filter_by(user_id=user_id).first()
        return user





# Данные для бота
ECO_TIPS = [
    "Замените пластиковые пакеты на многоразовые тканевые сумки.",
    "Используйте восковые салфетки вместо пищевой плёнки.",
    "Покупайте крупы и специи на развес в свою тару.",
    "Организуйте компостирование пищевых отходов (даже в квартире с помощью вермикомпостера).",
    "Замените лампочки на светодиодные - экономия до 90% энергии.",
    "Установите аэратор на кран - сократите расход воды на 50%.",
    "Выбирайте технику с классом энергоэффективности А+++.",
    "Откажитесь от одноразовых стаканчиков для кофе - используйте термокружку.",
    "Регулярно размораживайте холодильник - наледь увеличивает энергопотребление.",
    "Покупайте бывшую в употреблении технику и мебель - это тренд circular economy.",
    "Сдавайте старые гаджеты на переработку - в них содержатся редкоземельные металлы.",
    "Замените губки для мытья посуды на джутовые или люфовые.",
    "Используйте менструальную чашу вместо тампонов/прокладок - экономия до 150 кг отходов за жизнь.",
    "Печатайте на обеих сторонах бумаги - офисная бумага составляет 70% офисного мусора.",
    "Выбирайте цифровые билеты вместо бумажных.",
    "Организуйте каршеринг с коллегами - 1 автомобиль вместо 4-5.",
    "Установите программируемый термостат - экономия до 15% на отоплении.",
    "Покупайте вино в коробках - углеродный след на 80% меньше, чем у стеклянных бутылок.",
    "Замените одноразовые бритвы на безопасную бритву со сменными лезвиями.",
    "Используйте поисковик Ecosia - они сажают деревья за ваши поисковые запросы.",
    "Отдавайте предпочтение растительным альтернативам мяса - на производство говядины тратится в 20 раз больше ресурсов.",
    "Собирайте дождевую воду для полива растений.",
    "Выбирайте одежду из органического хлопка - обычный хлопок использует 25% мировых пестицидов.",
    "Откажитесь от чеков (они содержат BPA) - просите электронные.",
    "Участвуйте в буккроссинге - давайте книгам вторую жизнь.",
    "Замените воздушные шары на мыльные пузыри или бумажные флажки на праздниках.",
    "Используйте многоразовые контейнеры для еды вместо одноразовых.",
    "Покупайте местные сезонные продукты - сокращайте транспортный след.",
    "Выбирайте рыбу с сертификатом MSC - сохраняйте океаны.",
    "Установите bidet-насадку на унитаз - сократите использование туалетной бумаги.",
    "Организуйте zero waste свадьбу - цифровые приглашения, аренда платьев, местное меню.",
    "Сдавайте старые покрышки на переработку - они разлагаются 100+ лет.",
    "Используйте солнцезащитные кремы без оксибензона - он разрушает кораллы.",
    "Покупайте меньше, но более качественные вещи - fast fashion второй загрязнитель после нефти.",
    "Замените антибактериальное мыло на обычное - триклозан вредит водным экосистемам.",
    "Создайте зеленый офис - датчики движения, сбор батареек, виртуальные сервера.",
    "Выбирайте бамбуковые зубные щетки вместо пластиковых.",
    "Участвуйте в urban farming - выращивайте зелень даже на подоконнике.",
    "Откажитесь от глиттера - это микропластик, который попадает в океан.",
    "Используйте сервисы по аренде инструментов вместо покупки.",
    "Покупайте косметику без микропластика (полиэтилен/пропилен в составе).",
    "Выбирайте электронные книги вместо бумажных (окупается после 30-40 прочитанных).",
    "Сдавайте старую одежду в H&M на переработку - даже если не их бренд.",
    "Замените коктейльные трубочки на стеклянные/металлические.",
    "Установите умную систему полива сада с датчиками влажности.",
    "Покупайте refurbished-технику - как новая, но дешевле и экологичнее.",
    "Используйте экологичные средства для уборки (уксус, сода, лимон).",
    "Откажитесь от ламинирования бровей - в составе воска микропластик.",
    "Выбирайте кредитные карты из переработанного пластика.",
    "Участвуйте в tree-challenge - посадите дерево в свой день рождения."
]

ECO_FACTS = [
    "Переработка одной алюминиевой банки экономит энергию, достаточную для работы телевизора 3 часа.",
    "Ежегодно в океан попадает 8 млн тонн пластика - это как выбрасывать мусоровоз каждую минуту.",
    "Производство 1 кг говядины требует 15,000 литров воды - эквивалент 200 ванн.",
    "К 2050 году в океане будет больше пластика, чем рыбы (по весу).",
    "Один человек в среднем проглатывает 5 грамм пластика в неделю - это как кредитная карта.",
    "Fast fashion ответственна за 10% глобальных выбросов CO2 - больше чем авиация и морские перевозки вместе.",
    "За последние 50 лет популяция позвоночных сократилась на 68% (WWF Living Planet Report).",
    "Автомобиль, простаивающий в пробке 10 мин, выбрасывает 1 кг CO2.",
    "Один дуб за жизнь поглощает столько CO2, сколько выделяет автомобиль за 90,000 км пробега.",
    "В ЕС запрещены 1,300+ косметических ингредиентов, в США - только 11.",
    "Площадь арктического льда сокращается на 13% каждое десятилетие.",
    "Один гектар мангровых лесов поглощает в 4 раза больше CO2, чем тропический лес.",
    "Выброшенный в природу окурок разлагается 10-12 лет, отравляя 500 л воды.",
    "Коровы производят 150 млрд галлонов метана в день - мощный парниковый газ.",
    "Стекло требует 1 млн лет для полного разложения.",
    "Вдоль дорог в 6 раз больше микропластика, чем в океане.",
    "Один грузовой корабль выбрасывает столько же серы, сколько 50 млн автомобилей.",
    "92% населения мира дышит загрязненным воздухом (WHO).",
    "Пластиковые пакеты используются в среднем 12 минут, но разлагаются 500 лет.",
    "Вырубка лесов ответственна за 15% глобальных выбросов - больше чем весь транспорт.",
    "В Латинской Америке 40% биоразнообразия потеряно с 1970 года.",
    "Один смыв туалета в США использует больше воды, чем житель Африки за день.",
    "Для производства 1 джинсов требуется 7,000 литров воды - столько человек пьёт за 5 лет.",
    "Волокна от стирки синтетики составляют 35% микропластика в океане.",
    "К 2035 году 50% населения столкнется с нехваткой воды (UN).",
    "Одноразовые подгузники составляют 2% всех отходов на свалках.",
    "Вдыхание загрязненного воздуха сокращает жизнь на 2 года (University of Chicago).",
    "Один гектар солнечных панелей = 150 тонн сэкономленного CO2 в год.",
    "Великий Тихоокеанский мусорный остров в 3 раза больше Франции.",
    "Один смартфон требует 70 кг сырья для производства.",
    "Глобальное потепление сделает 600 млн человек климатическими беженцами к 2050 году.",
    "Один день без мяса экономит 3,000 литров воды.",
    "В Швеции только 1% мусора попадает на свалки - 99% перерабатывается.",
    "Каждую минуту вырубается 40 футбольных полей леса.",
    "Один киловатт-час от угля = 1 кг CO2, от ветра - только 12 грамм.",
    "Коралловые рифы могут исчезнуть к 2100 году из-за закисления океана.",
    "Один час работы газонокосилки = 100 км пробега автомобиля по выбросам.",
    "В Антарктиде тает 3 млрд тонн льда в день.",
    "Электронные отходы составляют 70% токсичных свалок.",
    "Один перелет Нью-Йорк-Лондон = 1 тонна CO2 на пассажира.",
    "Глобальное потепление снизит ВВП на 23% к 2100 году (Nature).",
    "В ЕС запретят одноразовый пластик с 2021 года (трубочки, столовые приборы и др.).",
    "Один житель США производит 2 кг мусора в день - в 10 раз больше чем в Индии.",
    "К 2030 году 50% электроэнергии в ЕС будет из возобновляемых источников.",
    "Один веганский год экономит 1.5 млн литров воды.",
    "В Китае построят город-лес Liuzhou - 40,000 деревьев поглотят 10,000 тонн CO2 в год.",
    "Один акр конопли поглощает столько же CO2, сколько 1 га леса.",
    "В Норвегии 60% новых авто - электромобили (рекорд мира).",
    "Переход на растительное питание сократит сельскохозяйственные земли на 75%."
]





#Пояснения 
waste_info = {
    "plastic": "♻️ **Пластик**\n\nПластик — один из самых опасных отходов из-за длительного разложения (до 500 лет). Его переработка позволяет сократить загрязнение окружающей среды.\n\n**Что можно сдавать:** бутылки, флаконы, контейнеры с маркировкой 1 (PET), 2 (HDPE), 5 (PP).\n**Куда сдавать:** контейнеры для раздельного сбора или пункты переработки.\n**Не сдаётся:** пакеты от чипсов, загрязнённая упаковка, пластик без маркировки.\n\n🔎 Маркировка обычно указывается на дне в виде треугольника с цифрой.",
    
    "paper": "📄 **Бумага и картон**\n\nБумага разлагается до 2 месяцев, но переработка сохраняет деревья и воду.\n\n**Что можно сдавать:** газеты, офисная бумага, коробки, упаковки.\n**Куда сдавать:** контейнеры для бумаги или эко-пункты.\n**Не сдаётся:** жирная, мокрая бумага, салфетки, тетрапак (если не указано обратное).",
    
    "glass": "🍾 **Стекло**\n\nСтекло можно перерабатывать бесконечно. Оно не теряет качества при повторной переработке.\n\n**Что можно сдавать:** бутылки, банки без крышек.\n**Куда сдавать:** стеклянные контейнеры.\n**Не сдаётся:** лампочки, зеркала, оконное стекло, посуда из жаропрочного стекла.",
    
    "metal": "🥫 **Металл**\n\nПереработка металла экономит 95% энергии по сравнению с добычей.\n\n**Что можно сдавать:** алюминиевые банки, консервные банки, крышки.\n**Куда сдавать:** контейнеры для металла или специальные пункты.\n**Не сдаётся:** фольга с остатками еды, баллончики под давлением.",
    
    "electronics": "🔌 **Электроника**\n\nЭлектроника содержит опасные элементы и драгоценные металлы.\n\n**Что можно сдавать:** телефоны, ноутбуки, провода, батарейки, зарядки.\n**Куда сдавать:** специальные пункты, магазины с утилизацией техники.\n**Не сдаётся:** лампы и аккумуляторы в обычные контейнеры!",
    
    "battery": "🔋 **Батарейки**\n\nБатарейки содержат тяжёлые металлы (ртуть, кадмий, свинец), которые **токсичны** и загрязняют почву и воду. **Одна батарейка может отравить до 400 литров воды.**\n\n**Что сдавать:**\n- Пальчиковые батарейки (AA, AAA)\n- Кроны, «таблетки», аккумуляторы от телефонов, ноутбуков\n\n**Как подготовить:**\n- Храните использованные батарейки в плотно закрытой банке или коробке\n- Не вскрывайте и не разбирайте их\n\n**Куда сдавать:**\n- Эко-боксы в магазинах (IKEA, М.Видео, Эльдорадо, Леруа Мерлен)\n- Пункты сбора опасных отходов при ЖКХ или в ТЦ\n- Специальные экобоксы от организаций типа «Собиратор»\n\n❗ **Никогда не выбрасывайте батарейки в обычный мусор — это крайне вредно для природы и здоровья!**",

    "organic": "🍎 **Органика**\n\nОрганические отходы — пищевые остатки, кожура, чай, кофе.\n\n**Куда сдавать:** в компост, либо использовать специальные контейнеры/компостеры.\n**Что нельзя:** мясо, рыбу, жир — они не подходят для домашнего компоста (привлекают вредителей).",
}
#Обработчики команд

#Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    bot.reply_to(message, "🌎Привет, Я ECOBOT! Я помогу сделать мир чище.В меню ты сможешь посмотреть что делает каждая команда.🌎")
#Команда /map
@bot.message_handler(commands=['map'])
def send_recycle_map(message):
    bot.send_message(
        message.chat.id,
        "🗺️ **Карта пунктов приёма отходов**\n\nОткройте карту, чтобы найти ближайшие места, где можно сдать батарейки, лампы, пластик и многое другое:\n\n🌐 [RecycleMap.ru](https://recyclemap.ru/)\n📱 Также доступно мобильное приложение: *Recycle Map*",
        parse_mode='Markdown'
    )

#Команды /plastic /paper /glass /metal /electronics /organic /battery
@bot.message_handler(commands=['plastic', 'paper', 'glass', 'metal', 'electronics', 'organic', "battery"])
def waste_info_handler(message):
    cmd = message.text[1:].lower()  
    info = waste_info.get(cmd, "Извините, информации по этому типу мусора пока нет.")
    bot.send_message(message.chat.id, info, parse_mode='Markdown')

#Команда /fact
@bot.message_handler(commands=['fact'])
def send_fact(message):
    fact = random.choice(ECO_FACTS)
    bot.send_message(message.chat.id, f"🌍 Эко-факт:\n\n{fact}")
#Команда /challenge
@bot.message_handler(commands=['challenge'])
def daily_challenge(message):
    user_id = message.from_user.id
    challenge = random.choice(ECO_TIPS)
    with app.app_context():
        update_user_score(user_id, 10)
    bot.send_message(
            message.chat.id,
            f"🌱 Твой эко-челлендж на сегодня:\n\n{challenge}\n\n+10 эко-очков! 🎯",
            parse_mode='Markdown')
    
#Команда /stats
@bot.message_handler(commands=['stats'])
def show_stats(message):
    user_id = message.from_user.id
    user = get_user_stats(user_id)
    
    if user:
        stats_message = f"""
📊 **Твоя экологическая статистика:**

🏆 Эко-очки: {user.score}
✅ Выполнено челленджей: {user.challenges_completed}
🌍 Углеродный след: {user.carbon_footprint} кг CO₂/месяц

💡 *Продолжай в том же духе! Каждое маленькое действие имеет значение.*
        """
        bot.send_message(message.chat.id, stats_message, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "❌ Не удалось найти вашу статистику. Попробуйте начать с команды /start")
                                                    

# Команда /footprint с InlineKeyboard
user_sessions = {}
@bot.message_handler(commands=['footprint'])
def carbon_footprint_start(message):
    user_id = message.from_user.id
    user_sessions[user_id] = {} 
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Каждый день", callback_data="diet_everyday"),
        InlineKeyboardButton("Несколько раз", callback_data="diet_few"),
        InlineKeyboardButton("Редко", callback_data="diet_rarely"),
        InlineKeyboardButton("Никогда", callback_data="diet_never")
    ]
    markup.add(*buttons)
    
    bot.send_message(message.chat.id, "🍖 Как часто ешь мясо?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('diet_'))
def handle_diet(call):
    user_id = call.from_user.id
    
    if call.data == 'diet_everyday':
        user_sessions[user_id]['diet'] = 10
    elif call.data == 'diet_few':
        user_sessions[user_id]['diet'] = 5
    elif call.data == 'diet_rarely':
        user_sessions[user_id]['diet'] = 3
    else:
        user_sessions[user_id]['diet'] = 1
    
    # Следующий вопрос
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Меньше 5 часов", callback_data="transport_low"),
        InlineKeyboardButton("5-10 часов", callback_data="transport_medium"),
        InlineKeyboardButton("Больше 10 часов", callback_data="transport_high")
    ]
    markup.add(*buttons)
    
    bot.edit_message_text("✅ Сохранено", call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "🚗 Часов в неделю в транспорте?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('transport_'))
def handle_transport(call):
    user_id = call.from_user.id
    
    if call.data == 'transport_low':
        user_sessions[user_id]['transport'] = 5
    elif call.data == 'transport_medium':
        user_sessions[user_id]['transport'] = 15
    else:
        user_sessions[user_id]['transport'] = 25
    
    # Следующий вопрос
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Мало (<100 кВт·ч)", callback_data="energy_low"),
        InlineKeyboardButton("Средне (100-200)", callback_data="energy_medium"),
        InlineKeyboardButton("Много (>200 кВт·ч)", callback_data="energy_high")
    ]
    markup.add(*buttons)
    
    bot.edit_message_text("✅ Сохранено", call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "⚡ кВт·ч электроэнергии в месяц?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('energy_'))
def handle_energy(call):
    user_id = call.from_user.id
    
    if call.data == 'energy_low':
        user_sessions[user_id]['energy'] = 50
    elif call.data == 'energy_medium':
        user_sessions[user_id]['energy'] = 100
    else:
        user_sessions[user_id]['energy'] = 150
    
    # Расчет результата
    data = user_sessions[user_id]
    total = data['diet'] + data['transport'] + data['energy']
    
    # Сохраняем в базу
    update_carbon_footprint(user_id, total)
    
    # Бонус за низкий след
    if total < 100:
        update_user_score(user_id, 20)
    
    # Показываем результат
    result = f"""
🌍 Твой углеродный след: {total} кг CO₂/месяц
"""
    bot.send_message(call.message.chat.id, result)
    
   


    
#Запуск бота
bot.polling()








