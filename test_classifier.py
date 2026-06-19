import os
from groq import Groq
from classifier import load_labeled_examples, build_few_shot_prompt
from config import GROQ_API_KEY, LLM_MODEL

def main():
    client = Groq(api_key=GROQ_API_KEY)
    examples = load_labeled_examples()
    
    test_desc = "Host Jane Doe sits down with three leading experts on artificial intelligence to debate the future of the field. They discuss everything from ethics to scaling laws, offering a variety of perspectives."
    
    prompt = build_few_shot_prompt(examples, test_desc)
    
    print("Testing episode classification...")
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=300
    )
    
    raw_text = response.choices[0].message.content
    print("Raw response text:\n" + "-"*40 + "\n" + raw_text + "\n" + "-"*40)

if __name__ == "__main__":
    main()
