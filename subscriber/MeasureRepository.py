from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


# Class MeasureRepository
class MeasureRepository:

    # Method: Constructor
    def __init__(self):
        self.uri = "mongodb+srv://andres345gm:UjFZq4tQgCJHCQ4U@waterqualitysystem.q1xr99q.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
        #self.uri = "mongodb+srv://andres345gm:UjFZq4tQgCJHCQ4U@waterqualitysystem.q1xr99q.mongodb.net/?retryWrites=true&w=majority"
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        self.db = self.client["water-measures"]
        self.collection = self.db["measures"]

    # end def

    # Method: Insert measure into database
    def insert_measure(self, measure):
        self.collection.insert_one(measure)

    # end def

# end class
