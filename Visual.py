from Agent import Agent
import networkx as nx
import matplotlib.pyplot as plt
import threading
from collections import defaultdict
import time
from graphviz import Digraph
import logging
import os
os.environ["PATH"] += os.pathsep + "C:\\Users\\Tan Tan\\Downloads\\Graphviz-12.2.1-win64\\bin"


class Visual:
    def __init__(self, agents, monitor):
        self.agents = agents
        self.monitor = monitor  # Keep a reference to the monitor with live relationships
        self.lock = threading.Lock()
        #agent.memory = []
        self.relationship_history = [] # ← این خط اضافه شود

    def analyze_social_dynamics(self):
        """ Analyze the evolution of relationships and social changes """
        avg_relationship = sum(
            self.monitor.relationships[agent.name][other_agent.name]
            for agent in self.agents for other_agent in self.agents
            if agent != other_agent
        ) / (len(self.agents) * (len(self.agents) - 1))
        
        logging.info("\n--- Social Dynamics Analysis ---")
        logging.info(f"Average Relationship Strength: {avg_relationship:.2f}")
        logging.info("Relationship Strength Between Agents:")
        for agent in self.agents:
            for other in self.agents:
                if agent != other:
                    logging.info(f"  {agent.name} ↔ {other.name}: {self.monitor.relationships[agent.name][other.name]:.2f}")
        
    def analyze_behavioral_patterns(self):
        """ Analyze the behavioral patterns and decision-making """
        logging.info("\n--- Behavioral Patterns Analysis ---") 
        for agent in self.agents:
            mood_counts = {
                "happy": sum(1 for mood in agent.memory if mood.get('mood') == "happy"),
                "neutral": sum(1 for mood in agent.memory if mood.get('mood') == "neutral"),
                "angry": sum(1 for mood in agent.memory if mood.get('mood') == "angry"),
                "frustrated": sum(1 for mood in agent.memory if mood.get('mood') == "frustrated"),
                "nervous": sum(1 for mood in agent.memory if mood.get('mood') == "nervous")
            }
            decision_theories_counts = {
                "Increased Risk-Taking": sum(1 for theory in agent.memory if theory.get("cognitive pattern") == "Increased Risk-Taking"),
                "Positive Reinforcement": sum(1 for theory in agent.memory if theory.get("cognitive pattern") == "Positive Reinforcement"),
                "Baseline Functioning": sum(1 for theory in agent.memory if theory.get("cognitive pattern") == "Baseline Functioning"),
                "Avoidance Behavior": sum(1 for theory in agent.memory if theory.get("cognitive pattern") == "Avoidance Behavior"),
                "Defensive Mechanism": sum(1 for theory in agent.memory if theory.get("cognitive pattern") == "Defensive Mechanism")

            }
            cliche_counts = {
                "I'm on the edge of my seat!": sum(1 for cliche in agent.memory if cliche.get("cliche") == "I'm on the edge of my seat!"),
                "Everything is awesome!": sum(1 for cliche in agent.memory if cliche.get("cliche") == "Everything is awesome!"),
                "Just another day.": sum(1 for cliche in agent.memory if cliche.get("cliche") =="Just another day."),
                "I'm fed up!": sum(1 for cliche in agent.memory if cliche.get("cliche") == "I'm fed up!"),
               "I can't believe this!": sum(1 for cliche in agent.memory if cliche.get("cliche") == "I can't believe this!")

            }
            soical_pressure_counts = {
                "The Pressure to Be Agreeable": sum(1 for pressure in agent.memory if pressure.get("social_pressures") == "The Pressure to Be Agreeable"),
                "The Pressure to Be Interesting or Entertaining": sum(1 for pressure in agent.memory if pressure.get("social_pressures") == "The Pressure to Be Interesting or Entertaining"),
                "The Pressure to Avoid Awkward Silences": sum(1 for pressure in agent.memory if pressure.get("social_pressures") =="The Pressure to Avoid Awkward Silences"),
                "'The Pressure to Conform": sum(1 for pressure in agent.memory if pressure.get("social_pressures") == "'The Pressure to Conform"),
                "The Pressure to Overshare or Open Up": sum(1 for pressure in agent.memory if pressure.get("social_pressures") == "The Pressure to Overshare or Open Up"),
                "The Pressure to Respond Immediately": sum(1 for pressure in agent.memory if pressure.get("social_pressures") == "The Pressure to Respond Immediately")

            }
            efactors_counts = {
                 "Cultural changes": sum(1 for efactor in agent.memory if efactor.get("environmental_factors") == "Cultural changes"),
                "Social pressure": sum(1 for efactor in agent.memory if efactor.get("environmental_factors") == "Social pressure"),
                "Social learning": sum(1 for efactor in agent.memory if efactor.get("environmental_factors") =="Social learning")
            }
            logging.info(f"{agent.name} behavioral pattern over the conversation:")
            logging.info("\n /....................................../")
            for mood, count in mood_counts.items():
                logging.info(f"  {mood.capitalize()}: {count} times")
            logging.info("\n -----------------------------------")
            for theory, countd in decision_theories_counts.items():
                logging.info(f"  {theory.capitalize()}: {countd} times")
            logging.info("\n -----------------------------------")
            for cliche, countc in cliche_counts.items():
                logging.info(f"  {cliche.capitalize()}: {countc} times")
            logging.info("\n -----------------------------------")
            for social_pressure, counts in soical_pressure_counts.items():
                logging.info(f"  {social_pressure.capitalize()}: {counts} times")
            logging.info("\n -----------------------------------")
            for efactor, counte in efactors_counts.items():
                logging.info(f"  {efactor.capitalize()}: {counte} times")
            logging.info("\n -----------------------------------")

    def analyze_rumors_and_influence(self):
        """ Analyze the effect of rumors, clichés, and social pressures """
        logging.info("\n--- Impact of Rumors and Social Influence ---")
        for agent in self.agents:
            for memory in agent.memory:
                if "overheard someone say" in memory.get("content", ""):
                    logging.info(f"  {agent.name} was influenced by the rumor: {memory['content']}")

    def display_end_of_simulation_report(self):
        """ Function to display final report after the simulation """
        logging.info("\n--- End of Simulation Analysis ---")
        self.analyze_social_dynamics()
        self.analyze_behavioral_patterns()
        self.analyze_rumors_and_influence()
        #self.display_statistics()

    def draw_relationship_graph(self):
        plt.clf()  # clear the current figure
        G = nx.Graph()
        
        # Add nodes and edges using the updated relationship values from the monitor
        for agent in self.agents:
            current_mood = agent.analyze_mood("")
            G.add_node(agent.name, mood=current_mood)
            for other_agent in self.agents:
                if agent != other_agent:
                   strength = self.monitor.relationships[agent.name][other_agent.name]
                   if strength > 0:  # مقیاس‌بندی بهتر
                      G.add_edge(agent.name, other_agent.name, weight=strength)
                    
        # Determine node colors based on current mood
        mood_colors = {
            "happy": "green",
            "neutral": "yellow",
            "angry": "red",
            "frustrated": "blue",
            "nervous": "purple"
        }
        color_map = [mood_colors.get(agent.analyze_mood(""), "grey") for agent in self.agents]
        
        # Compute positions for the nodes (this layout is computed each time)
        pos = nx.spring_layout(G)
        
        # Update edge widths based on relationship strength (scaled)
        edge_weights = [G.edges[edge]['weight'] * 10 for edge in G.edges]
        
        node_size = 1000
        font_size = 14
        
        nx.draw(
            G, pos,
            with_labels=True,
            node_color=color_map,
            edge_color='grey',
            width=edge_weights,
            font_size=font_size,
            font_weight='bold',
            node_size=node_size
        )
        plt.title("Relationship Strength Between Agents")
        plt.draw()
        plt.pause(0.1)
    
    def update_graph_periodically(self):
        plt.ion()
        while True:
            with self.lock:
                self.draw_relationship_graph()
            plt.pause(1)  # به جای 0.5، زمان بیشتری بذار برای بهبود عملکرد

    def generate_block_diagram(self):
        """Generate and render a block diagram of the system architecture."""
        dot = Digraph("Agent-Based Simulation", format="png")

        # Define nodes
        dot.node("Main", "main.py\n(Manages execution)", shape="box", style="filled", fillcolor="lightblue")
        dot.node("Agents", "Agents\n(Conversational Entities)", shape="box", style="filled", fillcolor="lightgreen")
        dot.node("Monitor", "ConversationMonitor\n(Tracks relationships & groups)", shape="box", style="filled", fillcolor="lightyellow")
        dot.node("Visual", "Visual\n(Displays interactions & reports)", shape="box", style="filled", fillcolor="lightcoral")
        dot.node("LangChain", "LangChain\n(Generates agent prompts)", shape="box", style="filled", fillcolor="lightgray")

        # Define connections
        dot.edge("Main", "Agents", label="Initializes & Starts Conversation")
        dot.edge("Agents", "LangChain", label="Sends agent details for prompt generation")
        dot.edge("LangChain", "Agents", label="Provides agent-specific prompts")
        dot.edge("Agents", "Monitor", label="Updates Relationships")
        dot.edge("Monitor", "Visual", label="Sends Data for Visualization")
        dot.edge("Visual", "Main", label="Displays Final Report")

        dot.edge("Main", "Monitor", label="Triggers Relationship Updates")
        dot.edge("Main", "Visual", label="Starts Visualization Thread")

        # Introduce rumor mechanism
        dot.node("Rumor", "Rumor\n(Spreads after 60 sec)", shape="ellipse", style="filled", fillcolor="gray")
        dot.edge("Rumor", "Agents", label="Randomly introduced")

        # Render the graph
        output_path = "simulation_diagram"
        dot.render(output_path, format="png", view=True)
        print(f"Block diagram saved as {output_path}.png")

