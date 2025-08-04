import xml.etree.ElementTree as ET
import json
import glob
import os

def parse_tac_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    label_drug = root.attrib.get("drug", "UnknownDrug")
    
    # Concatenate all sections as the input text
    sections = []
    for sec in root.findall(".//Section"):
        if sec.text:
            sections.append(sec.text.strip())
    text = "\n\n".join(sections)
    
    mentions = []
    for m in root.findall(".//Mention"):
        mtype = m.attrib["type"]
        starts = [int(s) for s in m.attrib["start"].split(",")]
        lengths = [int(l) for l in m.attrib["len"].split(",")]
        spans = [[s, min(s + l, len(text))] for s, l in zip(starts, lengths)]
        mentions.append({
            "id": m.attrib["id"],
            "type": mtype,
            "spans": spans,
            "text": m.attrib["str"]
        })

    # Build Drug and Event lists
    drug_mentions = [m for m in mentions if m["type"].lower() == "drug"]
    event_mentions = [m for m in mentions if m["type"].lower() == "adversereaction"]

    drug_list = []
    for m in drug_mentions:
        drug_list.extend(m["spans"])
    event_list = []
    for m in event_mentions:
        event_list.extend(m["spans"])

    # Map mention IDs to indices
    drug_id_to_idx = {m["id"]: idx for idx, m in enumerate(drug_mentions)}
    event_id_to_idx = {m["id"]: idx for idx, m in enumerate(event_mentions)}

    # Collect negated mentions
    negated_mentions = set()
    for rel in root.findall(".//Relation"):
        if rel.attrib["type"].lower() == "negated":
            negated_mentions.add(rel.attrib["arg2"])

    # Build ADR_list from explicit ADR relations (drug-event pairs)
    adr_list = []
    for rel in root.findall(".//Relation"):
        if rel.attrib["type"].lower() == "adr":
            drug_id = rel.attrib["arg1"]
            event_id = rel.attrib["arg2"]
            # Only include if not negated
            if event_id not in negated_mentions:
                if drug_id in drug_id_to_idx and event_id in event_id_to_idx:
                    adr_list.append([drug_id_to_idx[drug_id], event_id_to_idx[event_id]])

    # Fallback: if no explicit ADR relations, but only one drug, link all non-negated events to it
    if not adr_list and len(drug_list) == 1:
        for idx, m in enumerate(event_mentions):
            if m["id"] not in negated_mentions:
                adr_list.append([0, idx])

    result = {
        "id": os.path.splitext(os.path.basename(xml_path))[0],
        "text": text,
        "Drug_list": drug_list,
        "Event_list": event_list,
        "ADR_list": adr_list
    }
    return result

if __name__ == "__main__":
    input_dir = "train_xml"
    output_file = "tac2017_adrs_train.jsonl"

    xml_files = glob.glob(os.path.join(input_dir, "*.xml"))
    print(f"Found {len(xml_files)} files.")

    with open(output_file, "w", encoding="utf-8") as out_f:
        for xml_path in xml_files:
            example = parse_tac_xml(xml_path)
            out_f.write(json.dumps(example) + "\n")

    print(f"Done. JSONL saved to {output_file}")
