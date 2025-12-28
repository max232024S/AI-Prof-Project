import os
import requests
import json
import client
import prompts


def quiz(prompt): #temporary functional quiz feature
    data = client.run("quiz", prompt)
    count = 0
    numCorrect = 0
    for question in data["questions"]:
        choices = question["choices"]
        joined = " ".join(choices)
        answer = input(question["question"] + "\n" + joined + "\n")
        correct = question["answer"]
        if answer not in question["choices"]:
            print("Invalid Guess.\n")
            continue
        if answer != correct:
            print(f"Incorrect, the answer was {correct} \n")
        else:
            print("Correct!\n")
            numCorrect += 1
        count += 1
        length = len(data["questions"])
        if (count == length):
            percent = numCorrect / count
            print("Score: " + str(percent) + "%\n")


def flashcards(prompt): #temporary working model displaying each flashcard
    data = client.run("flashcard_generator", prompt)
    for card in data["flashcards"]:
        print(card["front"], ": ",  card["back"], "\n")





#flashcards("generate me five flashcards about math")
quiz("Generate a three question quiz on math")