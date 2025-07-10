# TAC2017 Adverse Reactions Dataset Preparation

This guide explains how to download, extract, and convert the TAC2017 dataset to JSON format ready for our LLM-based relation extraction pipeline.

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

- **Medicine_list**: always contains the document drug (e.g., `ACTEMRA`).
- **ADE_list**: all spans labeled as Adverse Reactions.
- **ADR_list**: pairs linking the drug to each reaction (negated reactions are excluded).

---

## 6️⃣ Notes

- Negated reactions are **excluded** from `ADR_list` but included in `ADE_list`.
- All offsets are character positions relative to `text`.
- This JSONL can be used directly in your `get_instruction()` function.

---

## 7️⃣ Validation (Optional)

To quickly check the output, you can run this snippet:

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

✅ That’s it. You’re ready to start testing.
