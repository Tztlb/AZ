from Agent import Agent
from CM import ConversationMonitor
from Visual import Visual
import time
import random
import threading
import logging
from logging.handlers import RotatingFileHandler

api_key = "API KEY"
scenario = "Five friends—Ryan, Maya, Lena, Oliver, and Sam—sit around a table with steaming mugs, determined to beat overthinking"
agents = [
    Agent("Ryan", "Dismissive Realist", scenario, api_key, 0.6),
    Agent("Maya", "Eternal Spiral Thinker", scenario, api_key, 0.2),
    Agent("Lena", "One‑Up Trauma Dropper", scenario, api_key, 0.35),
    Agent("Oliver", "Fix‑It Know‑It‑All", scenario, api_key, 0.91),
    Agent("Sam", "Passive Viber", scenario, api_key, 0.75)
]

monitor = ConversationMonitor(agents)
visual = Visual(agents, monitor)
# Configure the logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        RotatingFileHandler('output.log', maxBytes=1024*1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Suppress warnings and errors
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

logging.info(f"Starting AI conversation with 5 agents with this scenario : {scenario}...")
graph_thread = threading.Thread(target=visual.update_graph_periodically, daemon=True)
graph_thread.start()
visual.generate_block_diagram()

def load_initial_conversation(raw_text, agents):
    lines = raw_text.strip().split("\n")
    memory_entries = []
    current_speaker = None
    current_content = []

    # همه اسم‌های ایجنت‌ها رو جمع کن
    agent_names = [agent.name for agent in agents]

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # چک کن اگه خط با اسم یکی از ایجنت‌ها شروع می‌شه
        matched_name = next((name for name in agent_names if line.startswith(name)), None)

        if matched_name:
            # اگر داشتیم دیالوگی رو جمع می‌کردیم، ثبتش کن
            if current_speaker and current_content:
                memory_entries.append({
                    "speaker": current_speaker,
                    "role": "user",
                    "content": " ".join(current_content).strip()
                })
            current_speaker = matched_name
            current_content = []
        else:
            current_content.append(line)

    # آخرین دیالوگ رو هم ثبت کن
    if current_speaker and current_content:
        memory_entries.append({
            "speaker": current_speaker,
            "role": "user",
            "content": " ".join(current_content).strip()
        })

    # محتوای اولیه رو به حافظه ایجنت‌ها اضافه کن
    for agent in agents:
        agent.memory.extend(memory_entries)


with open("conversation.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

load_initial_conversation(raw_text, agents)


start_time = time.time()  # Track when the conversation starts
rumor_introduced = False  # Ensure rumor only appears once

initial_speaker = random.choice(agents)
response = initial_speaker.query_gpt4(initial_speaker.memory, initial_speaker.mood_score, initial_speaker.decision_theory(), initial_speaker.cognitive_pattern() , initial_speaker.cliches() , initial_speaker.social_pressure() , initial_speaker.factors())
initial_speaker.memory.append(response)

# Main loop for conversation
#for i in range(10):
while time.time() - start_time < 300:
    random.shuffle(agents)
    for agent in agents:
        mood = agent.analyze_mood(response["content"])
        d = agent.decision_theory()
        cog = agent.cognitive_pattern()
        c = agent.cliches()
        s = agent.social_pressure()
        e = agent.factors()
        response = agent.query_gpt4(agent.memory, mood, d , cog , c, s , e)
        
        # Apply social rules and update memory
        response1_content = agent.apply_social_rules(mood, response["content"], monitor.relationship_strength)
        structured_response = {
        "speaker": agent.name,
        "role": "assistant",
        "content": response["content"],
        "mood": mood,
        "decision_theory": d,
        "cognitive_pattern": cog,
        "cliche": c,
        "social_pressure": s,
        "environmental_factors": e,
        "timestamp": time.time()
        }
        agent.memory.append(structured_response)

        for other_agent in agents:
            if other_agent != agent:
                other_agent.memory.append(structured_response)

        
        logging.info(f"{agent.name} ({mood}) ({d}) ({cog}) ({c}) ({s}) ({e}): {response['content']}")
        monitor.update_relationship(agent.name, mood)

    monitor.determine_groups()
    if not rumor_introduced and (time.time() - start_time) >= 150:
        rumor = Agent.introduce_rumor()  # تابع باید از کلاس Agent صدا زده شود

        # انتخاب یک عامل تصادفی برای شنیدن شایعه
        random_agent = random.choice(agents)  

        # اضافه کردن شایعه به حافظه‌ی عامل انتخاب‌شده
        random_agent.memory.append({"role": "user", "content": f"I just overheard someone say: '{rumor}' What do you think about that?"})

        logging.info(f"(Rumor spread) {random_agent.name} hears: {rumor}")

        rumor_introduced = True  # جلوگیری از معرفی مجدد شایعه
        mood = random_agent.analyze_mood(response["content"])
        d = random_agent.decision_theory()
        cog = random_agent.cognitive_pattern()
        c = random_agent.cliches()
        s = random_agent.social_pressure()
        e = random_agent.factors()
        response = random_agent.query_gpt4(random_agent.memory, mood, d , cog , c, s , e)
        
        # Apply social rules and update memory
        response1_content = random_agent.apply_social_rules(mood, response["content"], monitor.relationship_strength)
        structured_response = {
        "speaker": random_agent.name,
        "role": "assistant",
        "content": response["content"],
        "mood": mood,
        "decision_theory": d,
        "cognitive_pattern": cog,
        "cliche": c,
        "social_pressure": s,
        "environmental_factors": e,
        "timestamp": time.time()
        }
        random_agent.memory.append(structured_response)

        for other_agent in agents:
            if other_agent != random_agent:
                other_agent.memory.append(structured_response)
        
        logging.info(f"{random_agent.name} ({mood}) ({d}) ({cog}) ({c}) ({s}) ({e}): {response['content']}")
        monitor.update_relationship(random_agent.name, mood)
        
    time.sleep(1)
logging.info("Simulation ended")
visual.display_end_of_simulation_report()
