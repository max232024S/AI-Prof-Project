import os
import requests
import json
import client
import prompts


data = client.run("flashcard_generator", "Generate me ten flashcards for upper level math terms.")
for card in data["flashcards"]:
    print(card["front"])
