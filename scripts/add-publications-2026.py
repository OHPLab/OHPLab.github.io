import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "publications.json"

NEW = [
    {
        "title": "The Effects of Expressive Arts Therapy on Emotion Regulation and Aggression in Violent Offenders: A Randomized Controlled Trial",
        "authors": ["Xu, Z.", "Ou, X.", "Fan, J."],
        "journal": "Behavioral Sciences",
        "year": 2026,
        "publication_date": "2026-08-10",
        "doi": "10.3390/bs16081366",
        "url": "https://doi.org/10.3390/bs16081366",
        "source": "manual",
        "openalex_id": "",
        "confirmed": True,
        "manual": True,
        "note": "16(8), 1366",
        "source_note": "来源：MDPI / PubMed 人工核对",
    },
    {
        "title": "Neural Correlates of Brief Mindfulness Practice in Fostering Interpersonal Cooperation",
        "authors": ["Fan, J.", "Li, Y.", "Chen, Y.", "Lin, W.", "Deng, X."],
        "journal": "Mindfulness",
        "year": 2026,
        "publication_date": "2026-06-11",
        "doi": "10.1007/s12671-026-02890-y",
        "url": "https://doi.org/10.1007/s12671-026-02890-y",
        "source": "manual",
        "openalex_id": "",
        "confirmed": True,
        "manual": True,
        "note": "1-16",
        "source_note": "来源：Springer / CNKI 人工核对",
    },
    {
        "title": "Oxytocin Modulates Inhibitory Control via Neural-Temporal Mechanisms",
        "authors": ["Yi, W.", "Lin, H.", "Xu, X.", "Fan, J.", "Chen, Q.", "Xin, F."],
        "journal": "Psychophysiology",
        "year": 2026,
        "publication_date": "2026-06-01",
        "doi": "10.1111/psyp.70342",
        "url": "https://doi.org/10.1111/psyp.70342",
        "source": "manual",
        "openalex_id": "",
        "confirmed": True,
        "manual": True,
        "note": "63(6), e70342",
        "source_note": "来源：Wiley / PubMed 人工核对",
    },
    {
        "title": "Neural underpinnings of thematic and taxonomic processing in indirect semantic priming: evidence from the N400 and frontal negativity",
        "authors": ["Xiao, F.", "Xiao, N.", "Liang, X.", "Zhong, Y.", "Fan, J.", "Chen, Q."],
        "journal": "BMC Psychology",
        "year": 2026,
        "publication_date": "2026-04-24",
        "doi": "10.1186/s40359-026-04589-0",
        "url": "https://doi.org/10.1186/s40359-026-04589-0",
        "source": "manual",
        "openalex_id": "",
        "confirmed": True,
        "manual": True,
        "note": "14(1), 773",
        "source_note": "来源：Springer / PubMed 人工核对",
    },
    {
        "title": "Mental health, coping and related risk factors during the first 2 years of the COVID-19 pandemic in children: Nationally representative, multi-wave, cross-sectional results from 12 countries from the global COH-FIT study",
        "authors": ["Agorastos, A.", "Thompson, T.", "Solmi, M.", "Cortese, S.", "Estrade, A.", "et al. (incl. Fan, J.)"],
        "journal": "European Neuropsychopharmacology",
        "year": 2026,
        "publication_date": "2026-03-01",
        "doi": "10.1016/j.euroneuro.2025.112741",
        "url": "https://doi.org/10.1016/j.euroneuro.2025.112741",
        "source": "manual",
        "openalex_id": "",
        "confirmed": True,
        "manual": True,
        "note": "104, 112741（COH-FIT 国际协作研究，共 150 余位作者，范家琳为合作作者）",
        "source_note": "来源：Elsevier / PubMed 人工核对",
    },
]

existing = json.loads(DATA.read_text(encoding="utf-8"))
titles = {(p.get("title") or "").strip().lower() for p in existing}
dois = {(p.get("doi") or "").strip().lower() for p in existing if p.get("doi")}

added, skipped = [], []
for item in NEW:
    if item["title"].strip().lower() in titles:
        skipped.append(item["title"])
        continue
    if item["doi"].lower() in dois:
        skipped.append(item["title"])
        continue
    added.append(item)

merged = added + existing
DATA.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"新增 {len(added)} 条，跳过重复 {len(skipped)} 条，现有共 {len(merged)} 条")
for t in skipped:
    print("  已存在:", t)
