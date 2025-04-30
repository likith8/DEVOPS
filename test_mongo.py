from pymongo import MongoClient
import certifi

uri = "mongodb+srv://likithm539:likith123@data.otirnyd.mongodb.net/?retryWrites=true&w=majority&appName=Data"

try:
    client = MongoClient(uri, tls=True, tlsCAFile=certifi.where())
    print("Databases:", client.list_database_names())
except Exception as e:
    print("Connection error:", e)
