#!/usr/bin/python3

from map import rooms
from player import *
from items import *
from gameparser import *
from enemy import *
import random
import sys

global type_attack

type_attack = ["Slash", "Fire"]
def list_of_items(items):
    return ", ".join(i["name"] for i in items) 
         

def print_room_items(room):
       if len(room["items"]) != 0: 
        print("There is " + str(list_of_items(room["items"]) + " here."))  
        print("") 
def print_inventory_items(items):
    print("You have " + str(list_of_items(items)) + ".") 
    print("") 
def yes_or_no(question):
    reply = str(input(question+' (f/r): ')).lower().strip()
    if reply[0] == 'f':
        return True
    if reply[0] == 'r':
        return False
    else:
        return yes_or_no("please enter f/r")

def print_enemies(enemies):
    global current_room
    global prev_room
    x = [] 
    for enemy_ in enemies:
        x.append(enemy_["name"])
        
    print("There is " + str(x) + " here.")
    question = "Run or Fight?"
    if yes_or_no(question) == False:
        current_room = prev_room
        main()
    else:
        return True 
## plans to make it so that a room can regen enemies if your coming back to it       
def print_room(room):
    # Display room name
    print("")
    print(room["name"].upper())
    print("")
    # Display room description
    print(room["description"])
    print("")
    
    if len(room["items"]) != 0: 
        print_room_items(room) 


def print_arena(enemies):
    for current in enemies:
        print(current["name"] + ":" + str(current["temp_hp"]))
def exit_leads_to(exits, direction):
    return rooms[exits[direction]]["name"]


def print_exit(direction, leads_to):
    print("GO " + direction.upper() + " to " + leads_to + ".")


def print_menu(exits, room_items, inv_items, room_market):
    print("You can:")
    # Iterate over available exits
    for direction in exits:
        # Print the exit name and where it leads to
        print_exit(direction, exit_leads_to(exits, direction))

    for i in room_market:
        print("BUY " + str(i["id"]).upper() + " to buy " + str(i["name"])) 
    for i in room_items: 
        print("TAKE " + str(i["id"]).upper() + " to take " + str(i["name"]) + ".")

    if len(current_room["market"]) > 0:
        for i in inv_items:
            print("SELL " + str(i["id"]).upper() + " to sell " + str(i["name"]) + ".") 
    for i in inv_items: 
        print("DROP " + str(i["id"]).upper() + " to drop " + str(i["name"]) + ".")    
    print("What do you want to do?")

def print_combat_menu(inventory, enemies):
    print("You can: ")
    item = []  
    for i in inventory:
        if str(i["type"]) in type_attack:
            item.append(i["id"])
        
    for enemy_ in enemies:
        print("ATTACK " + str(enemy_["id"]).upper() + " with " + str(', '.join(item)).upper() + ".")
    for i in inventory:
        if i["type"] == "Heal":
            print("USE " + str(i["id"]).upper() + " to heal for " + str(i["hp"]) + ".")
    print("What do you want to do?")
    
def is_valid_exit(exits, chosen_exit):
    return chosen_exit in exits.keys()

def execute_buy(item_id):
    global gold 
    
    for item in current_room["market"]:
        if item_id == item["id"]:
            if gold > item["cost"]:
                inventory.append(item)
                current_room["market"].remove(item)
                gold = gold - item["cost"]
                print("you have bought " + str(item["name"]))
                print("you have " + str(gold) + " gold")  
                break
            else:
                print("You don't have enough gold mate")
            
def execute_sell(item_id):
    global gold 
    
    for item in inventory:
        if item_id == item["id"]: 
            inventory.remove(item)
            gold = gold + int((0.5*int(item["cost"]))) 
            current_room["market"].append(item)
            print("you have sold " + str(item["name"]) + " you have gained, " + str(int(0.5*item["cost"]))) 
            print("you have " + str(gold) + " gold")
            break
        else: 
            print("You cannot sell that")        
                 
def execute_go(direction):
    global current_room
    global prev_room
    prev_room = current_room 
    if is_valid_exit(current_room["exits"], direction) == True: 
        current_room = move(current_room["exits"], direction)
        if len(current_room["check_item"]) > 0 and current_room["check_item"] not in inventory:
            current_room = prev_room
            print("You cannot enter here yet, there must be something you need")
        else: 
            print("moving into " + str(current_room["name"])) 
    else: 
        print("You cannot go there")  
     

def execute_take(item_id):
    for item in current_room["items"]: 
        if item_id == item["id"]: 
            inventory.append(item) 
            current_room["items"].remove(item) 
            print("you have taken " + str(item["name"]))
            break   
        else: 
            print("You cannot take that.") 
        
    

def execute_drop(item_id):
    for item in inventory:
        if item_id == item["id"]: 
            inventory.remove(item)
            current_room["items"].append(item)
            print("you have dropped " + str(item["name"])) 
            break
        else: 
            print("You cannot drop that")        

def execute_attack(enemy_, item_id):
    global enemies 
    for item in inventory:
        if item_id == item["id"]:
            if str(item["type"]) in type_attack:
                for enemyx in enemies:
                    if enemy_ == enemyx["id"]:
                        
                        if item["type"] == enemyx["weak"]:
                            enemyx["temp_hp"] = enemyx["temp_hp"] - int((2 * item["attack"]))
                            print("that was super effective!")
                            print(enemyx["name"] + " has " + str(enemyx["temp_hp"]) + " hp")
                            break
                        elif item["type"] == enemyx["resist"]: 
                            enemyx["temp_hp"] = enemyx["temp_hp"] - int((0.5 * item["attack"]))
                            print("that wasn't very effective...")
                            print(enemyx["name"] + " has " + str(enemyx["temp_hp"]) + " hp")
                            break
                        else: 
                            enemyx["temp_hp"] = enemyx["temp_hp"] -  item["attack"]
                            print(enemyx["name"] + " has " + str(enemyx["temp_hp"]) + " hp")
                            break
        else:
            print("You cannot attack with that")

def execute_use(item_id):
    global hp 

    for item in inventory:
        if item_id == item["id"]:
            if item["type"] == "Heal":
                hp = hp + item["hp"]
                print("hp: " + str(hp))
                break
            else:
                print("You cannot use that item") 
def execute_command(command):

    if 0 == len(command):
        return

    if command[0] == "go":
        if len(command) > 1:
            execute_go(command[1])
        else:
            print("Go where?")

    elif command[0] == "take":
        if len(command) > 1:
            execute_take(command[1])
        else:
            print("Take what?")
    elif command[0] == "buy":
        if len(command) > 1:
            execute_buy(command[1])
        else:
            print("Buy what?") 
    elif command[0] == "sell":
        if len(command) > 1:
            execute_sell(command[1])
        else:
            print("Sell what?") 
    elif command[0] == "drop":
        if len(command) > 1:
            execute_drop(command[1])
        else:
            print("Drop what?")

    else:
        print("This makes no sense.")

def execute_combat_command(command):
    if 0 == len(command):
        return
    if command[0] == "attack":
        if len(command)> 2:
            execute_attack(command[1], command[2])
        else:
            print("Attack what?")
    elif command[0] == "use":
        if len(command)> 1:
            execute_use(command[1])
        else:
            print("Use what?")
    else:
        print("This makes no sense.") 

def menu(exits, room_items, inv_items, room_market):

    # Display menu
    print_menu(exits, room_items, inv_items, room_market)

    # Read player's input
    user_input = input("> ")

    # Normalise the input
    normalised_user_input = normalise_input(user_input)

    return normalised_user_input


def move(exits, direction):
    
    # Next room to go to 
    return rooms[exits[direction]]
def combat_menu(inventory, enemies):
    print_combat_menu(inventory, enemies)

    user_input = input("> ")

    normalised_user_input = normalise_input(user_input)

    return normalised_user_input 
    
def combat():
    global current_room 
    if current_room["combat"] == True:
        global enemies
        enemies = []
        for x in range(1, current_room["max enemy"]):
            temp_enemy = random.choice(current_room["enemy"])
            if temp_enemy != None:
                if temp_enemy not in enemies:
                    enemies.append(temp_enemy)
        if print_enemies(enemies) == True:
            while True:
                print_arena(enemies)
                
                command = combat_menu(inventory, enemies)
                #print(command) 
                execute_combat_command(command)

                for enemy_ in enemies:
                    if enemy_["temp_hp"] < 1:
                        print("You killed 1 " + enemy_["name"])
                        enemy_["temp_hp"] = enemy_["hp"] 
                        enemies.remove(enemy_)
                if len(enemies) == 0:
                    current_room["combat"] = False
                    break
    else:
        return None
                    
        
        
# This is the entry point of our program
def main():
    global prev_room
        
    # Main game loop
    while True:
        # Display game status (room description, inventory etc.)
        print_room(current_room)
        print_inventory_items(inventory)

        combat()

        # Show the menu with possible actions and ask the player
        command = menu(current_room["exits"], current_room["items"], inventory, current_room["market"])

        # Execute the player's command
        execute_command(command)

if __name__ == "__main__":
    main() 
    
