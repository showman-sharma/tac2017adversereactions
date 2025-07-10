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

        # Split start and length to handle multi-span mentions
        starts = [int(s) for s in m.attrib["start"].split(",")]
        lengths = [int(l) for l in m.attrib["len"].split(",")]
        spans = [[s, s + l] for s, l in zip(starts, lengths)]
        
        mentions.append({
            "id": m.attrib["id"],
            "type": mtype,
            "spans": spans,
            "text": m.attrib["str"]
        })
        
    # Build ADE list (all spans of Adverse Reactions)
    ade_mentions = [m for m in mentions if m["type"] == "AdverseReaction"]
    ade_list = []
    for m in ade_mentions:
        ade_list.extend(m["spans"])

    # Map mention IDs to index
    mention_id_to_idx = {m["id"]: idx for idx, m in enumerate(ade_mentions)}

    # Collect negated mentions
    negated_mentions = set()
    for rel in root.findall(".//Relation"):
        if rel.attrib["type"].lower() == "negated":
            negated_mentions.add(rel.attrib["arg1"])

    # Filter ADR list: include only non-negated ADRs
    adr_list = []
    for idx, m in enumerate(ade_mentions):
        if m["id"] not in negated_mentions:
            # Since we have only one drug per document, index is 0
            adr_list.append([0, idx])

    # Medicine_list: treat the label drug as a synthetic span at start
    med_span = [0, len(label_drug)]

    result = {
        "id": os.path.splitext(os.path.basename(xml_path))[0],
        "text": text,
        "input_text": text,
        "Medicine_list": [med_span],
        "ADE_list": ade_list,
        "ADR_list": adr_list
    }
    return result

if __name__ == "__main__":
    # Path to your TAC XML files
    input_dir = "gold_xml"
    output_file = "tac2017_adrs.jsonl"

    xml_files = glob.glob(os.path.join(input_dir, "*.xml"))
    print(f"Found {len(xml_files)} files.")

    with open(output_file, "w", encoding="utf-8") as out_f:
        for xml_path in xml_files:
            example = parse_tac_xml(xml_path)
            out_f.write(json.dumps(example) + "\n")

    print(f"Done. JSONL saved to {output_file}")
