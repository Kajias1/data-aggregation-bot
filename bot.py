from dotenv import dotenv_values
from aiogram import Bot, Dispatcher, executor, types
import pymongo

config = dotenv_values(".env")

mongo_client = pymongo.MongoClient(config["MONGO_CLIENT"])
db = mongo_client["sampleDB"]
collection = db["sample_collection"]

bot = Bot(config["TOKEN"])
dp = Dispatcher(bot)

@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer("Hello!")

if __name__ == "__main__":
    executor.start_polling(dp)