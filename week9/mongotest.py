#!/usr/bin/env python3

import pymongo
import random
import pprint

client = pymongo.MongoClient()

db = client.Performances
Groups = db.Groups

for i in range(5):
    Groups.insert_one({"name": f"Band {i}", "numberMembers": i + 3, "costToBook": i * 500, "genre": f"genre{i}"})

Venue = db.Venue
for i in range(3):
    Venue.insert_one({"name": f"Venue {i}", "city": "Denver", "seatingCapcity": random.randint(1,20) * 1000})
    
UpcomingPerformances = db.UpcomingPerformances
UpcomingPerformances.insert_one({"groupName": "Band 1", "performances": [{"venueName":"Venue 1", "date":"2023-3-28"}]})

pprint.pprint(Groups.find_one({"numberMembers": 5}))
pprint.pprint(Venue.find_one({"city": {"$regex": 'Den'} }))

Groups.delete_one({"name": "Band 4"})
