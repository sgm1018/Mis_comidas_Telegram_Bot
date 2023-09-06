import telebot
import logging

# Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# init bot
TOKEN = "6423462500:AAFzq3l8dGJSNumVXf4q-I1zkA7YDcSqw0s"
bot = telebot.TeleBot(TOKEN)
opciones = []
desayunos = {}  # Guardará el desayuno de cada usuario
PRECIO_TORTILLA = 1.80
PRECIO_BEBIDA = 1.40
PRECIO_COMBO = 2.90



@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=False, selective=True) # set one_time_keyboard to False for default
    opciones = ['/desayuno', '/resumen']
    for opcion in opciones:
        markup.add(opcion)
    bot.reply_to(message, "¡Bienvenido al bot de desayunos! Usa el comando /desayuno para empezar \nEscriba /resumen Para ver todos los desayunos.", reply_markup=markup)
    logging.info(f"Usuario: {message.from_user.first_name} (ID: {message.chat.id}) ha ingresado el comando: {message.text}")

@bot.message_handler(commands=['desayuno', 'Desayuno', 'DESAYUNO', 'd'])
def seleccion_desayuno(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, selective=True)
    opciones = ['Nada', 'Tortilla de Bacon', 'Tortilla de Cecina', 'Tortilla de Jamon', 'Tortilla de Chaka', 'Tortilla de Picante', 'Tortilla de Bonito', 'Tortilla de Cebolla', 'Tortilla de Alioli', 'Tostada']
    for opcion in opciones:
        markup.add(opcion)
    bot.send_message(message.chat.id, "Elige tu comida:", reply_markup=markup)
    bot.register_next_step_handler(message, seleccion_bebida)
    logging.info(f"Usuario: {message.from_user.first_name} (ID: {message.chat.id}) ha ingresado el comando: {message.text}")

def seleccion_bebida(message):
    comida = message.text
    desayunos[message.chat.id] = {'comida': comida}
    
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True ,selective=True)
    opciones = ['Nada', 'Café Solo', 'Café Cortado', 'Café Leche', 'Café Americano', 'Poleo Menta']
    for opcion in opciones:
        markup.add(opcion)
    bot.send_message(message.chat.id, "Elige tu bebida:", reply_markup=markup)
    bot.register_next_step_handler(message, seleccion_hielo)

def seleccion_hielo(message):
    bebida = message.text
    desayunos[message.chat.id]['bebida'] = bebida
    
    if bebida != "Nada":
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, selective=True)
        opciones = ['Con hielo', 'Sin hielo']
        for opcion in opciones:
            markup.add(opcion)
        bot.send_message(message.chat.id, "¿Quieres hielo?", reply_markup=markup)
        bot.register_next_step_handler(message, guardar_desayuno)
    else:
        guardar_desayuno(message)
def guardar_desayuno(message):
    if message.text in ['Con hielo', 'Sin hielo']:
        desayunos[message.chat.id]['hielo'] = message.text
    else:
        desayunos[message.chat.id]['hielo'] = "N/A"
    bot.send_message(message.chat.id, "¡Desayuno guardado!")
    calcular_costo(message.chat.id)
    logging.info(f"Usuario: {message.from_user.first_name} (ID: {message.chat.id}) ha pedido: Comida - {desayunos[message.chat.id]['comida']}, Bebida - {desayunos[message.chat.id]['bebida']}, Hielo - {desayunos[message.chat.id]['hielo']}")

    reset(message)
    
    
@bot.message_handler(commands=['resumen', 'Resumen','RESUMEN','r'])
def mostrar_resumen(message):
    totales_comida = {}
    totales_bebida = {}
    total_general = 0  # Se añade un acumulador para el costo total
    comida_to_show = ""
    bebida_to_show = ""
    costo_toShow=""
    for chat_id, desayuno in desayunos.items():
        comida = desayuno['comida']
        bebida = desayuno['bebida']
        if comida in totales_comida:
            totales_comida[comida] += 1
        else:
            totales_comida[comida] = 1

        if bebida in totales_bebida:
            totales_bebida[bebida] += 1
        else:
            totales_bebida[bebida] = 1

        total_general += desayuno['costo']  # Se acumula el costo total


    mensaje = "<b>Resumen de Desayunos:</b>\n\n"
    mensaje += "\n<b>Costos:</b>\n"
    for chat_id, desayuno in desayunos.items():
        if desayuno['comida'] != "Nada":
            comida_to_show= desayuno['comida']
        if desayuno['bebida'] != "Nada":
            bebida_to_show= desayuno['bebida']
        chat_info = bot.get_chat(chat_id)
        usuario = chat_info.username if chat_info.username else f"{chat_info.first_name} {chat_info.last_name if chat_info.last_name else ''}".strip()
        
        mensaje += f"@{usuario}: {comida_to_show} {bebida_to_show} - {desayuno['costo']}€\n"   
        
    mensaje += "<b>Total:</b>\n"
    mensaje += "<b>Comida ☕️:</b>\n"
    for comida, cantidad in totales_comida.items():
        if comida != "Nada":
            mensaje += f"     {comida}: {cantidad}\n"
    mensaje += "<b>Bebida 🥤:</b>\n"
    for bebida, cantidad in totales_bebida.items():
        if bebida != "Nada":
            mensaje += f"     {bebida}: {cantidad}\n"

    mensaje += f"\n<b>Total a pagar:</b> {total_general:.2f}€\n"  # Se muestra el costo total
    bot.send_message(message.chat.id, mensaje, parse_mode='HTML')
    logging.info(f"Usuario: {message.from_user.first_name} (ID: {message.chat.id}) ha ingresado el comando: {message.text}")
    logging.info(mensaje)
    reset(message)

def calcular_costo(chat_id):
    comida = desayunos[chat_id]['comida']
    bebida = desayunos[chat_id]['bebida']
    
    if comida != "Nada" and bebida != "Nada":
        desayunos[chat_id]['costo'] = PRECIO_COMBO
    else:
        costo = 0
        if comida != "Nada":
            costo += PRECIO_TORTILLA
        if bebida != "Nada":
            costo += PRECIO_BEBIDA
        desayunos[chat_id]['costo'] = costo
            
def reset(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=False, selective=True)
    opciones = ['/desayuno', '/resumen']
    for opcion in opciones:
        markup.add(opcion)
    bot.send_message(message.chat.id, "¿Qué deseas hacer ahora?", reply_markup=markup)
    
    
print("iniciando el bot mis_comidas:\n\n")
bot.polling()
