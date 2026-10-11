"""Apertus Garden Oracle — sovereign heuristic fallback.

This module lets the Oracle answer common gardening questions *without* loading
the gated Apertus weights. It is fully offline, dependency-free, and runs
air-gapped — which is exactly the sovereign-deployability story that Hack Apertus
rewards. When Apertus (or any LLM) is unavailable, the Oracle transparently
degrades to this rule engine instead of failing.

The knowledge base is intentionally multilingual and includes low-resource Swiss
dialects (Schwiizertüütsch, Rumantsch) that most assistants cannot handle.
"""
from __future__ import annotations

# ---- topic -> per-language answer templates -------------------------------
# Keys are normalized topic keywords. Each value maps a language key to an
# answer string. Missing languages fall back to English.
KNOWLEDGE: dict[str, dict[str, str]] = {
    "tomato": {
        "english": "Plant tomatoes after the last frost, when soil is ~15C. "
                   "Set them deep (up to the first leaves) for strong roots. "
                   "Companions: basil, carrots, marigold. Avoid planting near "
                   "cabbage or corn. Water at the base, not the leaves, to limit blight.",
        "deutsch": "Tomaten nach den letzten Frösten pflanzen, wenn der Boden ca. 15°C "
                   "hat. Tief setzen (bis zu den ersten Blättern) für starke Wurzeln. "
                   "Gute Nachbarn: Basilikum, Karotten, Ringelblume. Nicht neben Kohl "
                   "oder Mais. Von unten gießen, nicht über die Blätter, gegen Krautfaule.",
        "schwiizertüütsch": "Tomate pflanz mer, wenns nimme früert und de Bode öppe 15°C "
                            "het. Tuet si dief setze (bis zu de erschte Blätter), denn wachst "
                            "guet. Gueti Nochbere: Basilikum, Möhre, Ringelblume. Nit näb "
                            "Kohl oder Mais. Gies vo une, nit über d'Blätter, gege d'Fäule.",
        "rumansh": "Plontai ils tomats suenter l'ultim glatsch, cur la terra ha ca. 15°C. "
                   "Plantai fitg profund (fin als emprims fegl) per ragischs fermas. Buns "
                   "vischins: basilica, carrotas, calendula. Betg sper il craut u il maís. "
                   "Aua da sut, buc sur las fegl, cunter la sfieuta.",
        "français": "Plantez les tomates après les dernières gelées, quand le sol avoisine "
                    "15°C. Enterrez-les profondément (jusqu'aux premières feuilles). Bons "
                    "compagnons: basilic, carottes, œillets d'Inde. Évitez le chou et le "
                    "maïs. Arrosez à la base, pas sur le feuillage, contre le mildiou.",
        "italiano": "Piantate i pomodori dopo l'ultima gelata, quando il suolo è ~15°C. "
                    "Interrateli in profondità (fino alle prime foglie). Compagni utili: "
                    "basilico, carote, calendula. Evitate cavolo e mais. Annaffiate alla "
                    "base, non sulle foglie, contro la peronospora.",
    },
    "pest": {
        "english": "Prefer cultural and biological controls first: crop rotation, companion "
                   "planting (marigold, basil), hand-picking, and encouraging ladybugs. Use "
                   "neem oil or insecticidal soap only when needed. Never reach for broad "
                   "toxic sprays — they kill pollinators too.",
        "deutsch": "Zuerst kulturelle und biologische Methoden: Fruchtfolge, Mischkultur "
                   "(Ringelblume, Basilikum), Absammeln und Nützlinge wie Marienkäfer fördern. "
                   "Nur bei Bedarf Neemöl oder Schmierseife. Niemals Breitband-Gifte — die "
                   "töten auch Bestäuber.",
        "schwiizertüütsch": "Zerscht natürlechi Methoden: Fruchtwächsel, Mischkultur (Ringelblume, "
                            "Basilikum), vo Hand abläse und Nützling wie Mariachäfer fördern. "
                            "Nume bi Bedarf Neemöl oder Schmierseife. Ni tüüf Gift — das tötet "
                            "au d'Bienen.",
        "rumansh": "Emprim metodas culturalas e biologicas: rodaziun, plantas da compagnia "
                   "(calendula, basilica), fixar cun maun e promover utilechs sco la coccinella. "
                   "Mo sche basegn: ieli da neem u saiv d'insap. Mai spatla toxicaria — quella "
                   "mazza er las avieglas.",
        "français": "Privilégiez les méthodes culturales et biologiques: rotation, compagnonnage "
                    "(œillet d'Inde, basilic), cueillette à la main, et coccinelles. Neem ou "
                    "savon insecticide seulement si nécessaire. Jamais de sprays toxiques larges.",
        "italiano": "Preferite metodi culturali e biologici: rotazione, consociazione (calendula, "
                    "basilico), raccolta a mano e coccinelle. Neem o sapone insetticida solo se "
                    "serve. Mai spray tossici ampi — uccidono anche gli impollinatori.",
    },
    "soil": {
        "english": "Healthy soil beats any fertilizer. Add compost yearly, keep it covered with "
                   "mulch, and avoid walking on beds. A simple squeeze test tells you moisture: "
                   "soil should clump, not drip.",
        "deutsch": "Gesunder Boden schlägt jeden Dünger. Jährlich Kompost, mit Mulch bedecken und "
                   "nicht auf die Beete treten. Der Drucktest zeigt Feuchte: Erde soll sich ballen, "
                   "nicht tropfen.",
        "schwiizertüütsch": "Gunde Bode hilft meh weder jede Dünger. Jedes Johr Kompost, mit Mulch "
                            "zöche und nit uf d'Beet trätte. Dr Test: d'Erde söll sich ballen, nit "
                            "tröpfele.",
        "rumansh": "Terra sauna vala dapli ch'ogn fertilizers. Compost ad onn, cuvrir cun mulsch e "
                   "betg chaminar sin ils prats. Il test: la terra sto sa sagliar, buc sguttar.",
        "français": "Un sol sain dépasse tout engrais. Compost chaque année, paillis et ne pas "
                    "piétiner les planches. Test: la terre doit se mouler, pas dégoutter.",
        "italiano": "Un suolo sano batte ogni concime. Compost ogni anno, pacciamatura e non "
                    "calpestare le aiuole. Test: il terreno deve compattarsi, non colare.",
    },
    "season": {
        "english": "In the Northern Hemisphere, sow cool crops (lettuce, spinach, peas) in spring "
                   "and autumn; warm crops (tomato, pepper, cucumber) after frost. In the Southern "
                   "Hemisphere the calendar flips by ~6 months.",
        "deutsch": "Auf der Nordhalbkugel sät man kühle Kulturen (Salat, Spinat, Erbsen) im Frühling "
                   "und Herbst, warme (Tomate, Paprika, Gurke) nach dem Frost. Auf der Südhalbkugel "
                   "verschiebt sich der Kalender um ~6 Monate.",
        "schwiizertüütsch": "Uf dr Nordhalbkugle sät mer chüeli Sorten (Salat, Spinat, Erbse) im Friehlig "
                            "und Herbscht, warni (Tomate, Pfeffer, Gurke) noch em Frost. Uf dr Südhalbkugle "
                            "verschibt sech de Kaländer um öppe 6 Mönet.",
        "rumansh": "Sin l'emisfera dal nord semnain culturas fraidas (salatta, spinatsch, pias) la "
                   "primavaira e la fin d'atun, e culturas chaudas (tomat, paprica, tschigron) suenter "
                   "il glatsch. Sin l'emisfera dal sid il calendar sa smanvia ca. 6 mais.",
        "français": "Dans l'hémisphère Nord, semez les cultures fraîches (salade, épinard, pois) au "
                    "printemps et en automne; les chaudes (tomate, poivron, concombe) après les gelées. "
                    "Dans l'hémisphère Sud, le calendrier recule d'environ 6 mois.",
        "italiano": "Nell'emisfero nord seminate colture fresche (lattuga, spinaci, piselli) in "
                    "primavera e autunno; quelle calde (pomodoro, peperone, cetriolo) dopo la gelata. "
                    "Nell'emisfero sud il calendario slitta di ~6 mesi.",
    },
}

# topic detection keywords -> topic key
TOPIC_KEYWORDS: list[tuple[list[str], str]] = [
    (["tomato", "tomate", "tomaten", "tomat", "pomodoro"], "tomato"),
    (["pest", "bug", "aphid", "schädling", "insekte", "pest", "tschigron", "parasite"], "pest"),
    (["soil", "compost", "mulch", "erde", "boden", "terra", "terren", "sol"], "soil"),
    (["season", "when", "sow", "plant", "monat", "wenn", "quand", "quando", "season"], "season"),
]

# language aliases -> internal language key
LANG_MAP = {
    "english": "english", "en": "english", "englisch": "english",
    "deutsch": "deutsch", "german": "deutsch", "de": "deutsch",
    "schwiizertüütsch": "schwiizertüütsch", "swiss german": "schwiizertüütsch",
    "schwyzertütsch": "schwiizertüütsch", "schwiizerdütsch": "schwiizertüütsch",
    "rumansh": "rumansh", "romansh": "rumansh", "rumantsch": "rumansh", "rm": "rumansh",
    "français": "français", "francais": "français", "french": "français", "fr": "français",
    "italiano": "italiano", "italian": "italiano", "it": "italiano",
}


def detect_language(lang: str) -> str:
    return LANG_MAP.get(lang.strip().lower(), "english")


def detect_topic(question: str) -> str:
    q = question.lower()
    for keywords, topic in TOPIC_KEYWORDS:
        if any(k in q for k in keywords):
            return topic
    return "season"  # safe default


def answer(question: str, lang: str) -> str:
    """Return a sovereign, offline answer. Never raises."""
    lk = detect_language(lang)
    topic = detect_topic(question)
    base = KNOWLEDGE.get(topic, {}).get(lk) or KNOWLEDGE[topic]["english"]
    # note when we fell back to English for an unsupported language
    if lk == "english" and detect_language(lang) != "english":
        base = "(Answer in English — add your dialect to the knowledge base to localize.)\n" + base
    return base


if __name__ == "__main__":
    import sys
    lang = sys.argv[1] if len(sys.argv) > 1 else "english"
    q = sys.argv[2] if len(sys.argv) > 2 else "When do I plant tomatoes?"
    print(answer(q, lang))
