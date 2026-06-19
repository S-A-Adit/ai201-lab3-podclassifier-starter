# Evaluation Spec — Pod Classifier

Complete this spec **before** writing any code for Milestone 3.

Use Plan or Ask mode to think through each blank field. When you're done,
your answers here become the blueprint for `compute_accuracy()` and
`compute_per_class_accuracy()` in `evaluate.py`.

---

## Background: What is evaluation?

After building a classifier, we need to know how well it works. Evaluation answers:
- **Overall:** What fraction of episodes did we classify correctly?
- **Per-class:** Are we better at some labels than others?

Both functions take the same inputs: a list of predicted labels and a list of
ground-truth labels, in the same order.

---

## compute_accuracy(predictions, ground_truth)

### What it does
Returns the fraction of predictions that exactly match the ground truth.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `predictions` | `list[str]` | Labels predicted by `classify_episode()`, one per episode. |
| `ground_truth` | `list[str]` | The correct labels, in the same order as `predictions`. |

### Output

| Return value | Type | Description |
|---|---|---|
| accuracy | `float` | A value between 0.0 and 1.0. |

---

### Spec fields — fill these in before writing code

**Formula:**

**Formula:**

```
Accuracy is calculated by taking the number of correct predictions and dividing it by the total number of predictions. A prediction counts as "correct" if it exactly matches the ground-truth label for that episode.
```

---

**Step-by-step logic:**

**Step-by-step logic:**

```
1. If the list of predictions is empty, return 0.0 to prevent division by zero.
2. Initialize a counter for correct predictions to 0.
3. Iterate through both lists simultaneously (e.g. using zip).
4. For each pair, if predicted == ground_truth, increment the counter.
5. Return the counter divided by the length of the predictions list.
```

---

**Edge case — what if both lists are empty?**

**Edge case — what if both lists are empty?**

```
The function should return 0.0. This prevents a division by zero error, since the denominator (total number of predictions) would be 0.
```

---

**Worked example:**

```
predictions  = ["interview", "solo", "panel", "interview"]
ground_truth = ["interview", "solo", "solo",  "narrative"]

Correct matches are at indices 0 and 1. Indices 2 and 3 do not match.
Total correct: 2
Total predictions: 4
Accuracy: 2 / 4 = 0.5
```

---

## compute_per_class_accuracy(predictions, ground_truth)

### What it does
Returns accuracy broken down by each label. For each label in `VALID_LABELS`,
reports how many episodes with that ground-truth label were classified correctly.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `predictions` | `list[str]` | Labels predicted by `classify_episode()`. |
| `ground_truth` | `list[str]` | Correct labels, in the same order. |

### Output

A `dict` keyed by label. Each value is a dict with three keys:

```python
{
    "interview": {"correct": int, "total": int, "accuracy": float},
    "solo":      {"correct": int, "total": int, "accuracy": float},
    "panel":     {"correct": int, "total": int, "accuracy": float},
    "narrative": {"correct": int, "total": int, "accuracy": float},
}
```

---

### Spec fields — fill these in before writing code

**What does "correct" mean for a given class?**

**What does "correct" mean for a given class?**

```
For a specific class (like "interview"), an episode counts as "correct" if its ground-truth label is "interview" AND the predicted label is also "interview".
```

---

**What does "total" mean for a given class?**

**What does "total" mean for a given class?**

```
"Total" means the total number of episodes in the test set where the *ground-truth* label is that given class. It is the denominator for calculating per-class accuracy.
```

---

**Step-by-step logic:**

**Step-by-step logic:**

```
1. Initialize a dictionary tracking "correct", "total", and "accuracy" for every label in VALID_LABELS.
2. Loop over predictions and ground_truth simultaneously (e.g., using zip).
3. For each pair (predicted, truth), increment the "total" count for the `truth` label.
4. If predicted == truth, also increment the "correct" count for the `truth` label.
5. After the loop, iterate over the keys in the dictionary and compute "accuracy" as correct / total (if total > 0, else 0.0).
6. Return the dictionary.
```

---

**Edge case — what if a class has no examples in ground_truth (total == 0)?**

**Edge case — what if a class has no examples in ground_truth (total == 0)?**

```
The accuracy for that class should be set to 0.0. This avoids a ZeroDivisionError during the division.
```

---

**Worked example:**

```
predictions  = ["interview", "interview", "solo", "panel", "panel"]
ground_truth = ["interview", "solo",      "solo", "panel", "narrative"]

```
label       correct  total  accuracy
----------  -------  -----  --------
interview   1        1      1.0
solo        1        2      0.5
panel       1        1      1.0
narrative   0        1      0.0
```

---

## Reflection questions (discuss at the checkpoint)

1. Your overall accuracy might be decent even if one class has very low accuracy.
   Why is per-class accuracy a more informative metric than overall accuracy alone?

2. If `panel` episodes consistently get misclassified as `interview`, what does
   that tell you about your training labels or your prompt?

3. You labeled 20 training episodes and evaluated on 20 test episodes (5 per class).
   How might the evaluation results change if you had labeled 100 training episodes?
   What if you had 200 test episodes?
