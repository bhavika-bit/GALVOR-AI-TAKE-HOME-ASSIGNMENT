import hashlib, json, re
from pathlib import Path

class BrandMemory:
    """Small persistent evidence store. Outcome memory stays empty until campaign results exist."""
    def __init__(self, path="outputs/brand_memory.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.items = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else []
        except (json.JSONDecodeError, OSError):
            self.items = []
        self._ids = {x.get("id") for x in self.items}

    def add(self, category, text, source="provided data"):
        text = str(text or "").strip()
        if not text:
            return
        key = hashlib.sha256(f"{category}|{source}|{text}".encode("utf-8")).hexdigest()[:20]
        if key not in self._ids:
            self.items.append({"id": key, "category": category, "text": text, "source": source})
            self._ids.add(key)

    def seed(self, ads, creators):
        ad_fields = ["hook_line", "main_benefit", "ad_format", "story_structure", "performance_style", "persuasion", "cta_type", "narratives", "ad_categories"]
        creator_fields = ["handle", "persona", "voice", "language_use", "themes", "format_habits", "what_feels_native", "what_would_feel_foreign"]
        for _, row in ads.iterrows():
            self.add("creative_knowledge", " | ".join(str(row.get(c, "")) for c in ad_fields), "ads.csv")
        for _, row in creators.iterrows():
            self.add("creator_knowledge", " | ".join(str(row.get(c, "")) for c in creator_fields), "creators.csv")
        # No outcome_memory records are fabricated: populate only after real campaign outcomes are supplied.

    def retrieve(self, query, limit=8):
        q = set(re.findall(r"[a-z0-9]+", str(query).lower()))
        ranked = []
        for item in self.items:
            words = set(re.findall(r"[a-z0-9]+", item.get("text", "").lower()))
            similarity = len(q & words) / max(1, len(q | words))
            ranked.append((similarity, item))
        return [item for similarity, item in sorted(ranked, key=lambda x: x[0], reverse=True)[:limit] if similarity > 0]

    def save(self):
        self.path.write_text(json.dumps(self.items, indent=2, ensure_ascii=False), encoding="utf-8")
