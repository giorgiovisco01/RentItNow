#!/usr/bin/env python
# coding: utf-8

# ## RentItNow car sharing
# 
# You are software engineer at **RentItNow**, a car sharing company located in SimpleTown.
# SimpleTown is a rounded village dived in three concentric circles: **Inner Circle**, **Middle Circle**, **Outer Circle**.
# 
# Your boss asks you to develop a new software to manage company's cars and users.
# The boss needs to:
# - Add, update and remove cars;
# - Check the status of the car: location, total distance traveled, next service time, availability.
# - Add, update and remove users;
# 
# A car has (at least)
# - a type, 
# - a license plate, 
# - a brand,
# - a name
# 
# There are three types of car: 
# - **ECO**, max 2 persons,
# - **MID-CLASS**, max 4 persons,
# - **DELUXE**, max 7 persons.
# 
# Each type of car has a rental price per km:
# - **ECO**: 1$/km;
# - **MID-CLASS**: 2$/km;
# - **DELUXE**: 5$/km
# 
# Each type of car has a fixed speed:
# - **ECO**: 15km/h
# - **MID-CLASS**: 25km/h
# - **DELUXE**: 50km/h
# 
# The company must **service** its cars every 1500km. Service takes 1 day and cost 300$. Car cannot be rented on that day.
# 
# A **user** can register to the company service, update its data and delete its account. User has (at least):
# - name, 
# - surname, 
# - address, 
# - credit card,
# - driving license
# 
# A user can ask for a car: select type of car, number of passengers, starting circle and destination circle. 
# 
# Travel distance is computed based on **hops**; an hop is 5km; an hops is going from one circle to the next one. **Always counts 1 hop for the starting circle**
# (e.g. travelling from Inner Circle to Middle Circle is 2 hops, not 1 hop). Travelling in the same circle is 1 hop.
# 
# The software select the best car for the user based on some metric (up to you), calculate the cost of the trip and make the payment.
# If no car is available, the software presents the user an expected waiting time. 
# 

# **Circle** class used to calculated the distance in kilometers between hops

# In[2]:


class Circle:
    def __init__(self, name):
        self.name = name

    def distance_to(self, other_circle):
        if self.name == other_circle.name:
            return 5  # 1 hop
        elif (self.name == "Inner Circle" and other_circle.name == "Middle Circle") or (self.name == "Middle Circle" and other_circle.name == "Inner Circle"):
            return 10  # 2 hops
        elif (self.name == "Middle Circle" and other_circle.name == "Outer Circle") or (self.name == "Outer Circle" and other_circle.name == "Middle Circle"):
            return 10  # 2 hops
        elif (self.name == "Inner Circle" and other_circle.name == "Outer Circle") or (self.name == "Outer Circle" and other_circle.name == "Inner Circle"):
            return 15  # 3 hops
        else:
            raise ValueError(f"Invalid circles for calculating distance: {self.name} and {other_circle.name}")


# **RentItNow** class where the users and cars are stored. All the methods to add, update and delete cars and users are here.
# 
# I also added a variable bank account to store the payments done by the users for their trip.
# 
# The method **find_best_car** filters the available cars with the specific type chosen by the user and then if at least one car is available it choses and returns the best car with the lowest calculated cost.
# 

# In[3]:


class RentItNow:
    def __init__(self):
        self.cars = []
        self.users = []
        self.circles = {
            "Inner Circle": Circle("Inner Circle"),
            "Middle Circle": Circle("Middle Circle"),
            "Outer Circle": Circle("Outer Circle"),
        }
        self.bank_account = 0
        
    def iterate_cars(self):
        for car in self.cars:
            yield car
            
    def get_last_saved_car_by_type(self, car_type: str):
        last_saved_car = None
        for car in reversed(self.cars):
            if car.type == car_type:
                last_saved_car = car
                break
        return last_saved_car
    
    def add_car(self, car):
        self.cars.append(car)

    def update_car(self, car):
        for idx, c in enumerate(self.cars):
            if c.license_plate == car.license_plate:
                self.cars[idx] = car
                break
    
    def remove_car(self, license_plate):
        self.cars = [car for car in self.cars if car.license_plate != license_plate]
    
    def iterate_users(self):
        for user in self.users:
            yield user
            
    def add_user(self, user):
        self.users.append(user)

    def update_user(self, user):
        for idx, u in enumerate(self.users):
            if u.driving_license == user.driving_license:
                self.users[idx] = user
                break

    def remove_user(self, driving_license):
        self.users = [user for user in self.users if user.driving_license != driving_license]

    def update_bank_account(self, amount):
        self.bank_account += amount

    def get_bank_account(self):
        return self.bank_account

    def find_best_car(self, car_type: str, num_passengers: int, start_circle, destination_circle):
        available_cars = [car for car in self.cars if car.availability and car.type == car_type]

        if not available_cars:
            return None

        best_car = min(available_cars, key=lambda car: car.calculate_cost(start_circle.distance_to(destination_circle)))

        return best_car


# The **Car** class stores all the informations related to a car and it also has the methods to: 
# 
# reserve a car,
# 
# calculate the travel time and cost of a car based on its type,
# 
# do the service of a car every 1500km.

# In[4]:


class Car:
    TYPE_PRICES = {
        "ECO": 1,
        "MID-CLASS": 2,
        "DELUXE": 5,
    }

    TYPE_SPEEDS = {
        "ECO": 15,
        "MID-CLASS": 25,
        "DELUXE": 50,
    }

    def __init__(self, car_type, license_plate, brand, name):
        self.type = car_type
        self.license_plate = license_plate
        self.brand = brand
        self.name = name
        self.total_distance = 0
        self.next_service_distance = 1500
        self.availability = True
        self.travel_time = 0
        self.serviced = False
    
    def calculate_cost(self, distance):
        return distance * self.TYPE_PRICES[self.type]

    def calculate_travel_time(self, distance):
        self.travel_time = distance / self.TYPE_SPEEDS[self.type]
        return distance / self.TYPE_SPEEDS[self.type]
        
    def get_travel_time(self):
        return self.travel_time
        
    def service(self, rent_it_now: RentItNow):
        self.next_service_distance = self.total_distance + 1500
        self.availability = False
        rent_it_now.update_bank_account(-300)
        self.serviced = True
        
    def reserve(self):
        self.availability = False

    def make_available(self):
        self.availability = True

    def set_total_distance(self, distance, rent_it_now: RentItNow):
        self.total_distance += distance
        if self.total_distance >= 1500 and self.total_distance % 1500 == 0:
            self.service(rent_it_now)
        
    def print_car_info(self):
        print(self.license_plate)
        print(self.type)
        print(f"Total Distance Traveled: {self.total_distance} km")
        print(f"Next Service at: {self.next_service_distance} km")
        print(f"Availability: {'Available' if self.availability else 'Not Available'}")
        print(f"Service: {'Done' if self.serviced else 'Not done'}")


# The **User** class stores all the information of a user and has the method **reserve_car** which assign to the user the best car if available using the method **find_best_car** described in the class **RentItNow**, if the car is not available it presents the expected waiting time based on the last rented car by type expected travel time, it then sets all the information of the rental and make the payment to **RentItNow** bank account and prints the information of the rental.

# In[5]:


import datetime
from typing import List, Optional

class User:
    def __init__(self, name, surname, address, credit_card, driving_license, selected_car_type: str, num_passengers: int, 
                 start_circle: str, destination_circle: str):
        self.name = name
        self.surname = surname
        self.address = address
        self.credit_card = credit_card
        self.driving_license = driving_license
        self.selected_car_type = selected_car_type
        self.num_passengers = num_passengers
        self.start_circle = Circle(start_circle)
        self.destination_circle = Circle(destination_circle)
        
    def reserve_car(self, rent_it_now: 'RentItNow'):
        best_car = rent_it_now.find_best_car(self.selected_car_type, self.num_passengers, self.start_circle, self.destination_circle)
        
        if not best_car:
            waiting_time = rent_it_now.get_last_saved_car_by_type(self.selected_car_type).get_travel_time()
            return f"No cars are available at the moment for {self.name} {self.surname}. The expected waiting time is {waiting_time} hours."
        
        total_distance = self.start_circle.distance_to(self.destination_circle)
        best_car.set_total_distance(total_distance, rent_it_now)
        travel_time = best_car.calculate_travel_time(total_distance)
        cost = best_car.calculate_cost(total_distance)

        best_car.reserve()

        rent_it_now.update_bank_account(cost)
        
        return f"Car {best_car.license_plate} has been reserved to {self.name} {self.surname}. The travel time is {travel_time} hours, and the cost is ${cost}."

    def print_user_info(self):
        print("Name:", self.name)
        print("Surname:", self.surname)
        print("Address:", self.address)
        print("Credit Card:", self.credit_card)
        print("Driving License:", self.driving_license)
        print("Selected Car Type:", self.selected_car_type)
        print("Number of Passengers:", self.num_passengers)


# The below **main** method is used to test the case where we have more users than cars so we should see that all the cars are rented and some users will need to wait. (see output below main method)

# In[9]:


def main():

    rent_it_now = RentItNow()

    eco_car = Car("ECO", "ECO123", "Tesla", "Model S")
    mid_class_car = Car("MID-CLASS", "MID456", "Toyota", "Camry")
    deluxe_car = Car("DELUXE", "DEL789", "Mercedes-Benz", "S-Class")
    suv_car = Car("MID-CLASS", "SUV101", "Ford", "Explorer")
    
    rent_it_now.add_car(eco_car)
    rent_it_now.add_car(mid_class_car)
    rent_it_now.add_car(deluxe_car)
    rent_it_now.add_car(suv_car)

    user1 = User("John", "Doe", "123 Main St", "4123-4567-8901-2345", "DL123456", "ECO", 2, "Inner Circle", "Outer Circle")
    user2 = User("Jane", "Doe", "456 Elm St", "1234-5678-9012-3456", "DL654321", "MID-CLASS", 4, "Middle Circle", "Outer Circle")
    user3 = User("Alice", "Smith", "789 Oak St", "9876-5432-1098-7654", "DL987654", "DELUXE", 6, "Outer Circle", "Inner Circle")
    user4 = User("Emily", "Johnson", "567 Pine St", "5678-9012-3456-7890", "DL135792", "ECO", 1, "Middle Circle", "Middle Circle")
    user5 = User("Michael", "Williams", "890 Cedar St", "7896-3452-9018-7456", "DL246813", "MID-CLASS", 3, "Inner Circle", "Inner Circle")
    user6 = User("Sophia", "Brown", "123 Oak St", "3214-8765-9102-6543", "DL975318", "DELUXE", 7,"Outer Circle", "Middle Circle")
    
    rent_it_now.add_user(user1)
    rent_it_now.add_user(user2)
    rent_it_now.add_user(user3)
    rent_it_now.add_user(user4)
    rent_it_now.add_user(user5)
    rent_it_now.add_user(user6)

    print(user1.reserve_car(rent_it_now))

    print(user2.reserve_car(rent_it_now))

    print(user3.reserve_car(rent_it_now))

    print(user4.reserve_car(rent_it_now))

    print(user5.reserve_car(rent_it_now))

    print(user6.reserve_car(rent_it_now))

    print("\nSaved cars info\n")
    for car in rent_it_now.iterate_cars():
        car.print_car_info()
        print("\n")

    print(f"bank account balance of RentItNow:  {rent_it_now.get_bank_account()} " )

if __name__ == "__main__":
    main()


# 
# 
# The below **main** method is used to test the case where we have more cars than users so we should see that all the users get a car and some cars remain available. (see output below main method)

# In[13]:


def main():

    rent_it_now = RentItNow()

    eco_car = Car("ECO", "ECO123", "Tesla", "Model S")
    mid_class_car = Car("MID-CLASS", "MID456", "Toyota", "Camry")
    deluxe_car = Car("DELUXE", "DEL789", "Mercedes-Benz", "S-Class")
    suv_car = Car("MID-CLASS", "SUV101", "Ford", "Explorer")
    compact_car = Car("ECO", "CMP202", "Honda", "Civic")
    luxury_car = Car("DELUXE", "LUX303", "BMW", "7 Series")
    
    rent_it_now.add_car(eco_car)
    rent_it_now.add_car(mid_class_car)
    rent_it_now.add_car(deluxe_car)
    rent_it_now.add_car(suv_car)
    rent_it_now.add_car(compact_car)
    rent_it_now.add_car(luxury_car)
    
    user1 = User("John", "Doe", "123 Main St", "4123-4567-8901-2345", "DL123456", "ECO", 2, "Inner Circle", "Outer Circle")
    user2 = User("Jane", "Doe", "456 Elm St", "1234-5678-9012-3456", "DL654321", "MID-CLASS", 4, "Middle Circle", "Outer Circle" )
    user3 = User("Alice", "Smith", "789 Oak St", "9876-5432-1098-7654", "DL987654", "DELUXE", 6, "Inner Circle", "Outer Circle")
    user4 = User("Emily", "Johnson", "567 Pine St", "5678-9012-3456-7890", "DL135792", "ECO", 1, "Middle Circle", "Middle Circle" )
    
    rent_it_now.add_user(user1)
    rent_it_now.add_user(user2)
    rent_it_now.add_user(user3)
    rent_it_now.add_user(user4)

    print(user1.reserve_car(rent_it_now))

    print(user2.reserve_car(rent_it_now))

    print(user3.reserve_car(rent_it_now))

    print(user4.reserve_car(rent_it_now))


    print("\nSaved cars info\n")
    for car in rent_it_now.iterate_cars():
        car.print_car_info()
        print("\n")

    print(f"bank account balance of RentItNow:  {rent_it_now.get_bank_account()} " )
    
if __name__ == "__main__":
    main()


# The below **main** method is used to test the case where we have the same number of users and cars more users than cars so we should see that all the cars are rented. (see output below main method)

# In[10]:


def main():

    rent_it_now = RentItNow()

    eco_car = Car("ECO", "ECO123", "Tesla", "Model S")
    mid_class_car = Car("MID-CLASS", "MID456", "Toyota", "Camry")
    deluxe_car = Car("DELUXE", "DEL789", "Mercedes-Benz", "S-Class")
    suv_car = Car("MID-CLASS", "SUV101", "Ford", "Explorer")
    compact_car = Car("ECO", "CMP202", "Honda", "Civic")
    luxury_car = Car("DELUXE", "LUX303", "BMW", "7 Series")
    
    rent_it_now.add_car(eco_car)
    rent_it_now.add_car(mid_class_car)
    rent_it_now.add_car(deluxe_car)
    rent_it_now.add_car(suv_car)
    rent_it_now.add_car(compact_car)
    rent_it_now.add_car(luxury_car)
    
    user1 = User("John", "Doe", "123 Main St", "4123-4567-8901-2345", "DL123456", "ECO", 2, "Inner Circle", "Outer Circle")
    user2 = User("Jane", "Doe", "456 Elm St", "1234-5678-9012-3456", "DL654321", "MID-CLASS", 4, "Middle Circle", "Outer Circle" )
    user3 = User("Alice", "Smith", "789 Oak St", "9876-5432-1098-7654", "DL987654", "DELUXE", 6, "Inner Circle", "Outer Circle")
    user4 = User("Emily", "Johnson", "567 Pine St", "5678-9012-3456-7890", "DL135792", "ECO", 1, "Middle Circle", "Middle Circle" )
    user5 = User("Michael", "Williams", "890 Cedar St", "7896-3452-9018-7456", "DL246813", "MID-CLASS", 3, "Inner Circle", "Inner Circle")
    user6 = User("Sophia", "Brown", "123 Oak St", "3214-8765-9102-6543", "DL975318", "DELUXE", 7, "Middle Circle", "Outer Circle")
    
    rent_it_now.add_user(user1)
    rent_it_now.add_user(user2)
    rent_it_now.add_user(user3)
    rent_it_now.add_user(user4)
    rent_it_now.add_user(user5)
    rent_it_now.add_user(user6)

    print(user1.reserve_car(rent_it_now))

    print(user2.reserve_car(rent_it_now))

    print(user3.reserve_car(rent_it_now))

    print(user4.reserve_car(rent_it_now))

    print(user5.reserve_car(rent_it_now))

    print(user6.reserve_car(rent_it_now))

    print("\nSaved cars info\n")
    for car in rent_it_now.iterate_cars():
        car.print_car_info()
        print("\n")

    print(f"bank account balance:  {rent_it_now.get_bank_account()} $" )
    
if __name__ == "__main__":
    main()


# The below **main** method uses the same number of users and cars and present the test for 2 rounds of rental

# In[6]:


def main():

    rent_it_now = RentItNow()

    eco_car = Car("ECO", "ECO123", "Tesla", "Model S")
    mid_class_car = Car("MID-CLASS", "MID456", "Toyota", "Camry")
    deluxe_car = Car("DELUXE", "DEL789", "Mercedes-Benz", "S-Class")
    suv_car = Car("MID-CLASS", "SUV101", "Ford", "Explorer")
    compact_car = Car("ECO", "CMP202", "Honda", "Civic")
    luxury_car = Car("DELUXE", "LUX303", "BMW", "7 Series")
    
    rent_it_now.add_car(eco_car)
    rent_it_now.add_car(mid_class_car)
    rent_it_now.add_car(deluxe_car)
    rent_it_now.add_car(suv_car)
    rent_it_now.add_car(compact_car)
    rent_it_now.add_car(luxury_car)
    
    user1 = User("John", "Doe", "123 Main St", "4123-4567-8901-2345", "DL123456", "ECO", 2, "Inner Circle", "Outer Circle")
    user2 = User("Jane", "Doe", "456 Elm St", "1234-5678-9012-3456", "DL654321", "MID-CLASS", 4, "Middle Circle", "Outer Circle" )
    user3 = User("Alice", "Smith", "789 Oak St", "9876-5432-1098-7654", "DL987654", "DELUXE", 6, "Inner Circle", "Outer Circle")
    user4 = User("Emily", "Johnson", "567 Pine St", "5678-9012-3456-7890", "DL135792", "ECO", 1, "Middle Circle", "Middle Circle" )
    user5 = User("Michael", "Williams", "890 Cedar St", "7896-3452-9018-7456", "DL246813", "MID-CLASS", 3, "Inner Circle", "Inner Circle")
    user6 = User("Sophia", "Brown", "123 Oak St", "3214-8765-9102-6543", "DL975318", "DELUXE", 7, "Middle Circle", "Outer Circle")
    
    rent_it_now.add_user(user1)
    rent_it_now.add_user(user2)
    rent_it_now.add_user(user3)
    rent_it_now.add_user(user4)
    rent_it_now.add_user(user5)
    rent_it_now.add_user(user6)

    print(user1.reserve_car(rent_it_now))

    print(user2.reserve_car(rent_it_now))

    print(user3.reserve_car(rent_it_now))

    print(user4.reserve_car(rent_it_now))

    print(user5.reserve_car(rent_it_now))

    print(user6.reserve_car(rent_it_now))

    print("\nSaved cars info\n")
    for car in rent_it_now.iterate_cars():
        car.print_car_info()
        print("\n")

    print(f"bank account balance:  {rent_it_now.get_bank_account()} $" )

    eco_car.make_available()
    mid_class_car.make_available()
    deluxe_car.make_available()
    suv_car.make_available()
    compact_car.make_available()
    luxury_car.make_available()
    
    print(user4.reserve_car(rent_it_now))
    print(user5.reserve_car(rent_it_now))
    print(user6.reserve_car(rent_it_now))
    print(user1.reserve_car(rent_it_now))
    print(user2.reserve_car(rent_it_now))
    print(user3.reserve_car(rent_it_now))

    print("\nSaved cars info\n")
    for car in rent_it_now.iterate_cars():
        car.print_car_info()
        print("\n")

    print(f"bank account balance:  {rent_it_now.get_bank_account()} $" )
    
if __name__ == "__main__":
    main()


# The below **main** method is used to test the add, update and delete functions related to cars

# In[7]:


def main():

    rent_it_now = RentItNow()

    eco_car = Car("ECO", "ECO123", "Tesla", "Model S")
    mid_class_car = Car("MID-CLASS", "MID456", "Toyota", "Camry")
    deluxe_car = Car("DELUXE", "DEL789", "Mercedes-Benz", "S-Class")
    suv_car = Car("MID-CLASS", "SUV101", "Ford", "Explorer")
    compact_car = Car("ECO", "CMP202", "Honda", "Civic")
    luxury_car = Car("DELUXE", "LUX303", "BMW", "7 Series")
    
    rent_it_now.add_car(eco_car)
    rent_it_now.add_car(mid_class_car)
    rent_it_now.add_car(deluxe_car)
    rent_it_now.add_car(suv_car)
    rent_it_now.add_car(compact_car)
    rent_it_now.add_car(luxury_car)

    print("Car list before modification\n")
    for car in rent_it_now.iterate_cars():
        car.print_car_info()
        print("\n")

    rent_it_now.remove_car("SUV101")
    rent_it_now.update_car(Car("MID-CLASS", "CMP202", "Honda", "Civic"))

    print("Car list after SUV101 deleted and CMP202 type change\n")
    for car in rent_it_now.iterate_cars():
        car.print_car_info()
        print("\n")
    
if __name__ == "__main__":
    main()


# The below **main** method is used to test the add, update and delete functions related to users

# In[8]:


def main():

    rent_it_now = RentItNow()
    
    user1 = User("John", "Doe", "123 Main St", "4123-4567-8901-2345", "DL123456", "ECO", 2, "Inner Circle", "Outer Circle")
    user2 = User("Jane", "Doe", "456 Elm St", "1234-5678-9012-3456", "DL654321", "MID-CLASS", 4, "Middle Circle", "Outer Circle" )
    user3 = User("Alice", "Smith", "789 Oak St", "9876-5432-1098-7654", "DL987654", "DELUXE", 6, "Inner Circle", "Outer Circle")
    user4 = User("Emily", "Johnson", "567 Pine St", "5678-9012-3456-7890", "DL135792", "ECO", 1, "Middle Circle", "Middle Circle" )
    user5 = User("Michael", "Williams", "890 Cedar St", "7896-3452-9018-7456", "DL246813", "MID-CLASS", 3, "Inner Circle", "Inner Circle")
    user6 = User("Sophia", "Brown", "123 Oak St", "3214-8765-9102-6543", "DL975318", "DELUXE", 7, "Middle Circle", "Outer Circle")
    
    rent_it_now.add_user(user1)
    rent_it_now.add_user(user2)
    rent_it_now.add_user(user3)
    rent_it_now.add_user(user4)
    rent_it_now.add_user(user5)
    rent_it_now.add_user(user6)

    print("Users list before modification\n")
    for car in rent_it_now.iterate_users():
        car.print_user_info()
        print("\n")

    rent_it_now.remove_user("DL987654")
    rent_it_now.update_user(User("Jane", "Doe", "456 Elm St", "3456-9012-5678-1245", "DL654321", "DELUXE", 5, "Middle Circle", "Middle Circle" ))

    print("Users list after Alice Smith (DL987654) deleted and Jane Doe (DL654321) updated\n")
    for car in rent_it_now.iterate_users():
        car.print_user_info()
        print("\n")
    
if __name__ == "__main__":
    main()


# To test the **service** method of the class **Car** as it triggers every 1500km we can increment the distance between the hops in the class **Circle**

# In[ ]:


class CircleTest:
    def __init__(self, name):
        self.name = name

    def distance_to(self, other_circle):
        if self.name == other_circle.name:
            return 500  # 1 hop
        elif (self.name == "Inner Circle" and other_circle.name == "Middle Circle") or (self.name == "Middle Circle" and other_circle.name == "Inner Circle"):
            return 1000  # 2 hops
        elif (self.name == "Middle Circle" and other_circle.name == "Outer Circle") or (self.name == "Outer Circle" and other_circle.name == "Middle Circle"):
            return 1000  # 2 hops
        elif (self.name == "Inner Circle" and other_circle.name == "Outer Circle") or (self.name == "Outer Circle" and other_circle.name == "Inner Circle"):
            return 1500  # 3 hops
        else:
            raise ValueError(f"Invalid circles for calculating distance: {self.name} and {other_circle.name}")


# Below the output of the **main** method with same number of cars and user using the above class **CircleTest** to calculate distances

# Car ECO123 has been reserved to John Doe. The travel time is 100.0 hours, and the cost is 1500$.
# 
# Car MID456 has been reserved to Jane Doe. The travel time is 40.0 hours, and the cost is 2000$.
# 
# Car DEL789 has been reserved to Alice Smith. The travel time is 30.0 hours, and the cost is 7500$.
# 
# Car CMP202 has been reserved to Emily Johnson. The travel time is 33.333333333333336 hours, and the cost is 500$.
# 
# Car SUV101 has been reserved to Michael Williams. The travel time is 20.0 hours, and the cost is 1000$.
# 
# Car LUX303 has been reserved to Sophia Brown. The travel time is 20.0 hours, and the cost is 5000$.
# 
# Saved cars info
# 
# ECO123
# ECO
# Total Distance Traveled: 1500 km
# Next Service at: 3000 km
# Availability: Not Available
# Service: Done
# 
# 
# MID456
# MID-CLASS
# Total Distance Traveled: 1000 km
# Next Service at: 1500 km
# Availability: Not Available
# Service: Not done
# 
# 
# DEL789
# DELUXE
# Total Distance Traveled: 1500 km
# Next Service at: 3000 km
# Availability: Not Available
# Service: Done
# 
# 
# SUV101
# MID-CLASS
# Total Distance Traveled: 500 km
# Next Service at: 1500 km
# Availability: Not Available
# Service: Not done
# 
# 
# CMP202
# ECO
# Total Distance Traveled: 500 km
# Next Service at: 1500 km
# Availability: Not Available
# Service: Not done
# 
# 
# LUX303
# DELUXE
# Total Distance Traveled: 1000 km
# Next Service at: 1500 km
# Availability: Not Available
# Service: Not done
# 
# 
# bank account balance:  16900

# In[ ]:




