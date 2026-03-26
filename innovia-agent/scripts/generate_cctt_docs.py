import json
import re

# Charger les données CCTT
with open("cctt_dataset.json", encoding="utf-8") as f:
    data = json.load(f)

cctt_docs = []
for entry in data:
    # Générer un id unique basé sur le nom
    id_val = "cctt_" + re.sub(r"[^a-z0-9]", "", entry["nom"].lower())
    # Générer le texte principal
    text = entry["nom"]
    if "subtitle" in entry:
        text += " " + entry["subtitle"]
    if "secteurs" in entry:
        text += " " + " ".join(entry["secteurs"])
    if "expertises" in entry:
        text += " " + " ".join(entry["expertises"])
    if "description" in entry:
        if isinstance(entry["description"], list):
            text += " " + " ".join(entry["description"])
        else:
            text += " " + entry["description"]
    # Construction du doc
    doc = {
        "id": id_val,
        "text": text.strip(),
        "metadata": {
            "type": "CCTT",
            "name": entry["nom"],
            "domaines": entry.get("secteurs", [])
        }
    }
    cctt_docs.append(doc)

# Sauvegarde
with open("cctt_docs.json", "w", encoding="utf-8") as f:
    json.dump(cctt_docs, f, ensure_ascii=False, indent=2)

print(f"{len(cctt_docs)} CCTT docs saved in cctt_docs.json")
