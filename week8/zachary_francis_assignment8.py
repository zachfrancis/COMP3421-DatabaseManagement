#!/usr/bin/env python3
"""Assignment 8

The following script adds a new passenger to the railways database,
then makes a ticket purchase for that passenger.
"""

import mysql.connector

# Passenger info to add
firstName = "Zach"
lastName = "Francis"
age = 31

# Ride date and desired routes
rideDate = '2023-03-01'
routes = ['A', 'C', 'E']

raildb = mysql.connector.connect(
    user='python-user',
    passwd='mypy123',
    database='railways',
    host='127.0.0.1'
)

myc = raildb.cursor()
myc.execute("use railways")

# Passenger ID will be one more than the max ID in the table
myc.execute("SELECT MAX(id) from Passengers ;")
newId = myc.fetchone()[0] + 1

# Add info to passenger table
print(f"Adding passenger {firstName} {lastName}...")
passenger_data = (newId, firstName, lastName, age)
add_passenger_cmd = """
INSERT INTO Passengers 
(id, firstName, lastName, age)
VALUES (%s, %s, %s, %s)
"""
myc.execute(add_passenger_cmd, passenger_data)
print(f"Passenger {firstName} {lastName} successfully added!\n"
      f"Passenger ID is {newId}\n")

# Ticket Num will be one more than existing max
myc.execute("SELECT MAX(ticketNum) from Tickets ;")
ticketNum = myc.fetchone()[0] + 1

# Add info to passenger table
print(f"Purchasing a ticket for routes {', '.join(routes)} on {rideDate}...")
ticket_data = (ticketNum, rideDate, newId)
add_ticket_cmd = """
INSERT INTO Tickets 
(ticketNum, rideDate, passengerId)
VALUES (%s, %s, %s)
"""
myc.execute(add_ticket_cmd, ticket_data)

# Add each route to the Assigned table
for route in routes:
    myc.execute("INSERT INTO Assigned (ticketNum, routeName) VALUES (%s, %s)", (ticketNum, route))

# Calculate the price
# Add single quotes around each route name so SQL query is valid
route_list = (', '.join('"' + route + '"' for route in routes))
myc.execute(f"SELECT price from Routes where routeName in ({route_list})")
prices = myc.fetchall()
total_price = sum(price[0] for price in prices)
print(f"The total price is ${total_price}")

myc.close()
raildb.commit()
raildb.close()
