# Classifier Spec — Pod Classifier

Complete this spec **before** writing any code for Milestone 2.

Use Plan or Ask mode to think through each blank field. When you're done,
your answers here become the blueprint for `build_few_shot_prompt()` and
`classify_episode()` in `classifier.py`.

---

## build_few_shot_prompt(labeled_examples, description)

### What it does
Constructs a prompt string for the LLM that includes the task instructions,
all labeled training examples, and the new episode description to classify.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `labeled_examples` | `list[dict]` | Each dict has `"title"`, `"description"`, `"label"` (and others). These are the examples you labeled in Milestone 1. |
| `description` | `str` | The episode description to classify. |

### Output

| Return value | Type | Description |
|---|---|---|
| prompt | `str` | A complete prompt string ready to send to the LLM. |

---

### Spec fields — fill these in before writing code

**Task instruction (what should the LLM know about the task?):**

```
You are classifying podcast episodes by their format. Classify the episode
into exactly one of these four labels:

- interview: a conversation between a host and one or more guests
- solo: a single host speaking from memory, experience, or opinion — no guests,
  no assembled external sources
- panel: multiple guests with roughly equal speaking time, often debating or
  discussing a topic together
- narrative: a story assembled from external sources — interviews, archival
  audio, reporting — with a clear narrative arc

Return only the label and your reasoning. Do not explain the taxonomy.
```

---

**How should labeled examples be formatted in the prompt?**

```
Each example should include the episode title, a brief excerpt or the full
description, and the correct label. Separate examples with a blank line or
a delimiter like "---". Include all fields that help the model see why the
label was applied — title and description are both useful; other fields
(like episode ID) are not needed.
```

---

**Example block sketch (write one concrete example):**

```
Title: {title}
Description: {description}
Label: {label}
```

---

**How should the new episode (to be classified) be presented?**

```
Present it in the same format as the labeled examples, but omit the Label
line and replace it with an instruction to classify. For example:

Title: {title}
Description: {description}
Label: ?

Then add a line like: "Classify the episode above. Return your answer in
the format below:" followed by the output format you chose.
```

---

**What output format should you request from the LLM?**

```
I will request a JSON object format. It is the most reliable way to parse structured data. 
Format: {"label": "the_label", "reasoning": "brief explanation"}.
Tradeoffs: JSON can sometimes be wrapped in markdown code blocks by LLMs, but that is easily stripped out. It is far less error-prone than splitting by text delimiters.
```

---

**Edge cases to handle in the prompt:**

```
If `labeled_examples` is empty, the loop constructing the examples will just be skipped, falling back smoothly to a zero-shot prompt. For very short descriptions, the LLM will just classify based on what is available.
```

---

## classify_episode(description, labeled_examples)

### What it does
Classifies a single podcast episode description using the few-shot LLM classifier.
Returns a dict with a label and reasoning.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `description` | `str` | The episode description to classify. |
| `labeled_examples` | `list[dict]` | Labeled training examples from `load_labeled_examples()`. |

### Output

| Return value | Type | Description |
|---|---|---|
| result | `dict` | Must have keys `"label"` and `"reasoning"`. `"label"` must be one of `VALID_LABELS` or `"unknown"`. |

---

### Spec fields — fill these in before writing code

**Step 1 — Build the prompt:**

```
Call build_few_shot_prompt(labeled_examples, description) and store the
returned string in a variable (e.g., prompt). Pass through both arguments
exactly as received — no modification needed before calling.
```

---

**Step 2 — Send to the LLM:**

```
Call _client.chat.completions.create() with:
  - model: the model name from config (LLM_MODEL)
  - messages: a list with one dict — {"role": "user", "content": prompt}
    (system-design.md shows an optional system message too — either shape works)
  - max_tokens: a reasonable limit (e.g., 200–300) to keep responses concise

Extract the response text from:
  response.choices[0].message.content
```

---

**Step 3 — Parse the response:**

```
Since I requested JSON, I will extract the text, strip any backticks or "```json" markdown formatting the LLM might have added, and use `json.loads(text)` to parse it. Then I will extract the "label" and "reasoning" keys from the parsed dictionary.
```

---

**Step 4 — Validate the label:**

```
I will convert the extracted label to lowercase (just in case), and check if `label in VALID_LABELS`. If it is not, I will set the label to "unknown", preserving the LLM's original reasoning so it can be debugged.
```

---

**Step 5 — Handle errors gracefully:**

```
I will wrap the API call and the parsing logic in a broad `try...except Exception as e:` block. If anything goes wrong (e.g., API error, JSON decode error, missing keys), I will catch the exception and return a fallback dictionary: `{"label": "unknown", "reasoning": f"Error occurred: {str(e)}"}`. This ensures the loop continues.
```

---

### Return value structure

```python
{
    "label": str,      # one of VALID_LABELS, or "unknown" if invalid/error
    "reasoning": str,  # brief explanation from the LLM
}
```

---

## Notes on label quality

The classifier is only as good as your labels. If your training examples have
inconsistent or ambiguous labels, the LLM will learn the wrong pattern.

Before implementing the classifier, re-read `data/taxonomy.md` and double-check
any labels you're unsure about. Annotation quality is part of the lab.

---

## Implementation Notes

*Fill this in after implementing and testing both functions.*

**Test: what does the raw LLM response look like for one episode?**

```
Episode tested: "Host Jane Doe sits down with three leading experts on artificial intelligence..."
Raw response text: 
```json
{
  "label": "panel",
  "reasoning": "The description indicates multiple guests discussing a topic together ('three leading experts... debate the future') and 'offering a variety of perspectives', which aligns with the panel format of multiple speakers without a single subject."
}
```
```

**How did you parse the label out of the response?**

```
First, I used `.strip()` on the raw text. Then, I checked if the string started with "```json" or "```" and ended with "```" and stripped those markdown characters out. After that, I passed the cleaned string to `json.loads(text)` and extracted the label with `.get("label", "unknown").lower()`.
```

**Did any episodes return `"unknown"`? If so, why?**

```
No, the LLM successfully followed the output instructions and provided valid labels within the requested JSON format, because the JSON instruction and validation instructions were very explicit in the few-shot prompt.
```

**One thing about the output format that surprised you:**

```
I found it slightly surprising how often the LLM insists on wrapping pure JSON in markdown formatting (like ```json), even when strictly told to just return the JSON format. Stripping the markdown fence was a necessary step.
```
