from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
import random

class Agent:
    def __init__(self, name, persona, scenario, api_key, mood):
        self.name = name
        self.persona = persona
        self.scenario = scenario
        self.api_key = api_key
        self.mood_score = mood  # مقدار اولیه برای مود بین 0.4 تا 0.6
        self.friends = set()
        self.memory = []

        self.chat_model = ChatOpenAI(
            openai_api_key=self.api_key,
            model="deepseek-chat",  # یا deepseek-chat اگر API دیگر دارید
            temperature=0.3,
            base_url = "domain"
            )

        self.prompt_template = PromptTemplate(
            input_variables=["persona", "scenario", "mood", "decision_theories" , "cognitive_patterns" , "cliches" , "social_pressures" , "environmental_factors"],
            template=(
                "You are {persona}. You are currently in a scenario where {scenario}.\n"
                "Respond in a way that reflects your current mood: {mood}.\n" 
                "Use these social patterns: {decision_theories},{social_pressures},{environmental_factors}. Use this cognitive pattern: {cognitive_patterns}. Use this cliche in your sentences: {cliches} \n"
                "Do not go beyond the given scenario and context And act as yourself."
            )
        )

    def query_gpt4(self, conversation_history, mood, decision_theories, cognitive_patterns, cliches, social_pressures, environmental_factors):
        """ارسال درخواست به مدل و دریافت پاسخ در محدوده تعیین شده"""
        prompt = self.prompt_template.format(
            persona=self.persona,
            scenario=self.scenario,
            mood=mood,
            decision_theories=decision_theories,
            cognitive_patterns=cognitive_patterns,
            cliches=cliches,
            social_pressures=social_pressures,
            environmental_factors=environmental_factors
        )

        messages = [SystemMessage(content=prompt)]
        for msg in conversation_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        response = self.chat_model.invoke(messages)
        current_mood = self.analyze_mood(response.content)
        current_pattern = self.cognitive_pattern()
        current_cliche = self.cliches()
        current_decision = self.decision_theory()
        current_social_pressures = self.social_pressure()
        current_environmental_factors = self.factors()
        # ذخیره در حافظه به همراه مود
        self.memory.append({
            "role": "assistant",
            "content": response.content,
            "mood": current_mood,
            "decision theory": current_decision,
            "cognitive pattern": current_pattern,
            "cliche": current_cliche,
            "social_pressures": current_social_pressures,
            "environmental_factors": current_environmental_factors
        })

        return {"role": "assistant", "content": response.content}
    
    def analyze_mood(self, last_response):
        if last_response is None:
            return "neutral"  # Default mood if no response is available

        positive_keywords = ["interesting", "agree", "exciting", "innovative", "good"]
        negative_keywords = ["concern", "problematic", "disagree", "risky", "bad", "Ugh"]
        
        for word in positive_keywords:
            if word in last_response.lower():
                self.mood_score = min(1.0, self.mood_score + 0.1)
                break
        
        for word in negative_keywords:
            if word in last_response.lower():
                self.mood_score = max(0.0, self.mood_score - 0.1)
                break
        if self.mood_score > 0.9:
            return "excited"
        elif self.mood_score > 0.7:
            return "happy"
        elif self.mood_score > 0.5:
            return "neutral"
        elif self.mood_score > 0.3:
            return "frustrated"
        elif self.mood_score > 0.15:
            return "nervous"
        else:
            return "angry"


    def decision_theory(self):
        decision_theories = {
            "happy": "Game theory",
            "neutral": "Logical decision-making",
            "frustrated": "Emotional decision-making",
            "angry": "Risk-averse decision-making"
        } #add nervous

        selected_decision = decision_theories.get(self.analyze_mood(""), "Logical decision-making")
        
        return f"{selected_decision}"
    
    def cognitive_pattern(self):
        patterns = {
            "excited" : "Increased Risk-Taking",
            "happy" : "Positive Reinforcement",
            "neutral" : "Baseline Functioning",
            "frustrated" : "Avoidance Behavior",
            "angry" : "Defensive Mechanism"
        }

        selected_patterns = patterns.get(self.analyze_mood(""), "Baseline Functioning")
        return f"{selected_patterns}"
    
    def cliches(self):
        cliches = {
            "excited" : "I'm on the edge of my seat!",
            "happy" : "Everything is awesome!",
            "neutral" : "Just another day.",
            "frustrated" : "I'm fed up!",
            "angry" : "I can't believe this!"
        }

        selected_cliche = cliches.get(self.analyze_mood(""), "Just another day.")
        return f"{selected_cliche}"
    
    def social_pressure(self):
        social_pressures = ["The Pressure to Be Agreeable" , 'The Pressure to Be Interesting or Entertaining', 'The Pressure to Avoid Awkward Silences',
                            'The Pressure to Conform', 'The Pressure to Overshare or Open Up' , 'The Pressure to Respond Immediately']
        
        selected_social_pressure = random.choice(social_pressures)
        return f"{selected_social_pressure}"
    
    def factors(self):
        environmental_factors = ["Cultural changes", "Social pressure", "Social learning"]
        selected_environment = random.choice(environmental_factors)
        return f"{selected_environment}"
    
    def apply_social_rules(self, mood, response, relationship_strength):
        if response == None:
            self.memory.append(response)

        if relationship_strength < 0.3:
            return f"{self.name} seems hesitant to engage. {response}"
        elif relationship_strength < 0.6:
            return f"{self.name} is cautious but willing to share. {response}"
        else:
            return f"{self.name} is enthusiastic and open. {response}"
        
    @staticmethod
    def introduce_rumor():
        """Randomly introduces a rumor into the conversation."""
        rumors = [
            "I overheard someone say that AI might replace all jobs by 2030.",
            "I overheard someone say at the event AI will surpass human intelligence in a decade!",
            "I overheard someone say how AI ethics are impossible to regulate!"
        ]
        return random.choice(rumors)
