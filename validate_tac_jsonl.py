import json

def validate_file(jsonl_path):
    total_examples = 0
    total_event_spans = 0
    total_adr_links = 0
    empty_spans = []
    out_of_bounds = []
    duplicate_spans = 0

    with open(jsonl_path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            ex = json.loads(line)
            total_examples += 1

            text = ex["text"]
            event_spans = ex["Event_list"]  # updated key
            adr_list = ex["ADR_list"]
            text_length = len(text)

            # Count
            total_event_spans += len(event_spans)
            total_adr_links += len(adr_list)

            # Validate spans
            seen_spans = set()
            for s, e in event_spans:
                if s >= e:
                    empty_spans.append((ex["id"], s, e))
                if e > text_length:
                    out_of_bounds.append((ex["id"], s, e, text_length))
                if (s, e) in seen_spans:
                    duplicate_spans += 1
                seen_spans.add((s, e))

            # Validate ADR indices
            for rel in adr_list:
                if rel[0] != 0:
                    print(f"WARNING: ADR relation drug index !=0 in {ex['id']}: {rel}")

    # Summary
    print("\n=== Validation Report ===")
    print(f"Examples processed : {total_examples}")
    print(f"Total Event spans  : {total_event_spans}")
    print(f"Total ADR links    : {total_adr_links}")
    print(f"Empty spans        : {len(empty_spans)}")
    print(f"Out-of-bounds spans: {len(out_of_bounds)}")
    print(f"Duplicate spans    : {duplicate_spans}")

    if empty_spans:
        print("\nFirst 5 empty spans:")
        for i, (docid, s, e) in enumerate(empty_spans[:5]):
            print(f"- {docid}: {s}-{e}")
    if out_of_bounds:
        print("\nFirst 5 out-of-bounds spans:")
        for i, (docid, s, e, tlen) in enumerate(out_of_bounds[:5]):
            print(f"- {docid}: {s}-{e} (text length={tlen})")
    if duplicate_spans:
        print("\nNote: duplicate spans detected (may be OK if mentions overlap).")

if __name__ == "__main__":
    validate_file("tac2017_adrs_train.jsonl")
