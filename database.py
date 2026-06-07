from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://<username>:<password>@cluster0.mongodb.net//?appName=Cluster0"
)

db = client["quiz_system"]
