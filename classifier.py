import json
import os
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_LABELS, DATA_PATH, TRAIN_FILE, LABELS_FILE

_client = Groq(api_key=GROQ_API_KEY)


def load_labeled_examples() -> list[dict]:
    """
    Load the training episodes and merge them with the student's labels.

    Returns a list of dicts, each with:
      - "id"          : episode ID
      - "title"       : episode title
      - "podcast"     : podcast name
      - "description" : episode description
      - "label"       : the label from my_labels.json (may be None if not yet annotated)

    Only returns episodes where the label is a valid, non-null string.
    Episodes with null labels are silently skipped.
    """
    train_path = os.path.join(DATA_PATH, TRAIN_FILE)
    labels_path = os.path.join(DATA_PATH, LABELS_FILE)

    with open(train_path, encoding="utf-8") as f:
        episodes = {ep["id"]: ep for ep in json.load(f)}

    with open(labels_path, encoding="utf-8") as f:
        labels = {entry["id"]: entry["label"] for entry in json.load(f)}

    labeled = []
    for ep_id, ep in episodes.items():
        label = labels.get(ep_id)
        if label in VALID_LABELS:
            labeled.append({**ep, "label": label})

    return labeled


def build_few_shot_prompt(labeled_examples: list[dict], description: str) -> str:
    """
    Build a few-shot classification prompt using the student's labeled training examples.
    """
    prompt_parts = []
    
    # Task Instructions
    prompt_parts.append(
        "You are classifying podcast episodes by their format. Classify the episode\n"
        "into exactly one of these four labels:\n\n"
        "- interview: a conversation between a host and one or more guests\n"
        "- solo: a single host speaking from memory, experience, or opinion — no guests,\n"
        "  no assembled external sources\n"
        "- panel: multiple guests with roughly equal speaking time, often debating or\n"
        "  discussing a topic together\n"
        "- narrative: a story assembled from external sources — interviews, archival\n"
        "  audio, reporting — with a clear narrative arc\n\n"
        "Return only the label and your reasoning. Do not explain the taxonomy.\n"
    )

    # Examples
    if labeled_examples:
        prompt_parts.append("Here are some labeled examples:\n")
        for ex in labeled_examples:
            prompt_parts.append(
                f"Title: {ex.get('title', 'Unknown')}\n"
                f"Description: {ex.get('description', '')}\n"
                f"Label: {ex.get('label')}\n"
                "---\n"
            )

    # New Episode Request
    prompt_parts.append("Now, classify the following new episode:")
    prompt_parts.append(f"Title: Unknown\nDescription: {description}\nLabel: ?\n")
    
    prompt_parts.append(
        "Classify the episode above. Return your answer in JSON format with exactly "
        "two keys: \"label\" (must be one of the four valid labels) and \"reasoning\"."
    )

    return "\n".join(prompt_parts)


def classify_episode(description: str, labeled_examples: list[dict]) -> dict:
    """
    Classify a single podcast episode description using the few-shot LLM classifier.
    """
    prompt = build_few_shot_prompt(labeled_examples, description)
    
    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=300
        )
        
        raw_text = response.choices[0].message.content.strip()
        
        # Clean up markdown formatting if the LLM wrapped the JSON in a code block
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        raw_text = raw_text.strip()
        
        data = json.loads(raw_text)
        label = data.get("label", "unknown").lower()
        reasoning = data.get("reasoning", "")
        
        if label not in VALID_LABELS:
            label = "unknown"
            
        return {
            "label": label,
            "reasoning": reasoning
        }
        
    except Exception as e:
        return {
            "label": "unknown",
            "reasoning": f"Error occurred during classification: {str(e)}"
        }
