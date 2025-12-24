#class holding prompting functions as system role to define constraints and formatting
# different functions for different outlines 

def system_default():
    return {"role": "system",
            "content": "You are a helpful AI learning assistant"}

def system_tutor():
     return {"role": "system",
            "content": "You are a tutor for a student. Respond in meaningful and concise messages"}

system_prompts = {"default": system_default,
                  "tutor": system_tutor}