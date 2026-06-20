import os
import sys
import json
import telebot
from telebot import types

# ⚠️ التوكن الحُر الجديد والبيانات الثابتة لمتجرك
TOKEN = "8700905522:AAG61fDryAXFDpfyyZ8U9v33wju-jiR1W2o"
ADMIN_ID = 8243108672  
EXCHANGE_RATE = 14750  
SHAM_CASH_WALLET = "8bf19e519ba13641f2a8ae981b8f3081" 
SUPPORT_NUMBER = "939965929" 

bot = telebot.TeleBot(TOKEN)
DB_FILE = "database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content: return json.loads(content)
        except: pass
    return {'users': {}, 'orders_count': 8500, 'charge_count': 1000}

def save_db(data):
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f: 
            json.dump(data, f, ensure_ascii=False, indent=4)
    except: pass

db = load_db()
if "users" not in db: db["users"] = {}
if "orders_count" not in db: db["orders_count"] = 8500
if "charge_count" not in db: db["charge_count"] = 1000
save_db(db)

pending_orders = {}
pending_charges = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('💰 مستند حسابي ورصيدي'), types.KeyboardButton('🛒 المتجر'))
    markup.add(types.KeyboardButton('➕ شحن رصيد (شام كاش)'), types.KeyboardButton('📞 الدعم الفني'))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    if uid not in db['users']:
        db['users'][uid] = {'balance_syr': 0, 'docs_count': 0, 'selected_product': None}
        save_db(db)
    bot.send_message(message.chat.id, f"🎯 مرحباً بك في متجر الشحن الرقمي المتكامل!\n💵 سعر الصرف الحالي: 1$ = {EXCHANGE_RATE:,} ل.س", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == '💰 مستند حسابي ورصيدي')
def show_balance(message):
    uid = str(message.chat.id)
    if uid not in db['users']: 
        db['users'][uid] = {'balance_syr': 0, 'docs_count': 0, 'selected_product': None}
        save_db(db)
    b_syr = db['users'][uid]['balance_syr']
    b_usd = b_syr / EXCHANGE_RATE if b_syr > 0 else 0.0
    bot.send_message(message.chat.id, f'📋 **كشف حسابك المالي:**\n\n💵 رصيدك بالليرة: {b_syr:,} ل.س\n💳 رصيدك بالدولار: {b_usd:.2f} $\n📄 مستندات الشراء الناجحة: {db["users"][uid]["docs_count"]}')

@bot.message_handler(func=lambda message: message.text == '➕ شحن رصيد (شام كاش)')
def charge_request(message):
    bot.send_message(message.chat.id, f'💳 **الشحن عبر محفظة شام كاش:**\n\nيرجى تحويل الأموال إلى الرقم التالي:\n`{SHAM_CASH_WALLET}`\n\n✍️ بعد التحويل الفعلي، أرسل قيمة المبلغ بالدولار ($) هنا ليتم مراجعته وتأكيده من الإدارة:')
    bot.register_next_step_handler(message, process_charging)

def process_charging(message):
    try:
        usd_amount = float(message.text)
        syr_amount = int(usd_amount * EXCHANGE_RATE)
        uid = str(message.chat.id)
        db['charge_count'] += 1
        save_db(db)
        pending_charges[db['charge_count']] = {'user_id': uid, 'amount_syr': syr_amount, 'amount_usd': usd_amount}
        bot.send_message(message.chat.id, f'⏳ تم إرسال طلب الشحن رقم `#{db["charge_count"]}` بقيمة {syr_amount:,} ل.س للإدارة.\n⚠️ يرجى الانتظار لحين مراجعة وتأكيد وصول الحوالة المالية الفعلي من قِبل الإدارة.')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('✅ نعم وصل المال', callback_data=f'c_y_{db["charge_count"]}'))
        markup.add(types.InlineKeyboardButton('❌ لم يصلني شيء', callback_data=f'c_n_{db["charge_count"]}'))
        bot.send_message(ADMIN_ID, f'💰 **طلب شحن رصيد جديد (#{db["charge_count"]})**\n\n🆔 آيدي الزبون: `{uid}`\n💵 المبلغ: {usd_amount}$\n💵 القيمة: {syr_amount:,} ل.س', reply_markup=markup)
    except:
        bot.send_message(message.chat.id, '❌ خطأ، يرجى إدخال رقم صحيح فقط.')

@bot.message_handler(func=lambda message: message.text == '📞 الدعم الفني')
def support_info(message): 
    bot.send_message(message.chat.id, f"📞 تواصل مع الدعم الفني للإدارة عبر تيليجرام:\n\n💬 المعرف المباشر: @c{SUPPORT_NUMBER}")

@bot.message_handler(func=lambda message: message.text == '🛒 المتجر')
def show_shop_main(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🎮 متجر الألعاب الشامل', callback_data='sub_games'))
    bot.send_message(message.chat.id, '🛒 أهلاً بك في المتجر الرئيسي، اضغط بالأسفل لفتح قائمة الألعاب والتصنيفات:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'sub_games')
def sub_games_menu(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🎮 شدات ببجي مبايل', callback_data='game_pubg'))
    markup.add(types.InlineKeyboardButton('🔫 عملات كول اوف ديوتي', callback_data='game_cod'))
    markup.add(types.InlineKeyboardButton('🔥 جواهر فري فاير', callback_data='game_ff'))
    markup.add(types.InlineKeyboardButton('⚔️ ألماس موبايل ليجندز', callback_data='game_ml'))
    markup.add(types.InlineKeyboardButton('🏰 كلاش اوف كلانس وروبلوكس', callback_data='game_other'))
    bot.edit_message_text('🎮 تفضل بفتح متجر الألعاب المتاحة، اختر اللعبة للتصفح والشراء منها:', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'game_pubg')
def shop_pubg(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"🎮 ببجي - 60 UC ({int(1.0*EXCHANGE_RATE):,} ل.س)", callback_data="buy_pubg_60"))
    markup.add(types.InlineKeyboardButton(f"🎮 ببجي - 325 UC ({int(5.0*EXCHANGE_RATE):,} ل.س)", callback_data="buy_pubg_325"))
    markup.add(types.InlineKeyboardButton(f"🎮 ببجي - 660 UC ({int(9.8*EXCHANGE_RATE):,} ل.س)", callback_data="buy_pubg_660"))
    markup.add(types.InlineKeyboardButton('🔙 العودة لمتجر الألعاب', callback_data='sub_games'))
    bot.edit_message_text('👇 اختر باقة الشدات المطلوبة للعبة ببجي موبايل:', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'game_cod')
def shop_cod(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"🔫 كول اوف ديوتي - 320 CP ({int(5.0*EXCHANGE_RATE):,} ل.س)", callback_data="buy_cod_320"))
    markup.add(types.InlineKeyboardButton(f"🔫 كول اوف ديوتي - 480 CP ({int(7.3*EXCHANGE_RATE):,} ل.س)", callback_data="buy_cod_480"))
    markup.add(types.InlineKeyboardButton('🔙 العودة لمتجر الألعاب', callback_data='sub_games'))
    bot.edit_message_text('👇 اختر باقة العملات المطلوبة للعبة كول اوف ديوتي:', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'game_ff')
def shop_ff(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"🔥 فري فاير - 100+10 جواهر ({int(1.0*EXCHANGE_RATE):,} ل.س)", callback_data="buy_ff_100"))
    markup.add(types.InlineKeyboardButton(f"🔥 فري فاير - 210+21 جواهر ({int(2.0*EXCHANGE_RATE):,} ل.س)", callback_data="buy_ff_210"))
    markup.add(types.InlineKeyboardButton(f"🔥 فري فاير - 530+53 جواهر ({int(5.0*EXCHANGE_RATE):,} ل.س)", callback_data="buy_ff_530"))
    markup.add(types.InlineKeyboardButton('🔙 العودة لمتجر الألعاب', callback_data='sub_games'))
    bot.edit_message_text('👇 اختر باقة الجواهر المطلوبة للعبة فري فاير:', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'game_ml')
def shop_ml(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"⚔️ موبايل ليجندز - 172 ألماس ({int(2.9*EXCHANGE_RATE):,} ل.س)", callback_data="buy_ml_172"))
    markup.add(types.InlineKeyboardButton(f"⚔️ موبايل ليجندز - 257 ألماس ({int(4.0*EXCHANGE_RATE):,} ل.س)", callback_data="buy_ml_257"))
    markup.add(types.InlineKeyboardButton('🔙 العودة لمتجر الألعاب', callback_data='sub_games'))
    bot.edit_message_text('👇 اختر باقة الألماس المطلوبة لموبايل ليجندز:', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'game_other')
def shop_other(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"🏰 كلاش - 88 جوهرة ({int(1.3*EXCHANGE_RATE):,} ل.س)", callback_data="buy_coc_88"))
    markup.add(types.InlineKeyboardButton(f"🏰 كلاش - 500 جوهرة ({int(6.6*EXCHANGE_RATE):,} ل.س)", callback_data="buy_coc_500"))
    markup.add(types.InlineKeyboardButton(f"🧱 روبلوكس - كود 10$ ({int(10.0*EXCHANGE_RATE):,} ل.س)", callback_data="buy_roblox_10"))
    markup.add(types.InlineKeyboardButton('🔙 العودة لمتجر الألعاب', callback_data='sub_games'))
    bot.edit_message_text('👇 اختر الباقة المطلوبة لشحن كلاش أو روبلوكس:', call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def process_purchase_click(call):
    user_id = call.message.chat.id
    b_data = call.data
    uid = str(user_id)
    p_name, p_cost = "", 0.0
    if b_data == "buy_pubg_60": p_name, p_cost = "🎮 شدات ببجي - 60 UC", 1.0
    elif b_data == "buy_pubg_325": p_name, p_cost = "🎮 شدات ببجي - 325 UC", 5.0
    elif b_data == "buy_pubg_660": p_name, p_cost = "🎮 شدات ببجي - 660 UC", 9.80
    elif b_data == "buy_cod_320": p_name, p_cost = "🔫 عملات كول اوف ديوتي - 320 CP", 5.0
    elif b_data == "buy_cod_480": p_name, p_cost = "🔫 عملات كول اوف ديوتي - 480 CP", 7.30
    elif b_data == "buy_ff_100": p_name, p_cost = "🔥 جواهر فري فاير - 100+10", 1.0
    elif b_data == "buy_ff_210": p_name, p_cost = "🔥 جواهر فري فاير - 210+21", 2.0
    elif b_data == "buy_ff_530": p_name, p_cost = "🔥 جواهر فري فاير - 530+53", 5.0
    elif b_data == "buy_ml_172": p_name, p_cost = "⚔️ ألماس موبايل ليجندز - 172", 2.90
    elif b_data == "buy_ml_257": p_name, p_cost = "⚔️ ألماس موبايل ليجندز - 257", 4.0
    elif b_data == "buy_coc_88": p_name, p_cost = "🏰 جواهر كلاش - 88", 1.30
