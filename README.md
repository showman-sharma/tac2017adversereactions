# TAC2017 Adverse Reactions Dataset Preparation

This guide explains how to download, extract, and convert the TAC2017 dataset to JSON format ready for our LLM-based relation extraction pipeline.

---

## 📖 About the Dataset

The TAC2017 Adverse Reactions dataset was created by the U.S. National Library of Medicine as part of the Text Analysis Conference (TAC) Adverse Drug Reaction Extraction task.

**What it contains:**
- FDA-approved drug labels in XML format.
- High-quality annotations:
  - **Adverse Reactions:** spans of text describing adverse events.
  - **Relations:** including negation and severity.
  - Normalization to MedDRA codes.

**Why this dataset is valuable:**
- It is considered a benchmark corpus for evaluating NER and relation extraction models in the pharmacovigilance domain.
- It has been used in numerous publications and shared tasks.
- It provides real regulatory language, not synthetic text.

---

## 1️⃣ Download the Dataset

1. Go to:

   [https://bionlp.nlm.nih.gov/tac2017adversereactions/](https://bionlp.nlm.nih.gov/tac2017adversereactions/)

2. In the **Test Data – Gold Standard Annotations** section, download:

   ```
   gold_xml.tar.gz
   ```

---

## 2️⃣ Extract the XML Files

From your terminal, run:

```bash
mkdir gold_xml
tar -xvzf gold_xml.tar.gz -C gold_xml
```

After this step, you should see:

```
gold_xml/
  ACTEMRA.xml
  ...
```

---

## 3️⃣ Prepare the Conversion Script

Make sure you have the `tac_to_jsonl.py` script in the same directory.

✅ **This script is already provided.**  
You do not need to modify it.

---

## 4️⃣ Run the Conversion

In the same folder, run:

```bash
python tac_to_jsonl.py
```

This will create a file:

```
tac2017_adrs.jsonl
```

Each line contains one example in JSON format.

---

## 5️⃣ Output Format

Each example in `tac2017_adrs.jsonl` has this structure:

```json
{
  "id": "ACTEMRA",
  "text": "...",
  "input_text": "...",
  "Medicine_list": [[0, 7]],
  "ADE_list": [[start, end], ...],
  "ADR_list": [[0, i], ...]
}
```

**Fields:**
- `id`: Document identifier (usually the drug name).
- `text`: Full text of the drug label.
- `input_text`: Same as text.
- `Medicine_list`: One span representing the document drug.
- `ADE_list`: All spans of text annotated as Adverse Reactions (multi-span mentions included).
- `ADR_list`: Pairs linking the single drug (index 0) to each non-negated Adverse Reaction.

---

## 6️⃣ Important Notes

- Negated reactions are **excluded** from `ADR_list` but included in `ADE_list`.
- All offsets are character positions relative to `text`.
- If a mention has multiple discontinuous spans, all are included in `ADE_list`.
- Duplicate spans are allowed, as multiple annotations may overlap.

---

## 7️⃣ Validation

To ensure data integrity, you can run the provided validation script:

**validate_tac_jsonl.py**

This script will:
- Count total examples, spans, and relations.
- Detect empty spans.
- Detect out-of-bounds spans.
- Report duplicate spans.
- Verify ADR indices.

**How to run:**

```bash
python validate_tac_jsonl.py
```

**Example output:**
```
=== Validation Report ===
Examples processed : 99
Total ADE spans    : 13847
Total ADR links    : 12409
Empty spans        : 0
Out-of-bounds spans: 0
Duplicate spans    : 464

Note: duplicate spans detected. This is common when mentions overlap.
```

✅ **If you see `Out-of-bounds spans: 0` and `Empty spans: 0`, your dataset is valid.**

---

## 8️⃣ Quick Spot-Check (Optional)

You can also inspect a few examples manually:

```python
import json

with open("tac2017_adrs.jsonl") as f:
    for i, line in enumerate(f):
        ex = json.loads(line)
        print(f"{ex['id']} | ADEs: {len(ex['ADE_list'])} | ADRs: {len(ex['ADR_list'])}")
        if i > 5:
            break
```

---

✅ That’s it. You are ready to start testing your pipeline with clean, validated data.
