import json

# Charger les données de financement
with open("financement_cctt.json", encoding="utf-8") as f:
    data = json.load(f)["data"]

funding_docs = []
for prog in data:
    # Construction du texte principal
    text = f"{prog['nom']} financement R&D "
    if "domaines" in prog:
        text += " ".join(prog["domaines"]) + " "
    if "description" in prog:
        text += prog["description"]
    # Construction du doc
    doc = {
        "id": prog["id"],
        "text": text.strip(),
        "metadata": {
            "type": "PROGRAM",
            "name": prog["nom"],
            "trl": prog.get("trl_cible", "")
        }
    }
    funding_docs.append(doc)

# Sauvegarde
with open("funding_docs.json", "w", encoding="utf-8") as f:
    json.dump(funding_docs, f, ensure_ascii=False, indent=2)

print(f"{len(funding_docs)} funding docs saved in funding_docs.json")
