from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://talha:talha12345@cluster0.cah2qrr.mongodb.net/?appName=Cluster0"
)

db = client["quiz_system"]