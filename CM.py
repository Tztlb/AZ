import random
import threading
from Agent import Agent
from collections import defaultdict


class ConversationMonitor:
    def __init__(self, agents):
        self.agents = agents
        self.relationship_strength = 0.5
        self.relationships = {
            agent.name: {other.name: self.relationship_strength for other in agents if other != agent}
            for agent in agents
        }  # Initialize with a default value
        self.lock = threading.Lock()
        self.mood_history = []
        self.relationship_history = []  # ← این خط اضافه شود

    def update_relationship(self, speaker, mood):
        with self.lock:
            if speaker not in self.relationships:
                print(f"[ERROR] Speaker '{speaker}' not found in relationships dictionary.")
                return

            valid_moods = ["happy", "excited", "neutral", "frustrated", "angry" , "nervous"]
            if mood not in valid_moods:
                print(f"[ERROR] Invalid mood: {mood}")
                return

            for listener in self.agents:
                if listener.name == speaker:
                    continue

                # تغییر قدرت رابطه بر اساس مود
                if mood in ["happy", "excited"]:
                    change = 0.05  # افزایش آرام رابطه
                elif mood in ["frustrated" , "nervous"]:
                    change = -0.03  # کاهش متوسط
                elif mood in ["angry"]:
                    change = -0.07  # کاهش شدید
                else:
                    change = 0  # مود خنثی تغییری ایجاد نمی‌کند

                # مقداردهی اولیه اگر مقدار وجود نداشته باشد
                if listener.name not in self.relationships[speaker]:
                    self.relationships[speaker][listener.name] = 0.5  # مقدار پیش‌فرض

                if speaker not in self.relationships[listener.name]:
                    self.relationships[listener.name][speaker] = 0.5  # مقدار پیش‌فرض

                # تغییر مقدار رابطه
                self.relationships[speaker][listener.name] = min(1.0, max(0.0, self.relationships[speaker][listener.name] + change))
                self.relationships[listener.name][speaker] = min(1.0, max(0.0, self.relationships[listener.name][speaker] + change))

                print(f"[INFO] Relationship Updated: {speaker} → {listener.name} = {self.relationships[speaker][listener.name]}")



    def determine_groups(self):
        groups = []
        agent_groups = defaultdict(set)  
        max_groups_per_agent = 2  
        min_relationship_strength = 0.5  

        def is_fully_connected(group, new_member):
            return all(self.relationships[new_member].get(member, 0) >= min_relationship_strength for member in group)

        def find_groups(agent_name):
            possible_groups = []
            for group in groups:
                if is_fully_connected(group, agent_name) and len(agent_groups[agent_name]) < max_groups_per_agent:
                    possible_groups.append(group)
            return possible_groups

        for agent in self.agents:
            possible_groups = find_groups(agent.name)

            if possible_groups:
                for group in possible_groups:
                    if random.random() < 0.7:  
                        group.add(agent.name)
                        agent_groups[agent.name].add(tuple(group))  
            else:
                new_group = {agent.name}
                for friend, strength in self.relationships[agent.name].items():
                    if strength > min_relationship_strength and len(agent_groups[friend]) < max_groups_per_agent:
                        new_group.add(friend)
                        agent_groups[friend].add(friend)  

                if len(new_group) < len(self.agents):  
                    groups.append(new_group)
                    agent_groups[agent.name].add(agent.name)  

        # **حذف گروه‌هایی که قدرت رابطه‌ی بین اعضا ضعیف شده است**
        valid_groups = []
        for group in groups:
            all_valid = all(
                self.relationships[member1].get(member2, 0) >= min_relationship_strength
                for member1 in group for member2 in group if member1 != member2
            )
            if all_valid:
                valid_groups.append(group)

        # بروزرسانی لیست گروه‌ها
        groups = valid_groups  

        print("\n📢 Formed Groups:")
        for group in groups:
            print("👥 Group:", ", ".join(group))
