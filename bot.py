from dotenv import dotenv_values
from aiogram import Bot, Dispatcher, executor, types
import pymongo
import json
from datetime import datetime
import motor.motor_asyncio

config = dotenv_values(".env")

bot = Bot(config["TOKEN"])
dp = Dispatcher(bot)

@dp.message_handler(commands="start")
async def start(message: types.Message):
    user_id = message.from_user.id 
    user_name = message.from_user.first_name 
    mention = "["+user_name+"](tg://user?id="+str(user_id)+")"
    bot_msg = f"Hi, {mention}!"
    await bot.send_message(message.chat.id, bot_msg, parse_mode="Markdown")

invalid_input_msg = """
Пример формата входных данных:
{
"dt_from":"2022-09-01T00:00:00",
"dt_upto":"2022-12-31T23:59:00",
"group_type":"month"
}
"""

@dp.message_handler()
async def start(message: types.Message):
    # Проверка на правильность введённых данных
    # try:
        parsed_json = json.loads(message.text)
        if not isinstance(parsed_json, dict) or [key for key in ["dt_from", "dt_upto", "group_type"] if key not in parsed_json]:
            await bot.send_message(message.chat.id, invalid_input_msg)
            return

        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(config["MONGO_CLIENT"])
        db = mongo_client["sampleDB"]
        collection = db["sample_collection"]
        
        result = {"dataset": [], "labels": []}

        dt_from = datetime.strptime(parsed_json["dt_from"], "%Y-%m-%dT%H:%M:%S")
        dt_upto = datetime.strptime(parsed_json["dt_upto"], "%Y-%m-%dT%H:%M:%S")
        date_format = "%Y-%m"
        date_format_time = "-01T00:00:00"
        if parsed_json["group_type"] == "day":
            date_format = "%Y-%m-%d"
            date_format_time = "T00:00:00"
        if parsed_json["group_type"] == "hour":
            date_format = "%Y-%m-%dT%H"
            date_format_time = ":00:00"

        pipeline = [
            {"$sort": {"dt": 1}},
            {"$match": {"dt": {"$gte": dt_from, "$lte": dt_upto}}},
            {"$group": {"_id": {"$dateToString": {"format": date_format, "date": "$dt"}}, "total_value": {"$sum": "$value"}}}
        ]
        
        async for document in collection.aggregate(pipeline):
            result["dataset"].append(document.get('total_value'))
            result["labels"].append(document.get('_id') + date_format_time)

        await bot.send_message(message.chat.id, result)
        
    # except:
    #     await bot.send_message(message.chat.id, invalid_input_msg)


if __name__ == "__main__":
    executor.start_polling(dp)