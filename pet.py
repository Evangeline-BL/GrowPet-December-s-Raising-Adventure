import json
import random
import os
from datetime import datetime

dog_name = "December"
save_file = "pet_save_en.json"
log_file = "pet_log_en.txt"

FOODS = {
    "dog food":     {"affection": 10, "growth": 5, "health": 5, "msg":"Yum! December wags her tail."},
    "beef":         {"affection": 15, "growth": 10, "health": 10, "msg":"Delicious! December is delighted."},
    "carrot":       {"affection": 3, "growth": 2, "health": 7, "msg":"crunch! December enjoyed the carrot."},
    "bone":         {"affection": 12, "growth": 7, "health": 0, "msg":"December buries the bone for later."},
    "chicken":        {"affection": 7, "growth": 3, "health": 3, "msg":"December likes the chicken!"},
    "chocolate":    {"affection": -20, "growth": 0, "health": -40, "msg":"Uh-oh! Chocolate is toxic to dogs!"},
    "garlic":        {"affection": -5, "growth": 0, "health": -8, "msg":"Smelly! December doesn't like that."}
}

ACTIONS = {
    "pet":         {"affection": 10, "growth": 0, "health": 0, "msg":"december closes her eyes and smiles."},
    "walk":        {"affection": 7,  "growth": 5, "health": 7, "msg":"december loves the walk!"},
    "play fetch":  {"affection": 10, "growth": 4, "health": 5, "msg":"december plays fetch with you!"},
    "bath":        {"affection": 2,  "growth": 0, "health": 8, "msg":"Squeaky clean! december looks shiny."},
    "vet":         {"affection": -2, "growth": 0, "health": 20, "msg":"december looks nervous, but feels better after the check!"}
}

STAGES = [
    {"name": "Puppy",      "min_growth": 0,   "art": """\
  /^ ^\\ 
 / o o \\ 
 V\\ Y /V 
  / - \\
  |    \\
 || (__V
A tiny puppy wags her little tail.""", "sick_art": "december is lying down, shivering sadly."},

{"name": "Junior",     "min_growth": 25,  "art": """\
  /^ ^\\ 
 / o o \\ 
 V\\ Y /V 
  / --\\ 
  |    \\
 ||(__V
december is bouncy and playful!""", "sick_art": "december looks tired and weak."},

{"name": "Young Dog",  "min_growth": 55,  "art": """\
   /^ ^\\ 
  / o o \\ 
 V\\  Y  /V 
  / --- \\
  |     \\
 ||    (__V
december is growing fast and looks healthy!""", "sick_art":"december has dull fur and sad eyes."},

{"name": "Adult",  "min_growth": 90,  "art": """\
   /^  ^\\
  / ^  ^\\
 V\\ O  O /V
  /--O--\\
  |      \\
 ||     (__V
december is now a strong and loyal companion.""", "sick_art":"december refuses to get out of bed."},

{"name": "Legendary",  "min_growth": 140, "art": """\
   /^  ^\\
  / ^  ^\\
 V\\ ^  ^ /V
  /----\\
  |    \\
||     (__V
december glows with legendary energy and joy!""", "sick_art":"A weak spark glimmers in december's eyes as she struggles."}
]


class Pet:
    def __init__(self, name=dog_name, affection=50, growth=0, health=90, sick=False, history=None):
        self.name = name
        self.affection = affection
        self.growth = growth
        self.health = health  # 0~120
        self.sick = sick
        self.history = history if history else []

    def feed(self, food):
        effect = FOODS.get(food.lower())
        if not effect:
            return False, "december tilts her head in confusion. What is this?"
        
        self.affection += effect['affection']
        self.growth += effect['growth']
        self.health += effect['health']

        self.log_event(f"Fed {food}: Affection {effect['affection']} Growth {effect['growth']} Health {effect['health']}")
        if effect['health'] < 0:
            self.sick = True
            sick_msg = effect['msg'] + " december feels sick!"
            return True, sick_msg
        if self.health < 40:
            self.sick = True
        elif self.health >= 60:
            self.sick = False
        return True, effect['msg']

    def act(self, act):
        effect = ACTIONS.get(act.lower())
        if not effect:
            return False, "december doesn't understand this action."
        if self.sick and act.lower() != "vet":
            return False, "december is too sick to do this. Maybe visit the vet?"

        self.affection += effect['affection']
        self.growth += effect['growth']
        self.health += effect['health']

        self.log_event(f"Did {act}: Affection {effect['affection']} Growth {effect['growth']} Health {effect['health']}")
        if act.lower() == "vet":
            if self.sick:
                self.sick = False
                return True, "december went to the vet and is feeling MUCH better now!"
            else:
                return True, effect['msg'] + " (But she's not sick, just a little nervous!)"

        return True, effect['msg']

    def get_stage(self):
        stage = STAGES[0]
        for s in STAGES:
            if self.growth >= s['min_growth']:
                stage = s
        return stage
    
    def reaction(self):
        if self.health <= 0:
            return "Critical! december has collapsed! Go to the vet immediately!"
        if self.sick:
            return "december looks sick and doesn't want to play or eat anything."
        if self.affection > 120:
            return "december leaps into your arms, barking with endless joy and love!"
        elif self.affection > 80:
            return "december is incredibly close to you, always by your side."
        elif self.affection > 50:
            return "december is friendly and happy to see you."
        elif self.affection > 25:
            return "december looks at you, still a bit shy."
        else:
            return "december keeps her distance, but maybe more care will help..."

    def ascii_art(self):
        stage = self.get_stage()
        if self.sick or self.health < 40:
            return stage['sick_art']
        else:
            return stage['art']

    def trim_state(self):
        self.affection = max(0, min(self.affection, 150))
        self.growth = max(0, min(self.growth, 200))
        self.health = max(0, min(self.health, 120))
        if self.health < 40:
            self.sick = True
        
    def save(self):
        self.trim_state()
        with open(save_file, "w", encoding="utf-8") as f:
            json.dump({
                "affection": self.affection,
                "growth": self.growth,
                "health": self.health,
                "sick": self.sick,
                "history": self.history
            }, f, indent=2)
        print("Game progress saved.")
    
    def log_event(self, msg):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"{now} | {msg}"
        self.history.append(log_msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")

    def summary(self):
        stage = self.get_stage()
        return (f"\n===== {self.name}'s Current State =====\n"
                f"{self.ascii_art()}\n"
                f"Stage: {stage['name']}\n"
                f"Affection: {self.affection}/150   Growth: {self.growth}/200   Health: {self.health}/120\n"
                f"Sick: {'Yes' if self.sick else 'No'}\n"
                f"{self.reaction()}\n")
def load_pet():
    if os.path.exists(save_file):
        with open(save_file, "r", encoding="utf-8") as f:
            d = json.load(f)
            pet = Pet(dog_name, d["affection"], d["growth"], d["health"], d["sick"], d["history"])
            pet.trim_state()
            return pet
    return Pet(dog_name)

def main():
    print(f"🐾 Welcome to GrowPet: december's Raising Adventure!")
    pet = None
    if os.path.exists(save_file):
        print("Found a saved pet file. Load saved dog? (y/n)")
        if input("> ").strip().lower() == 'y':
            pet = load_pet()
            print("Save loaded. Let's keep raising december!")
        else:
            pet = Pet(dog_name)
    else:
        pet = Pet(dog_name)
    
    try:
        while True:
            pet.trim_state()
            print(pet.summary())
            print("What would you like to do?")
            print(" 1. Feed december")
            print(" 2. Interact with december")
            print(" 3. View growth log")
            print(" 4. Save game")
            print(" 5. Reset game (new puppy)")
            print(" 6. Quit\n")

            cmd = input("Enter your choice (1-6): ").strip()
            if cmd not in ['1', '2', '3', '4', '5', '6']:
                print("Invalid input. Please enter a number from 1 to 6.")
                continue


            if cmd == '1':
                print("\nWhat food will you give? (type name exactly; 'q' to cancel)")
                for fname, stat in FOODS.items():
                    print(f"  - {fname.capitalize()} (+Affection:{stat['affection']} Growth:{stat['growth']} Health:{stat['health']})")
                while True:
                    sel = input("> ").strip().lower()
                    if sel == "q":
                        break
                    success, msg = pet.feed(sel)
                    print(msg)
                    if success:
                        break
                    else:
                        print("Invalid food. Please try again or type 'q' to cancel.")
                    
            elif cmd == "2":
                print("\nHow will you interact? Options:")
                for act, st in ACTIONS.items():
                    print(f"  - {act.capitalize()} (+Affection:{st['affection']} Growth:{st['growth']} Health:{st['health']})")
                print("Type the action; or type 'q' to go back.")
                while True:
                    sel = input("> ").strip().lower()
                    if sel == "q":
                        break
                    success, msg = pet.act(sel)
                    print(msg)
                    if success:
                    # random event: playing fetch may bring bonus
                        if sel == "play fetch" and random.random() < 0.2:
                            bonus = random.randint(4, 12)
                            pet.affection += bonus
                            pet.log_event(f"Random Event: december brings you a special stick! +{bonus} Affection!")
                            print(f"Special! december brought you a stick out of excitement! Affection +{bonus}")
                        break
                    else:
                        print("Invalid or unavailable action. Please try again or type 'q'.")
        
            elif cmd == '3':
                print("\n--- Last 10 Growth Events ---")
                for line in pet.history[-10:]:
                    print(line)
                print("------------------------------\n")

            elif cmd == '4':
                pet.save()

            elif cmd == '5':
                check = input("Resetting will erase all progress. Are you sure? (y/n): ")
                if check.strip().lower() == 'y':
                    pet = Pet(dog_name)
                    if os.path.exists(save_file): os.remove(save_file)
                    print("New puppy december is here!")

            elif cmd == '6':
                pet.save()
                print("Thanks for taking care of december! See you next time!")
                break
        
    except KeyboardInterrupt:
        print("Invalid input. Please enter a number from 1 to 6.")
        print("Detected keyboard interrupt. Saving progress...")
        pet.save()
        print("Progress saved. Goodbye!")


if __name__ == "__main__":
    main()
