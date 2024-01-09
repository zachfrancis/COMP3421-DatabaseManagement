#!/usr/bin/env python3

# Author: Zachary Francis
# This file creates the tables for a Railway database
# as well as files the tables with data

import mysql.connector
import string
import random
from datetime import date, timedelta

print("Beginning Railway data script...")

raildb = mysql.connector.connect(
    user='python-user',
    passwd='mypy123',
    database='railways',
    host='127.0.0.1'
)

myc = raildb.cursor()
myc.execute("use railways")

# Drop tables
tables = ["BuiltOn", "Assigned", "Trains", "Routes", "Tickets", "Passengers", "Stations"]
for table in tables:
    try:
        myc.execute(f"delete from {table} ;")
    except:
        print(f"{table} does not exist")
    myc.execute(f"drop table if exists {table} ;")

# Constants for data generation
numStations = 80
numPassengers = 50000
numTrains = 200
numRoutes = 12
numTickets = 1000000
station_codes = []  # Store station codes to be used by Routes and BuiltOn

# Names for random name generation
with open('fnames.txt','r') as f:
    firstNames = f.read().splitlines()

with open('lnames.txt','r') as f:
    lastNames = f.read().splitlines()

# Function for random id generation
# Pass a size, returns a random sequence of characters (letters + digits)
def id_generator(size=8):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))


# Function to get a random date between start date and end date
def rand_date(start=date(2023, 1, 1), end=date(2023, 12, 31)):
    date_range = end - start
    day_delta = random.randint(0, date_range.days)
    return start + timedelta(days=day_delta)


# Function to generate station info
def station_info(size):
    for i in range(1, size+1):
        rand_code = id_generator(8)
        station_codes.append(rand_code)
        yield rand_code, f"Station{i}", f"{random.randint(1, 100)}th Street"


# Function to generate passenger info
def passenger_info(size):
    for i in range(1, size+1):
        yield i, random.choice(firstNames), random.choice(lastNames), random.randint(16, 80)


# Function to generate Route info
# I am using uppercase chars for route names, so do not add more than 26
def route_info(size):
    for i in range(size):
        endpoints = random.sample(station_codes, 2)
        duration = random.randint(30, 120)
        price = duration / 10  # Price per route, based off duration
        yield string.ascii_uppercase[i], endpoints[0], endpoints[1], duration, price


# Function to generate Ticket info
def ticket_info(size):
    for i in range(1, size+1):
        yield i, rand_date(), random.randint(1, numPassengers)


# Function to generate Train info
def train_info(size):
    speeds = [90, 120, 160, 200]
    capacities = [200, 400, 600, 800, 1000]
    routes = string.ascii_uppercase[:numRoutes]
    for i in range(1, size+1):
        yield i, random.choice(speeds), random.choice(capacities), random.choice(routes)


# Create Stations
print(f"Creating Station table and adding {numStations} stations")
myc.execute("""
create table Stations (
    code char(8),
    stationName varchar(20),
    street varchar(20),
    PRIMARY KEY (code) ) ;
""")
for station in station_info(numStations):
    cmd = "INSERT IGNORE INTO Stations (code, stationName, street) VALUES (%s, %s, %s)"
    myc.execute(cmd, station)

# Create Passengers
print(f"Creating Passenger table and adding {numPassengers} passengers")
myc.execute("""
create table Passengers (
    id int,
    firstName varchar(20),
    lastName varchar(20),
    age int,
    PRIMARY KEY (id) ) ;
""")
for passenger in passenger_info(numPassengers):
    cmd = "INSERT INTO Passengers (id, firstName, lastName, age) VALUES (%s, %s, %s, %s)"
    myc.execute(cmd, passenger)

# Create Routes
print(f"Creating Routes table and adding {numRoutes} routes")
myc.execute("""
create table Routes (
    routeName varchar(10),
    startStation varchar(20), 
    endStation varchar(20),
    duration int,
    price float,
    PRIMARY KEY (routeName),
    FOREIGN KEY (startStation) references Stations(code),
    FOREIGN KEY (endStation) references Stations(code)) ;
""")
for route in route_info(numRoutes):
    cmd = "INSERT INTO Routes (routeName, startStation, endStation, duration, price) VALUES (%s, %s, %s, %s, %s)"
    myc.execute(cmd, route)

# Create Tickets and the relation between tickets and routes
print(f"Creating Tickets table and adding {numTickets} tickets")
myc.execute("""
create table Tickets (
    ticketNum int,
    rideDate date,
    passengerId int,
    PRIMARY KEY (ticketNum),
    FOREIGN KEY (passengerId) references Passengers(id)) ;
""")
print(f"Creating Assigned table")
myc.execute("""
create table Assigned (
    ticketNum int,
    routeName varchar(10),
    PRIMARY KEY (ticketNum, routeName),
    FOREIGN KEY (ticketNum) references Tickets(ticketNum),
    FOREIGN KEY (routeName) references Routes(routeName));
""")
for ticket in ticket_info(numTickets):
    cmd = "INSERT INTO Tickets (ticketNum, rideDate, passengerId) VALUES (%s, %s, %s)"
    myc.execute(cmd, ticket)

    # Add entry to Assigned, tickets will be good for 1 to 5 routes
    routes = string.ascii_uppercase[:numRoutes]
    cmd = "INSERT INTO Assigned (ticketNum, routeName) VALUES (%s, %s)"
    for route in random.sample(routes, random.randint(1, 5)):
        myc.execute(cmd, (ticket[0], route))


# Create Trains
print(f"Creating Trains table and adding {numTrains} trains")
myc.execute("""
create table Trains (
    trainNum int,
    maxSpeed float,
    capacity int,
    routeName varchar(10),
    FOREIGN KEY (routeName) references Routes(routeName),
    PRIMARY KEY (trainNum) ) ;
""")
for train in train_info(numTrains):
    cmd = "INSERT INTO Trains (trainNum, maxSpeed, capacity, routeName) VALUES (%s, %s, %s, %s)"
    myc.execute(cmd, train)


# Create relation between routes and stations
myc.execute("""
create table BuiltOn (
    stationCode char(8),
    routeName varchar(10),
    PRIMARY KEY (stationCode, routeName),
    FOREIGN KEY (stationCode) references Stations(code),
    FOREIGN KEY (routeName) references Routes(routeName));
""")
for station in station_codes:
    cmd = "INSERT INTO BuiltOn (stationCode, routeName) VALUES (%s, %s)"
    routes = string.ascii_uppercase[:numRoutes]
    # Stations can be assigned between 1 to 3 routes, 1 is weighted heavier
    weighted_ints = [1] * 5 + [2] * 2 + [3]
    for route in random.sample(routes, random.choice(weighted_ints)):
        myc.execute(cmd, (station, route))

myc.close()
raildb.commit()
raildb.close()