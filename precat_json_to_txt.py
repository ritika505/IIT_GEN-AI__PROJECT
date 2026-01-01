import json

input_file = "precat_data.json"
output_file = "precat_data.txt"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(output_file, "w", encoding="utf-8") as f:
    for section, details in data.items():
        f.write(f"================ {section.upper()} ================\n\n")

        # Content (points / paragraphs)
        content = details.get("content", [])
        if content:
            f.write("CONTENT:\n")
            for i, item in enumerate(content, start=1):
                f.write(f"{i}. {item}\n")
        else:
            f.write("CONTENT: Not Available\n")

        # Table data (Batch schedule etc.)
        table = details.get("table", [])
        if table:
            f.write("\nTABLE DATA:\n")
            for row in table:
                f.write(" | ".join(row) + "\n")

        f.write("\n\n")

print("✅ precat_data.json converted to precat_data.txt")
