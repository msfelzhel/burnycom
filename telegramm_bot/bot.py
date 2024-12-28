import telebot
import psycopg
from telebot import types
import datetime
import logging

# Логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Токен вашего бота (получить в @BotFather)
BOT_TOKEN = 'TOKEN'
bot = telebot.TeleBot(BOT_TOKEN)

# Функция для подключения к базе данных
def connect_to_db():
    try:
        conn = psycopg.connect(
            dbname="home",
            user="home",
            password="123",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return None

# Функция для получения списка пользователей из базы данных
def get_users(conn):
    try:
        cur = conn.cursor()
        cur.execute("SELECT username FROM public.user")
        users = cur.fetchall()
        return [user[0] for user in users]
    except Exception as e:
        logging.error(f"Ошибка при получении пользователей: {e}")
        return []

# Генерация клавиатуры с кнопками пользователей
def generate_user_markup(users):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for user in users:
        markup.add(types.KeyboardButton(user))
    return markup

# Отправка списка команд
def send_command_list(chat_id):
    commands = (
        "/start - Запустить бота и выбрать пользователя\n"
        "/tasks - Просмотр списка задач\n"
        "/delete - Удаление задачи по ID\n"
        "/add_user - Добавить нового пользователя\n"
        "/clear_tasks - Удалить все задачи для пользователя\n"
        "/help - Список команд"
    )
    bot.send_message(chat_id, f"Доступные команды:\n{commands}")

# Обработка команды "/start"
@bot.message_handler(commands=['start'])
def start(message):
    send_command_list(message.chat.id)

    conn = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
        return

    users = get_users(conn)
    conn.close()

    if not users:
        bot.send_message(message.chat.id, "Нет доступных пользователей.")
        return

    markup = generate_user_markup(users)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите пользователя:", reply_markup=markup)

# Обработка выбора пользователя
@bot.message_handler(func=lambda message: message.text in get_users(connect_to_db()))
def process_user_selection(message):
    selected_user = message.text
    conn = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
        return

    cur = conn.cursor()
    cur.execute("SELECT id FROM public.user WHERE username=%s", (selected_user,))
    user_id = cur.fetchone()[0]
    conn.close()

    bot.send_message(message.chat.id, "Введите текст задачи:")
    bot.register_next_step_handler(message, process_task_text, user_id)

# Обработка текста задачи
def process_task_text(message, user_id):
    task_text = message.text
    current_time = datetime.datetime.now()
    conn = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
        return

    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO public.tasks (user_id, task_text, created_at) VALUES (%s, %s, %s)", 
                    (user_id, task_text, current_time))
        conn.commit()
        bot.send_message(message.chat.id, "Задача создана успешно!")
    except Exception as e:
        logging.error(f"Ошибка при добавлении задачи: {e}")
        bot.send_message(message.chat.id, "Ошибка при создании задачи.")
    finally:
        conn.close()

# Просмотр задач
@bot.message_handler(commands=['tasks'])
def view_tasks(message):
    conn = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT t.id, t.task_text, u.username, t.created_at FROM public.tasks t JOIN public.user u ON t.user_id = u.id ORDER BY t.created_at DESC")
        tasks = cur.fetchall()

        if not tasks:
            bot.send_message(message.chat.id, "Задач нет.")
            return

        response = "\n".join([f"ID: {task[0]}\nЗадача: {task[1]}\nПользователь: {task[2]}\nДата: {task[3]}" for task in tasks])
        bot.send_message(message.chat.id, response)
    except Exception as e:
        logging.error(f"Ошибка при получении задач: {e}")
        bot.send_message(message.chat.id, "Ошибка при получении задач.")
    finally:
        conn.close()

# Удаление задач
@bot.message_handler(commands=['delete'])
def delete_task(message):
    bot.send_message(message.chat.id, "Введите ID задачи, которую хотите удалить:")
    bot.register_next_step_handler(message, process_task_deletion)

def process_task_deletion(message):
    try:
        task_id = int(message.text)
        conn = connect_to_db()
        if not conn:
            bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
            return

        cur = conn.cursor()
        cur.execute("DELETE FROM public.tasks WHERE id=%s", (task_id,))
        conn.commit()
        conn.close()

        bot.send_message(message.chat.id, "Задача успешно удалена!")
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ID задачи. Попробуйте снова.")
    except Exception as e:
        logging.error(f"Ошибка при удалении задачи: {e}")
        bot.send_message(message.chat.id, "Ошибка при удалении задачи.")

# Добавление нового пользователя
@bot.message_handler(commands=['add_user'])
def add_user(message):
    bot.send_message(message.chat.id, "Введите имя нового пользователя:")
    bot.register_next_step_handler(message, process_add_user)

def process_add_user(message):
    username = message.text
    conn = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
        return

    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO public.user (username) VALUES (%s)", (username,))
        conn.commit()
        bot.send_message(message.chat.id, "Пользователь успешно добавлен!")
    except Exception as e:
        logging.error(f"Ошибка при добавлении пользователя: {e}")
        bot.send_message(message.chat.id, "Ошибка при добавлении пользователя.")
    finally:
        conn.close()

# Удаление всех задач пользователя
@bot.message_handler(commands=['clear_tasks'])
def clear_tasks(message):
    bot.send_message(message.chat.id, "Введите имя пользователя для очистки всех задач:")
    bot.register_next_step_handler(message, process_clear_tasks)

def process_clear_tasks(message):
    username = message.text
    conn = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM public.user WHERE username=%s", (username,))
        user_id = cur.fetchone()

        if not user_id:
            bot.send_message(message.chat.id, "Пользователь не найден.")
            return

        cur.execute("DELETE FROM public.tasks WHERE user_id=%s", (user_id[0],))
        conn.commit()
        bot.send_message(message.chat.id, f"Все задачи пользователя {username} удалены!")
    except Exception as e:
        logging.error(f"Ошибка при удалении задач пользователя: {e}")
        bot.send_message(message.chat.id, "Ошибка при удалении задач пользователя.")
    finally:
        conn.close()

@bot.message_handler(commands=['help'])
def help_command(message):
    commands = (
        "/start - Запустить бота и выбрать пользователя\n"
        "/tasks - Просмотр списка задач\n"
        "/delete - Удаление задачи по ID\n"
        "/add_user - Добавить нового пользователя\n"
        "/clear_tasks - Удалить все задачи для пользователя\n"
        "/help - Список команд\n"
        "/user_tasks - Просмотр задач конкретного пользователя\n"
        "/update_task - Обновить текст задачи по ID\n"
        "/task_summary - Получить статистику задач\n"
        "/assign_task - Назначить задачу пользователю\n"
        "/due_tasks - Просмотр задач с истекающим сроком"
    )
    bot.send_message(message.chat.id, f"Доступные команды:\n{commands}")

# Просмотр задач конкретного пользователя
@bot.message_handler(commands=['user_tasks'])
def view_user_tasks(message):
    bot.send_message(message.chat.id, "Введите имя пользователя для просмотра его задач:")
    bot.register_next_step_handler(message, process_user_tasks)

def process_user_tasks(message):
    username = message.text
    conn = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT t.id, t.task_text, t.created_at FROM public.tasks t JOIN public.user u ON t.user_id = u.id WHERE u.username = %s ORDER BY t.created_at DESC", (username,))
        tasks = cur.fetchall()

        if not tasks:
            bot.send_message(message.chat.id, f"У пользователя {username} задач нет.")
            return

        response = f"Задачи пользователя {username}:\n" + "\n".join([f"ID: {task[0]}, Задача: {task[1]}, Дата: {task[2]}" for task in tasks])
        bot.send_message(message.chat.id, response)
    except Exception as e:
        logging.error(f"Ошибка при получении задач пользователя: {e}")
        bot.send_message(message.chat.id, "Ошибка при получении задач пользователя.")
    finally:
        conn.close()

# Обновление задачи по ID
@bot.message_handler(commands=['update_task'])
def update_task(message):
    bot.send_message(message.chat.id, "Введите ID задачи, которую хотите обновить:")
    bot.register_next_step_handler(message, get_task_id_for_update)

def get_task_id_for_update(message):
    try:
        task_id = int(message.text)
        bot.send_message(message.chat.id, "Введите новый текст задачи:")
        bot.register_next_step_handler(message, process_task_update, task_id)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ID. Попробуйте снова.")


def process_task_update(message, task_id):
    new_text = message.text
    conn = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
        return

    try:
        cur = conn.cursor()
        cur.execute("UPDATE public.tasks SET task_text = %s WHERE id = %s", (new_text, task_id))
        conn.commit()
        bot.send_message(message.chat.id, "Задача успешно обновлена!")
    except Exception as e:
        logging.error(f"Ошибка при обновлении задачи: {e}")
        bot.send_message(message.chat.id, "Ошибка при обновлении задачи.")
    finally:
        conn.close()

# Назначение задачи пользователю
@bot.message_handler(commands=['assign_task'])
def assign_task(message):
    bot.send_message(message.chat.id, "Введите имя пользователя, которому нужно назначить задачу:")
    bot.register_next_step_handler(message, get_user_for_assignment)

def get_user_for_assignment(message):
    username = message.text
    conn = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM public.user WHERE username = %s", (username,))
        user = cur.fetchone()

        if not user:
            bot.send_message(message.chat.id, f"Пользователь {username} не найден.")
            return

        user_id = user[0]
        bot.send_message(message.chat.id, "Введите текст задачи для назначения:")
        bot.register_next_step_handler(message, assign_task_to_user, user_id)
    except Exception as e:
        logging.error(f"Ошибка при поиске пользователя: {e}")
        bot.send_message(message.chat.id, "Ошибка при поиске пользователя.")
    finally:
        conn.close()

def assign_task_to_user(message, user_id):
    task_text = message.text
    current_time = datetime.datetime.now()
    conn = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
        return

    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO public.tasks (user_id, task_text, created_at) VALUES (%s, %s, %s)", 
                    (user_id, task_text, current_time))
        conn.commit()
        bot.send_message(message.chat.id, "Задача успешно назначена!")
    except Exception as e:
        logging.error(f"Ошибка при назначении задачи: {e}")
        bot.send_message(message.chat.id, "Ошибка при назначении задачи.")
    finally:
        conn.close()

# Просмотр задач с истекающим сроком
@bot.message_handler(commands=['due_tasks'])
def view_due_tasks(message):
    bot.send_message(message.chat.id, "Введите количество дней для проверки истекающих задач:")
    bot.register_next_step_handler(message, process_due_tasks)

def process_due_tasks(message):
    try:
        days = int(message.text)
        due_date = datetime.datetime.now() + datetime.timedelta(days=days)
        conn = connect_to_db()
        if not conn:
            bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
            return

        cur = conn.cursor()
        cur.execute("SELECT t.id, t.task_text, t.created_at, u.username FROM public.tasks t JOIN public.user u ON t.user_id = u.id WHERE t.created_at <= %s", (due_date,))
        tasks = cur.fetchall()

        if not tasks:
            bot.send_message(message.chat.id, f"Нет задач с истекающим сроком в ближайшие {days} дней.")
            return

        response = f"Задачи с истекающим сроком в ближайшие {days} дней:\n" + "\n".join([
            f"ID: {task[0]}, Задача: {task[1]}, Дата: {task[2]}, Пользователь: {task[3]}" for task in tasks
        ])
        bot.send_message(message.chat.id, response)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное число. Попробуйте снова.")
    except Exception as e:
        logging.error(f"Ошибка при получении задач с истекающим сроком: {e}")
        bot.send_message(message.chat.id, "Ошибка при получении задач с истекающим сроком.")
    finally:
        conn.close()

# Статистика задач
@bot.message_handler(commands=['task_summary'])
def task_summary(message):
    conn = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT u.username, COUNT(t.id) FROM public.tasks t JOIN public.user u ON t.user_id = u.id GROUP BY u.username ORDER BY COUNT(t.id) DESC")
        summary = cur.fetchall()

        if not summary:
            bot.send_message(message.chat.id, "Задачи отсутствуют.")
            return

        response = "Статистика задач:\n" + "\n".join([f"Пользователь: {row[0]}, Количество задач: {row[1]}" for row in summary])
        bot.send_message(message.chat.id, response)
    except Exception as e:
        logging.error(f"Ошибка при получении статистики задач: {e}")
        bot.send_message(message.chat.id, "Ошибка при получении статистики задач.")
bot.polling() 