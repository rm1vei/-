import os
import telebot
import requests
import random
from deep_translator import GoogleTranslator

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, 'Привет!😊\nНаберите команду /help чтобы ознакомиться с возможностями нашего кулинарного помощника.')

@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, 'Что я умею:\nУ тебя есть какие-то продукты, но не знаешь, что из них приготовить?\nПиши список, и я найду подходящие рецепты.\nНадеюсь, мы станем отличными помощниками друг другу на кухне!\nОтправь команду /recipe, и я покажу тебе что можно приготовить.')

@bot.message_handler(commands=['recipe'])
def main(message):
    bot.send_message(message.chat.id, 'Введите продукты...')

@bot.message_handler(func=lambda message: True)
def get_recipe(message):
    user_input_ru = message.text

    if not user_input_ru.strip():
        bot.send_message(message.chat.id, "Пожалуйста, введите хотя бы один продукт.")
        return

    try:
        user_input_en = GoogleTranslator(source='auto', target='en').translate(user_input_ru)
        user_input_en = user_input_en.lower().replace(" ", "")
    except Exception:
        bot.send_message(message.chat.id, "Ошибка при переводе продуктов.")
        return

    ingredients = user_input_en.split(',')

    if not ingredients or not any(ingredients):
        bot.send_message(message.chat.id, "Пожалуйста, укажите хотя бы один продукт.")
        return

    all_meals = []

    for ingredient in ingredients:
        ingredient = ingredient.strip()
        if ingredient:
            response = requests.get(f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}")
            if response.status_code == 200:
                data = response.json()
                meals = data.get('meals', [])
                if meals:
                    all_meals.extend(meals)

    if all_meals:
        meal = random.choice(all_meals)
        meal_name = meal['strMeal']
        meal_thumb = meal['strMealThumb']
        meal_id = meal['idMeal']

        details_response = requests.get(f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}")
        if details_response.status_code == 200:
            details_data = details_response.json()
            instructions = details_data['meals'][0]['strInstructions']

            try:
                meal_name_ru = GoogleTranslator(source='en', target='ru').translate(meal_name)
                instructions_ru = GoogleTranslator(source='en', target='ru').translate(instructions)

                if meal_name:
                    bot.send_message(message.chat.id, f"Вот что можно приготовить: *{meal_name_ru}*", parse_mode='Markdown')
                    if instructions:
                        bot.send_message(message.chat.id, f"Рецепт:\n{instructions_ru}", parse_mode='Markdown')
                        bot.send_photo(message.chat.id, meal_thumb)
                    else:
                        bot.send_message(message.chat.id, "Не удалось получить подробный рецепт.")
                else:
                    bot.send_message(message.chat.id, "К сожалению, ничего не найдено по этим продуктам.")
            except Exception:
                bot.send_message(message.chat.id, "Ошибка при переводе рецепта.")
    else:
        bot.send_message(message.chat.id, "К сожалению, ничего не найдено по этим продуктам.")

bot.polling(none_stop=True)
