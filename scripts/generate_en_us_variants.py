#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import unicodedata
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path


DEFAULT_LEXICON = Path("../dictionary/build/en_US/language-data/en_US/lexicon.tsv")
DEFAULT_OUTPUT = Path("en_US/variants.tsv")
VOWELS = frozenset("aeiou")
MAX_VARIANTS_PER_BASE = 48

PRODUCTIVE_STOPWORDS = frozenset(
    {
        "the",
        "and",
        "for",
        "that",
        "with",
        "from",
        "this",
        "are",
        "was",
        "were",
        "been",
        "being",
        "will",
        "shall",
        "must",
        "may",
        "you",
        "his",
        "her",
        "she",
        "they",
        "their",
        "our",
        "your",
        "its",
        "who",
        "which",
        "about",
        "after",
        "just",
        "into",
        "when",
        "than",
        "them",
        "what",
        "there",
        "some",
        "those",
        "during",
        "before",
        "where",
        "through",
        "because",
        "should",
        "would",
        "could",
        "might",
        "not",
        "but",
        "more",
        "most",
        "against",
        "around",
        "between",
        "under",
        "without",
        "however",
        "never",
        "throughout",
        "towards",
        "instead",
        "alongside",
    }
)

BUILTIN_DENYLIST: frozenset[tuple[str, str, str]] = frozenset(
    {
        ("both", "bother", "comparative"),
        ("cent", "center", "comparative"),
        ("fire", "firence", "derivation"),
        ("sold", "solder", "comparative"),
        ("ball", "ballal", "derivation"),
        ("east", "easter", "comparative"),
        ("sent", "sentence", "derivation"),
        ("comment", "commence", "derivation"),
        ("spot", "spotify", "derivation"),
        ("contain", "contention", "derivation"),
        ("mode", "modest", "superlative"),
        ("hole", "holy", "derivation"),
        ("surge", "surgical", "derivation"),
        ("occur", "occurence", "derivation"),
        ("cape", "capable", "derivation"),
        ("dive", "divest", "superlative"),
        ("bans", "bansal", "derivation"),
        ("pole", "poly", "derivation"),
        ("bloc", "blocked", "past_tense"),
        ("bloc", "blocking", "present_participle"),
        ("pitt", "pittance", "derivation"),
        ("broth", "brother", "comparative"),
        ("prem", "premise", "derivation"),
        ("sept", "septic", "derivation"),
        ("fore", "forest", "superlative"),
        ("amen", "amenable", "derivation"),
        ("amen", "amenity", "derivation"),
        ("ange", "anger", "comparative"),
        ("char", "charity", "derivation"),
        ("bene", "bening", "present_participle"),
        ("sugg", "suggest", "superlative"),
        ("brows", "browsing", "present_participle"),
        ("brows", "browser", "agent_noun"),
        ("conserve", "conservest", "superlative"),
        ("moth", "mother", "comparative"),
        ("bric", "bricked", "past_tense"),
        ("bric", "bricking", "present_participle"),
        ("bere", "bering", "present_participle"),
        ("buie", "buying", "present_participle"),
        ("clic", "clicking", "present_participle"),
        ("conte", "contest", "superlative"),
        ("coole", "cooling", "present_participle"),
        ("harv", "harvest", "superlative"),
        ("harve", "harvest", "superlative"),
        ("ince", "incest", "superlative"),
        ("locke", "locking", "present_participle"),
        ("locke", "locker", "agent_noun"),
        ("trigg", "trigger", "comparative"),
        ("asses", "assessed", "past_tense"),
        ("asses", "assessing", "present_participle"),
        ("discus", "discussed", "past_tense"),
        ("discus", "discussing", "present_participle"),
        ("discus", "discussion", "derivation"),
        ("mutt", "mutter", "comparative"),
        ("tang", "tangible", "derivation"),
        ("temp", "tempest", "superlative"),
        ("temp", "temper", "comparative"),
        ("past", "pasting", "present_participle"),
        ("past", "pastor", "agent_noun"),
        ("service", "servicable", "derivation"),
        ("though", "thoughful", "derivation"),
        ("less", "lesser", "agent_noun"),
        ("access", "accessable", "derivation"),
        ("party", "partial", "derivation"),
        ("party", "partition", "derivation"),
        ("soon", "soa", "inflection"),
        ("soon", "sooner", "agent_noun"),
        ("fact", "factor", "agent_noun"),
        ("spent", "spence", "derivation"),
        ("improve", "improvise", "derivation"),
        ("apple", "apply", "derivation"),
        ("upon", "upa", "inflection"),
        ("severe", "several", "derivation"),
        ("prove", "provence", "derivation"),
        ("plus", "pli", "inflection"),
        ("please", "pleasence", "derivation"),
        ("earn", "earner", "comparative"),
        ("earn", "earnest", "superlative"),
        ("guide", "guidence", "derivation"),
        ("moon", "moa", "inflection"),
        ("icon", "ica", "inflection"),
        ("noon", "noa", "inflection"),
        ("dive", "diver", "comparative"),
        ("iron", "ira", "inflection"),
        ("messi", "messiness", "derivation"),
        ("silicon", "silica", "inflection"),
        ("morale", "morality", "derivation"),
        ("serie", "serious", "derivation"),
        ("pleas", "pleased", "past_tense"),
        ("pleas", "pleasing", "present_participle"),
        ("pleas", "pleased", "past_participle"),
        ("pleas", "pleasence", "derivation"),
        ("lemon", "lema", "inflection"),
        ("chant", "chance", "derivation"),
        ("chant", "chancy", "derivation"),
        ("marsh", "marshal", "derivation"),
        ("forge", "forgive", "derivation"),
        ("onion", "onia", "inflection"),
        ("polite", "political", "derivation"),
        ("belle", "belly", "derivation"),
        ("caste", "casting", "present_participle"),
        ("caste", "caster", "agent_noun"),
        ("caste", "castor", "agent_noun"),
        ("brake", "brakence", "derivation"),
        ("paste", "pastor", "agent_noun"),
        ("lille", "lilly", "derivation"),
        ("matte", "matter", "agent_noun"),
        ("probate", "probable", "derivation"),
        ("anant", "anancy", "derivation"),
        ("earle", "early", "derivation"),
        ("electron", "electra", "inflection"),
        ("frant", "france", "derivation"),
        ("viola", "violation", "derivation"),
        ("attain", "attention", "derivation"),
        ("grate", "grateful", "derivation"),
        ("grate", "gration", "derivation"),
        ("amore", "amoral", "derivation"),
        ("merci", "merciful", "derivation"),
        ("natale", "nataly", "derivation"),
        ("parti", "partied", "past_tense"),
        ("parti", "partied", "past_participle"),
        ("parti", "partial", "derivation"),
        ("parti", "partition", "derivation"),
        ("posse", "possible", "derivation"),
        ("ammonium", "ammonia", "inflection"),
        ("attache", "attached", "past_tense"),
        ("attache", "attaching", "present_participle"),
        ("attache", "attached", "past_participle"),
        ("curate", "curable", "derivation"),
        ("supple", "supply", "derivation"),
        ("tulle", "tully", "derivation"),
        ("classy", "classic", "derivation"),
        ("classy", "classical", "derivation"),
        ("rusty", "rustic", "derivation"),
        ("andry", "andric", "derivation"),
        ("organism", "organist", "agent_noun"),
        ("organist", "organism", "derivation"),
        ("chang", "changed", "past_tense"),
        ("chang", "changing", "present_participle"),
        ("chang", "changed", "past_participle"),
        ("chang", "changer", "agent_noun"),
        ("rang", "ranged", "past_tense"),
        ("rang", "ranging", "present_participle"),
        ("rang", "ranged", "past_participle"),
        ("rang", "ranger", "agent_noun"),
        ("breath", "breathed", "past_tense"),
        ("breath", "breathing", "present_participle"),
        ("breath", "breathed", "past_participle"),
        ("breath", "breather", "agent_noun"),
        ("breath", "breathable", "derivation"),
        ("bath", "bathed", "past_tense"),
        ("bath", "bathing", "present_participle"),
        ("bath", "bathed", "past_participle"),
        ("bath", "bather", "agent_noun"),
        ("cloth", "clothing", "present_participle"),
        ("cleans", "cleansing", "present_participle"),
        ("cleans", "cleanser", "agent_noun"),
        ("claus", "clauses", "inflection"),
        ("breez", "breezes", "inflection"),
        ("breez", "breezed", "past_tense"),
        ("breez", "breezed", "past_participle"),
        ("evolv", "evolved", "past_tense"),
        ("evolv", "evolving", "present_participle"),
        ("evolv", "evolved", "past_participle"),
        ("laps", "lapses", "inflection"),
        ("laps", "lapsed", "past_tense"),
        ("laps", "lapsed", "past_participle"),
        ("banke", "banked", "past_tense"),
        ("banke", "banking", "present_participle"),
        ("banke", "banked", "past_participle"),
        ("banke", "banker", "agent_noun"),
        ("banke", "bankable", "derivation"),
        ("calle", "called", "past_tense"),
        ("calle", "calling", "present_participle"),
        ("calle", "called", "past_participle"),
        ("calle", "caller", "agent_noun"),
        ("calle", "callous", "derivation"),
        ("parke", "parkes", "inflection"),
        ("parke", "parked", "past_tense"),
        ("parke", "parking", "present_participle"),
        ("parke", "parked", "past_participle"),
        ("parke", "parker", "agent_noun"),
        ("cooper", "cooperation", "derivation"),
        ("opera", "operation", "derivation"),
        ("chant", "chantal", "derivation"),
        ("supple", "supplement", "derivation"),
        ("prof", "proves", "inflection"),
        ("prof", "proffer", "agent_noun"),
        ("fife", "fives", "inflection"),
        ("hung", "hunger", "agent_noun"),
        ("latte", "latter", "agent_noun"),
        ("ledge", "ledger", "agent_noun"),
        ("numb", "number", "agent_noun"),
        ("ginge", "ginger", "agent_noun"),
        ("hamm", "hammer", "agent_noun"),
        ("ladd", "ladder", "agent_noun"),
        ("stag", "stagger", "agent_noun"),
        ("stagg", "stagger", "agent_noun"),
        ("antle", "antler", "agent_noun"),
        ("pande", "pander", "agent_noun"),
        ("pape", "paper", "agent_noun"),
        ("rive", "river", "agent_noun"),
        ("state", "stable", "derivation"),
        ("state", "station", "derivation"),
        ("state", "static", "derivation"),
        ("later", "lateral", "derivation"),
        ("media", "mediation", "derivation"),
        ("severe", "severed", "past_tense"),
        ("severe", "severed", "past_participle"),
        ("severe", "severance", "derivation"),
        ("finale", "finalist", "agent_noun"),
        ("finale", "finalise", "derivation"),
        ("finale", "finalize", "derivation"),
        ("monopole", "monopoly", "derivation"),
        ("overs", "oversize", "derivation"),
        ("frant", "frantic", "derivation"),
        ("marti", "martial", "derivation"),
        ("porte", "ported", "past_tense"),
        ("porte", "ported", "past_participle"),
        ("porte", "porting", "present_participle"),
        ("porte", "portable", "derivation"),
        ("porte", "portal", "derivation"),
        ("rationale", "rationality", "derivation"),
        ("humane", "humanity", "derivation"),
        ("coole", "cooled", "past_tense"),
        ("coole", "cooled", "past_participle"),
        ("coole", "cooler", "comparative"),
        ("coole", "coolest", "superlative"),
        ("coole", "cooly", "derivation"),
        ("wilde", "wildes", "inflection"),
        ("wilde", "wilding", "present_participle"),
        ("wilde", "wilder", "comparative"),
        ("wilde", "wildest", "superlative"),
        ("sharpe", "sharper", "comparative"),
        ("sharpe", "sharpest", "superlative"),
        ("leane", "leaned", "past_tense"),
        ("leane", "leaning", "present_participle"),
        ("leane", "leaned", "past_participle"),
        ("leane", "leaner", "comparative"),
        ("leane", "leanest", "superlative"),
        ("riche", "riches", "inflection"),
        ("riche", "richer", "comparative"),
        ("riche", "richest", "superlative"),
        ("bigg", "biggs", "inflection"),
        ("bigg", "bigger", "comparative"),
        ("bigg", "biggest", "superlative"),
        ("dens", "denser", "comparative"),
        ("dens", "densest", "superlative"),
        ("tempe", "temper", "comparative"),
        ("tempe", "tempest", "superlative"),
        ("sens", "senses", "inflection"),
        ("sens", "sensed", "past_tense"),
        ("sens", "sensing", "present_participle"),
        ("writ", "writer", "agent_noun"),
        ("mobil", "mobility", "derivation"),
        ("mobil", "mobilise", "derivation"),
        ("mobil", "mobilize", "derivation"),
        ("plan", "planer", "agent_noun"),
        ("suite", "suited", "past_tense"),
        ("suite", "suiting", "present_participle"),
        ("suite", "suited", "past_participle"),
        ("suite", "suitable", "derivation"),
        ("suite", "suitor", "agent_noun"),
        ("machin", "machination", "derivation"),
    }
)

IRREGULAR_FAMILIES: dict[str, tuple[tuple[str, str], ...]] = {
    "be": (
        ("am", "inflection"),
        ("is", "inflection"),
        ("are", "inflection"),
        ("was", "past_tense"),
        ("were", "past_tense"),
        ("been", "past_participle"),
        ("being", "present_participle"),
    ),
    "have": (("has", "inflection"), ("had", "past_tense"), ("having", "present_participle")),
    "do": (
        ("does", "inflection"),
        ("did", "past_tense"),
        ("done", "past_participle"),
        ("doing", "present_participle"),
    ),
    "go": (
        ("goes", "inflection"),
        ("went", "past_tense"),
        ("gone", "past_participle"),
        ("going", "present_participle"),
    ),
    "say": (("says", "inflection"), ("said", "past_tense"), ("saying", "present_participle")),
    "make": (("makes", "inflection"), ("made", "past_tense"), ("making", "present_participle")),
    "take": (
        ("takes", "inflection"),
        ("took", "past_tense"),
        ("taken", "past_participle"),
        ("taking", "present_participle"),
    ),
    "come": (("comes", "inflection"), ("came", "past_tense"), ("coming", "present_participle")),
    "see": (
        ("sees", "inflection"),
        ("saw", "past_tense"),
        ("seen", "past_participle"),
        ("seeing", "present_participle"),
    ),
    "know": (
        ("knows", "inflection"),
        ("knew", "past_tense"),
        ("known", "past_participle"),
        ("knowing", "present_participle"),
    ),
    "get": (
        ("gets", "inflection"),
        ("got", "past_tense"),
        ("gotten", "past_participle"),
        ("getting", "present_participle"),
    ),
    "give": (
        ("gives", "inflection"),
        ("gave", "past_tense"),
        ("given", "past_participle"),
        ("giving", "present_participle"),
    ),
    "find": (("finds", "inflection"), ("found", "past_tense"), ("finding", "present_participle")),
    "think": (
        ("thinks", "inflection"),
        ("thought", "past_tense"),
        ("thinking", "present_participle"),
    ),
    "tell": (("tells", "inflection"), ("told", "past_tense"), ("telling", "present_participle")),
    "feel": (("feels", "inflection"), ("felt", "past_tense"), ("feeling", "present_participle")),
    "leave": (("leaves", "inflection"), ("left", "past_tense"), ("leaving", "present_participle")),
    "keep": (("keeps", "inflection"), ("kept", "past_tense"), ("keeping", "present_participle")),
    "bring": (("brings", "inflection"), ("brought", "past_tense"), ("bringing", "present_participle")),
    "buy": (("buys", "inflection"), ("bought", "past_tense"), ("buying", "present_participle")),
    "sell": (("sells", "inflection"), ("sold", "past_tense"), ("selling", "present_participle")),
    "pay": (("pays", "inflection"), ("paid", "past_tense"), ("paying", "present_participle")),
    "can": (
        ("cans", "inflection"),
        ("canned", "past_tense"),
        ("canned", "past_participle"),
        ("canning", "present_participle"),
    ),
    "run": (
        ("runs", "inflection"),
        ("ran", "past_tense"),
        ("running", "present_participle"),
        ("runner", "agent_noun"),
    ),
    "try": (("tries", "inflection"), ("tried", "past_tense"), ("tried", "past_participle"), ("trying", "present_participle")),
    "tax": (("taxes", "inflection"), ("taxed", "past_tense"), ("taxed", "past_participle"), ("taxing", "present_participle")),
    "fix": (("fixes", "inflection"), ("fixed", "past_tense"), ("fixed", "past_participle"), ("fixing", "present_participle")),
    "mix": (("mixes", "inflection"), ("mixed", "past_tense"), ("mixed", "past_participle"), ("mixing", "present_participle")),
    "box": (("boxes", "inflection"), ("boxed", "past_tense"), ("boxed", "past_participle"), ("boxing", "present_participle")),
    "begin": (
        ("begins", "inflection"),
        ("began", "past_tense"),
        ("begun", "past_participle"),
        ("beginning", "present_participle"),
    ),
    "win": (("wins", "inflection"), ("won", "past_tense"), ("winning", "present_participle")),
    "write": (
        ("writes", "inflection"),
        ("wrote", "past_tense"),
        ("written", "past_participle"),
        ("writing", "present_participle"),
    ),
    "read": (("reads", "inflection"), ("reading", "present_participle")),
    "meet": (("meets", "inflection"), ("met", "past_tense"), ("meeting", "present_participle")),
    "lead": (("leads", "inflection"), ("led", "past_tense"), ("leading", "present_participle")),
    "lose": (("loses", "inflection"), ("lost", "past_tense"), ("losing", "present_participle")),
    "sit": (("sits", "inflection"), ("sat", "past_tense"), ("sitting", "present_participle")),
    "stand": (("stands", "inflection"), ("stood", "past_tense"), ("standing", "present_participle")),
    "break": (
        ("breaks", "inflection"),
        ("broke", "past_tense"),
        ("broken", "past_participle"),
        ("breaking", "present_participle"),
    ),
    "speak": (
        ("speaks", "inflection"),
        ("spoke", "past_tense"),
        ("spoken", "past_participle"),
        ("speaking", "present_participle"),
    ),
    "grow": (
        ("grows", "inflection"),
        ("grew", "past_tense"),
        ("grown", "past_participle"),
        ("growing", "present_participle"),
    ),
    "draw": (
        ("draws", "inflection"),
        ("drew", "past_tense"),
        ("drawn", "past_participle"),
        ("drawing", "present_participle"),
    ),
    "choose": (
        ("chooses", "inflection"),
        ("chose", "past_tense"),
        ("chosen", "past_participle"),
        ("choosing", "present_participle"),
    ),
    "fall": (
        ("falls", "inflection"),
        ("fell", "past_tense"),
        ("fallen", "past_participle"),
        ("falling", "present_participle"),
    ),
    "eat": (
        ("eats", "inflection"),
        ("ate", "past_tense"),
        ("eaten", "past_participle"),
        ("eating", "present_participle"),
    ),
    "good": (("better", "comparative"), ("best", "superlative")),
    "well": (("better", "comparative"), ("best", "superlative")),
    "bad": (("worse", "comparative"), ("worst", "superlative")),
    "far": (
        ("farther", "comparative"),
        ("farthest", "superlative"),
        ("further", "comparative"),
        ("furthest", "superlative"),
    ),
    "little": (("less", "comparative"), ("least", "superlative")),
    "many": (("more", "comparative"), ("most", "superlative")),
    "much": (("more", "comparative"), ("most", "superlative")),
    "old": (
        ("older", "comparative"),
        ("oldest", "superlative"),
        ("elder", "comparative"),
        ("eldest", "superlative"),
    ),
    "man": (("men", "inflection"),),
    "woman": (("women", "inflection"),),
    "person": (("people", "inflection"),),
    "child": (("children", "inflection"),),
    "life": (("lives", "inflection"),),
    "leaf": (("leaves", "inflection"),),
    "knife": (("knives", "inflection"),),
    "datum": (("data", "inflection"),),
}

REVIEW_IRREGULAR_FAMILIES: dict[str, tuple[tuple[str, str], ...]] = {
    "become": (("became", "past_tense"), ("become", "past_participle")),
    "bend": (("bent", "past_tense"), ("bent", "past_participle")),
    "bind": (("bound", "past_tense"), ("bound", "past_participle")),
    "bite": (("bit", "past_tense"), ("bitten", "past_participle")),
    "bleed": (("bled", "past_tense"), ("bled", "past_participle")),
    "blow": (("blew", "past_tense"), ("blown", "past_participle")),
    "bring": (("brought", "past_participle"),),
    "build": (("built", "past_tense"), ("built", "past_participle")),
    "buy": (("bought", "past_participle"),),
    "catch": (("caught", "past_tense"), ("caught", "past_participle")),
    "come": (("come", "past_participle"),),
    "cost": (("cost", "past_tense"), ("cost", "past_participle")),
    "deal": (("dealt", "past_tense"), ("dealt", "past_participle")),
    "drink": (("drank", "past_tense"), ("drunk", "past_participle")),
    "drive": (("drove", "past_tense"), ("driven", "past_participle")),
    "feed": (("fed", "past_tense"), ("fed", "past_participle")),
    "feel": (("felt", "past_participle"),),
    "fight": (("fought", "past_tense"), ("fought", "past_participle")),
    "find": (("found", "past_participle"),),
    "forget": (("forgot", "past_tense"), ("forgotten", "past_participle")),
    "forgive": (("forgave", "past_tense"), ("forgiven", "past_participle")),
    "freeze": (("froze", "past_tense"), ("frozen", "past_participle")),
    "get": (("got", "past_participle"),),
    "hang": (("hung", "past_tense"), ("hung", "past_participle"), ("hanged", "past_participle")),
    "have": (("had", "past_participle"),),
    "hear": (("heard", "past_tense"), ("heard", "past_participle")),
    "hide": (("hid", "past_tense"), ("hid", "past_participle"), ("hidden", "past_participle")),
    "hold": (("held", "past_tense"), ("held", "past_participle")),
    "hurt": (("hurt", "past_tense"), ("hurt", "past_participle")),
    "keep": (("kept", "past_participle"),),
    "lead": (("led", "past_participle"),),
    "leave": (("left", "past_participle"),),
    "lend": (("lent", "past_tense"), ("lent", "past_participle")),
    "light": (("lit", "past_tense"), ("lit", "past_participle"), ("lighted", "past_tense"), ("lighted", "past_participle")),
    "lose": (("lost", "past_participle"),),
    "make": (("made", "past_participle"),),
    "mean": (("meant", "past_tense"), ("meant", "past_participle")),
    "meet": (("met", "past_participle"),),
    "pay": (("paid", "past_participle"),),
    "read": (("read", "past_tense"), ("read", "past_participle")),
    "ride": (("rode", "past_tense"), ("ridden", "past_participle")),
    "ring": (("rang", "past_tense"), ("rung", "past_participle")),
    "rise": (("rose", "past_tense"), ("risen", "past_participle")),
    "run": (("run", "past_participle"),),
    "say": (("said", "past_participle"),),
    "seek": (("sought", "past_tense"), ("sought", "past_participle")),
    "sell": (("sold", "past_participle"),),
    "send": (("sent", "past_tense"), ("sent", "past_participle")),
    "shake": (("shook", "past_tense"), ("shaken", "past_participle")),
    "shine": (("shone", "past_tense"), ("shone", "past_participle"), ("shined", "past_participle")),
    "shoot": (("shot", "past_tense"), ("shot", "past_participle")),
    "show": (("shown", "past_participle"), ("showed", "past_participle")),
    "shrink": (("shrank", "past_tense"), ("shrunk", "past_tense"), ("shrunk", "past_participle")),
    "shut": (("shut", "past_tense"), ("shut", "past_participle")),
    "sing": (("sang", "past_tense"), ("sung", "past_participle")),
    "sink": (("sank", "past_tense"), ("sunk", "past_tense"), ("sunk", "past_participle")),
    "sit": (("sat", "past_participle"),),
    "sleep": (("slept", "past_tense"), ("slept", "past_participle")),
    "spend": (("spent", "past_tense"), ("spent", "past_participle")),
    "spin": (("spun", "past_tense"), ("spun", "past_participle")),
    "split": (("split", "past_tense"), ("split", "past_participle")),
    "spread": (("spread", "past_tense"), ("spread", "past_participle")),
    "spring": (("sprang", "past_tense"), ("sprung", "past_tense"), ("sprung", "past_participle")),
    "stand": (("stood", "past_participle"),),
    "steal": (("stole", "past_tense"), ("stolen", "past_participle")),
    "stick": (("stuck", "past_tense"), ("stuck", "past_participle")),
    "strike": (("struck", "past_tense"), ("struck", "past_participle"), ("stricken", "past_participle")),
    "swim": (("swam", "past_tense"), ("swum", "past_participle")),
    "teach": (("taught", "past_tense"), ("taught", "past_participle")),
    "tear": (("tore", "past_tense"), ("torn", "past_participle")),
    "tell": (("told", "past_participle"),),
    "think": (("thought", "past_participle"),),
    "throw": (("threw", "past_tense"), ("thrown", "past_participle")),
    "understand": (("understood", "past_tense"), ("understood", "past_participle")),
    "wake": (("woke", "past_tense"), ("waked", "past_tense"), ("woken", "past_participle"), ("waked", "past_participle")),
    "wear": (("wore", "past_tense"), ("worn", "past_participle")),
    "win": (("won", "past_participle"),),
}

for lemma, reviewed_forms in REVIEW_IRREGULAR_FAMILIES.items():
    IRREGULAR_FAMILIES[lemma] = IRREGULAR_FAMILIES.get(lemma, ()) + reviewed_forms

SHORT_IRREGULAR_WORDS = frozenset(
    word
    for family in IRREGULAR_FAMILIES.values()
    for word, _relation in family
    if len(word) < 3
) | frozenset(word for word in IRREGULAR_FAMILIES if len(word) < 3)

PREFIXES = (
    "un",
    "re",
    "pre",
    "post",
    "non",
    "anti",
    "counter",
    "over",
    "under",
    "out",
    "mis",
    "dis",
    "de",
    "co",
    "inter",
    "intra",
    "extra",
    "trans",
    "sub",
    "super",
    "micro",
    "macro",
    "multi",
    "auto",
    "semi",
    "proto",
    "neo",
)

DIALECT_VARIANTS = (
    ("color", "colour"),
    ("honor", "honour"),
    ("labor", "labour"),
    ("center", "centre"),
    ("theater", "theatre"),
    ("meter", "metre"),
    ("liter", "litre"),
    ("fiber", "fibre"),
    ("defense", "defence"),
    ("offense", "offence"),
    ("license", "licence"),
    ("practice", "practise"),
    ("organize", "organise"),
    ("analyze", "analyse"),
    ("catalog", "catalogue"),
    ("dialog", "dialogue"),
    ("gray", "grey"),
    ("mold", "mould"),
    ("plow", "plough"),
    ("draft", "draught"),
    ("check", "cheque"),
    ("tire", "tyre"),
    ("curb", "kerb"),
    ("program", "programme"),
)

CLASSICAL_PLURALS: dict[str, tuple[str, ...]] = {
    "analysis": ("analyses",),
    "basis": ("bases",),
    "bacterium": ("bacteria",),
    "consortium": ("consortia",),
    "corpus": ("corpora",),
    "criterion": ("criteria",),
    "crisis": ("crises",),
    "diagnosis": ("diagnoses",),
    "focus": ("foci",),
    "formula": ("formulae",),
    "fungus": ("fungi",),
    "index": ("indices",),
    "medium": ("media",),
    "millennium": ("millennia",),
    "nemesis": ("nemeses",),
    "paralysis": ("paralyses",),
    "phenomenon": ("phenomena",),
    "quantum": ("quanta",),
    "spectrum": ("spectra",),
    "stigma": ("stigmata",),
}

PLACE_ADJECTIVE_BASES: dict[str, tuple[str, ...]] = {
    "africa": ("african",),
    "america": ("american",),
    "asia": ("asian",),
    "brazil": ("brazilian",),
    "canada": ("canadian",),
    "europe": ("european",),
    "india": ("indian",),
    "iraq": ("iraqi",),
    "italy": ("italian",),
    "japan": ("japanese",),
}

NEGATIVE_PREFIX_DERIVATIONS: dict[str, tuple[str, ...]] = {
    "able": ("unable",),
    "active": ("inactive",),
    "affordable": ("unaffordable",),
    "aware": ("unaware",),
    "comfortable": ("uncomfortable",),
    "common": ("uncommon",),
    "effective": ("ineffective",),
    "happy": ("unhappy",),
    "healthy": ("unhealthy",),
    "legal": ("illegal",),
    "necessary": ("unnecessary",),
    "official": ("unofficial",),
    "popular": ("unpopular",),
    "possible": ("impossible",),
    "profit": ("nonprofit",),
    "regular": ("irregular",),
    "responsible": ("irresponsible",),
    "safe": ("unsafe",),
    "social": ("antisocial",),
    "successful": ("unsuccessful",),
    "visible": ("invisible",),
}

DERIVATIONAL_COLLISION_KEEPERS: frozenset[tuple[str, str, str]] = frozenset(
    {
        ("academy", "academic", "derivation"),
        ("academia", "academic", "derivation"),
        ("biology", "biological", "derivation"),
        ("biologic", "biological", "derivation"),
        ("commune", "communism", "derivation"),
        ("commune", "communist", "agent_noun"),
        ("journal", "journalism", "derivation"),
        ("journal", "journalist", "agent_noun"),
        ("lyric", "lyricism", "derivation"),
        ("lyric", "lyricist", "agent_noun"),
        ("oligarch", "oligarchic", "derivation"),
        ("realist", "realistic", "derivation"),
        ("terror", "terrorism", "derivation"),
        ("terror", "terrorist", "agent_noun"),
        ("tour", "tourist", "agent_noun"),
        ("tourism", "tourist", "agent_noun"),
    }
)

KNOWN_FAMILY_EDGES: dict[str, tuple[tuple[str, str], ...]] = {
    "academia": (("academic", "derivation"),),
    "biologic": (("biological", "derivation"),),
    "commune": (("communism", "derivation"), ("communist", "agent_noun")),
    "confide": (("confidence", "derivation"),),
    "confident": (("confidence", "derivation"),),
    "cute": (("cutest", "superlative"),),
    "dirty": (("dirtiest", "superlative"),),
    "dumb": (("dumbest", "superlative"),),
    "fabricate": (("fabrication", "derivation"),),
    "faint": (("faintest", "superlative"),),
    "flaky": (("flakiest", "superlative"),),
    "fond": (("fondest", "superlative"),),
    "funny": (("funniest", "superlative"),),
    "grumpy": (("grumpiest", "superlative"),),
    "halves": (("halve", "lemma"),),
    "holy": (("holiest", "superlative"),),
    "journal": (("journalism", "derivation"), ("journalist", "agent_noun")),
    "likely": (("likeliest", "superlative"),),
    "lyric": (("lyricism", "derivation"), ("lyricist", "agent_noun")),
    "lucky": (("luckiest", "superlative"),),
    "oligarch": (("oligarchic", "derivation"),),
    "perceive": (("perceptive", "derivation"),),
    "practice": (("practicable", "derivation"),),
    "precede": (("precedence", "derivation"),),
    "pretty": (("prettiest", "superlative"),),
    "pure": (("purest", "superlative"),),
    "receive": (("receivable", "derivation"),),
    "reduce": (("reductive", "derivation"),),
    "repel": (("repulsion", "derivation"),),
    "realist": (("realistic", "derivation"),),
    "rude": (("rudest", "superlative"),),
    "sick": (("sickest", "superlative"),),
    "silly": (("silliest", "superlative"),),
    "slight": (("slightest", "superlative"),),
    "subtle": (("subtlest", "superlative"),),
    "tasty": (("tastiest", "superlative"),),
    "tiny": (("tiniest", "superlative"),),
    "tour": (("tourist", "agent_noun"),),
    "terror": (("terrorism", "derivation"), ("terrorist", "agent_noun")),
    "transmit": (("transmissive", "derivation"),),
    "ugly": (("ugliest", "superlative"),),
}


@dataclass(frozen=True)
class LexiconWord:
    surface: str
    normalized: str
    frequency: float
    order: int


@dataclass(frozen=True)
class Candidate:
    related: str
    relation: str
    confidence: int


@dataclass(frozen=True)
class ScoredRow:
    lemma: str
    variant: str
    relation: str
    confidence: int
    score: float
    base_frequency: float
    variant_frequency: float
    base_order: int
    variant_order: int


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate en_US word-family variants.")
    parser.add_argument("--lexicon", type=Path, default=DEFAULT_LEXICON)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    words = read_lexicon(args.lexicon)
    rows = tuple(generate_rows(words, expanded_builtin_denylist()))
    write_rows(args.output, rows)
    print(f"generated {len(rows)} variants from {len(words)} lexicon words")
    return 0


def read_lexicon(path: Path) -> tuple[LexiconWord, ...]:
    words_by_normalized: dict[str, LexiconWord] = {}
    with path.open(encoding="utf-8", newline="") as input_file:
        reader = csv.reader(input_file, delimiter="\t")
        for order, row in enumerate(reader):
            if len(row) < 2:
                continue
            surface = row[0].strip()
            normalized = normalize_word(surface)
            if normalized is None:
                continue
            try:
                frequency = float(row[1])
            except ValueError:
                continue
            word = LexiconWord(surface=surface, normalized=normalized, frequency=frequency, order=order)
            existing = words_by_normalized.get(normalized)
            if existing is None or word_key(word) < word_key(existing):
                words_by_normalized[normalized] = word
    return tuple(sorted(words_by_normalized.values(), key=lambda word: word.order))


def read_frequency_file(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    frequencies: dict[str, float] = {}
    with path.open(encoding="utf-8", newline="") as input_file:
        reader = csv.reader(input_file, delimiter="\t")
        for row in reader:
            if len(row) < 3:
                continue
            normalized = normalize_word(row[1].strip())
            if normalized is None:
                continue
            try:
                frequency = float(row[2])
            except ValueError:
                continue
            frequencies[normalized] = max(frequencies.get(normalized, 0.0), frequency)
    return frequencies


def expanded_builtin_denylist() -> frozenset[tuple[str, str, str]]:
    rows: set[tuple[str, str, str]] = set()
    for lemma, variant, relation in BUILTIN_DENYLIST:
        rows.add((lemma, variant, relation))
        rows.add((lemma, variant, "*"))
    return frozenset(rows)


def generate_rows(
    words: tuple[LexiconWord, ...],
    denylist: frozenset[tuple[str, str, str]],
) -> Iterator[tuple[str, str, str]]:
    words_by_normalized = {word.normalized: word for word in words}
    scored_rows: list[ScoredRow] = []
    for base in words:
        candidates = validated_candidates(base.normalized, words_by_normalized)
        for candidate in candidates[:MAX_VARIANTS_PER_BASE]:
            row = (base.normalized, candidate.related, candidate.relation)
            if row in denylist or (row[0], row[1], "*") in denylist:
                continue
            scored_rows.append(score_row(base, candidate, words_by_normalized))

    emitted: set[tuple[str, str, str]] = set()
    for scored_row in resolve_collisions(scored_rows, words_by_normalized):
        row = (scored_row.lemma, scored_row.variant, scored_row.relation)
        if row not in emitted:
            emitted.add(row)
            yield row


def score_row(
    base: LexiconWord,
    candidate: Candidate,
    words_by_normalized: dict[str, LexiconWord],
) -> ScoredRow:
    variant = words_by_normalized.get(
        candidate.related,
        LexiconWord(candidate.related, candidate.related, 0.0, 10_000_000),
    )
    score = float(candidate.confidence)
    score += frequency_score(base.frequency) * 5.0
    score += frequency_score(variant.frequency) * 2.0
    if base.frequency <= 1.0 and candidate.confidence < 100:
        score -= 8.0
    if suspicious_final_e_base(base.normalized, words_by_normalized) and candidate.confidence < 100:
        score -= 12.0
    if len(base.normalized) <= 4 and candidate.confidence < 100:
        score -= 4.0
    return ScoredRow(
        lemma=base.normalized,
        variant=candidate.related,
        relation=candidate.relation,
        confidence=candidate.confidence,
        score=score,
        base_frequency=base.frequency,
        variant_frequency=variant.frequency,
        base_order=base.order,
        variant_order=variant.order,
    )


def resolve_collisions(
    rows: Iterable[ScoredRow],
    words_by_normalized: dict[str, LexiconWord],
) -> tuple[ScoredRow, ...]:
    rows_by_variant_relation: dict[tuple[str, str], list[ScoredRow]] = {}
    for row in rows:
        rows_by_variant_relation.setdefault((row.variant, row.relation), []).append(row)

    kept: list[ScoredRow] = []
    for group in rows_by_variant_relation.values():
        if len(group) == 1:
            kept.extend(group)
            continue
        best = max(group, key=collision_sort_key)
        for row in group:
            if row.confidence >= 100:
                kept.append(row)
            elif row == best:
                kept.append(row)
            elif should_keep_collision(row, best, words_by_normalized):
                kept.append(row)

    return tuple(sorted(kept, key=output_sort_key))


def should_keep_collision(
    row: ScoredRow,
    best: ScoredRow,
    words_by_normalized: dict[str, LexiconWord],
) -> bool:
    if (row.lemma, row.variant, row.relation) in DERIVATIONAL_COLLISION_KEEPERS:
        return True
    if row.lemma.endswith("e") and row.lemma[:-1] in words_by_normalized:
        return row.confidence >= 90 or row.score >= best.score - 30.0
    if row.confidence >= 90 and row.score >= best.score - 30.0:
        return True
    if row.confidence >= 90 and row.base_frequency >= 5.0:
        return True
    if row.confidence >= 90 and best.confidence < 100 and row.score >= best.score - 8.0:
        return True
    if row.score >= best.score - 8.0:
        return True
    if row.confidence == best.confidence and row.base_frequency >= best.base_frequency / 3.0:
        return True
    if row.base_frequency <= 1.0 and best.base_frequency >= 5.0:
        return False
    return row.score >= best.score - 16.0


def collision_sort_key(row: ScoredRow) -> tuple[float, int, float, int]:
    return (row.score, row.confidence, row.base_frequency, -row.base_order)


def output_sort_key(row: ScoredRow) -> tuple[int, int, int, str, str]:
    return (
        row.base_order,
        -row.confidence,
        relation_order(row.relation),
        row.variant,
        row.relation,
    )


def validated_candidates(
    base: str,
    words_by_normalized: dict[str, LexiconWord],
) -> tuple[Candidate, ...]:
    candidates: dict[tuple[str, str], Candidate] = {}
    base_profile = profile_base(base, words_by_normalized)
    for candidate in candidate_variants(base):
        if candidate.related == base and candidate.confidence < 100:
            continue
        if candidate.related not in words_by_normalized and candidate.confidence < 100:
            continue
        candidate = refine_candidate_relation(candidate, base_profile)
        if not plausible_pair(base, candidate, base_profile):
            continue
        key = (candidate.related, candidate.relation)
        existing = candidates.get(key)
        if existing is None or candidate_sort_key(candidate) < candidate_sort_key(existing):
            candidates[key] = candidate
    return tuple(
        sorted(
            candidates.values(),
            key=lambda candidate: (
                -candidate.confidence,
                relation_order(candidate.relation),
                words_by_normalized.get(
                    candidate.related,
                    LexiconWord(candidate.related, candidate.related, 0.0, 10_000_000),
                ).order,
                candidate.related,
            ),
        )
    )


@dataclass(frozen=True)
class BaseProfile:
    has_verb_forms: bool
    has_comparative_form: bool
    has_superlative_form: bool


def profile_base(base: str, words_by_normalized: dict[str, LexiconWord]) -> BaseProfile:
    return BaseProfile(
        has_verb_forms=(
            past_tense(base) in words_by_normalized
            or present_participle(base) in words_by_normalized
            or base in IRREGULAR_FAMILIES
        ),
        has_comparative_form=comparative(base) in words_by_normalized,
        has_superlative_form=superlative(base) in words_by_normalized,
    )


def refine_candidate_relation(candidate: Candidate, profile: BaseProfile) -> Candidate:
    if candidate.confidence >= 100:
        return candidate
    if candidate.relation == "agent_noun" and profile.has_superlative_form:
        return Candidate(candidate.related, "comparative", candidate.confidence + 4)
    return candidate


def candidate_sort_key(candidate: Candidate) -> tuple[int, int, str]:
    return (-candidate.confidence, relation_order(candidate.relation), candidate.related)


def relation_order(relation: str) -> int:
    return {
        "inflection": 0,
        "past_tense": 1,
        "past_participle": 2,
        "present_participle": 3,
        "comparative": 4,
        "superlative": 5,
        "agent_noun": 6,
        "lemma": 7,
        "spelling_variant": 8,
        "derivation": 9,
    }.get(relation, 99)


def candidate_variants(base: str) -> Iterator[Candidate]:
    for related, relation in IRREGULAR_FAMILIES.get(base, ()):
        yield Candidate(related, relation, 100)
    for related in CLASSICAL_PLURALS.get(base, ()):
        yield Candidate(related, "inflection", 100)
    for related, relation in KNOWN_FAMILY_EDGES.get(base, ()):
        yield Candidate(related, relation, 100)

    if base not in PRODUCTIVE_STOPWORDS and len(base) >= 4:
        yield from inflection_candidates(base)
        yield from classical_plural_candidates(base)
        yield from comparison_candidates(base)
        yield from adverb_candidates(base)
    if base not in PRODUCTIVE_STOPWORDS and len(base) >= 4:
        yield from derivation_candidates(base)
        yield from dialect_candidates(base)
        yield from prefixed_candidates(base)


def inflection_candidates(base: str) -> Iterator[Candidate]:
    yield Candidate(plural_or_third_person(base), "inflection", 90)
    yield Candidate(past_tense(base), "past_tense", 90)
    yield Candidate(past_tense(base), "past_participle", 82)
    yield Candidate(present_participle(base), "present_participle", 90)
    yield Candidate(agent_noun(base), "agent_noun", 74)


def classical_plural_candidates(base: str) -> Iterator[Candidate]:
    for related in CLASSICAL_PLURALS.get(base, ()):
        yield Candidate(related, "inflection", 100)


def comparison_candidates(base: str) -> Iterator[Candidate]:
    yield Candidate(comparative(base), "comparative", 82)
    yield Candidate(superlative(base), "superlative", 82)


def adverb_candidates(base: str) -> Iterator[Candidate]:
    yield Candidate(adverb(base), "derivation", 72)
    yield Candidate(f"{base}wise", "derivation", 54)
    yield Candidate(f"{base}ward", "derivation", 54)
    yield Candidate(f"{base}wards", "derivation", 54)


def derivation_candidates(base: str) -> Iterator[Candidate]:
    yield from negative_prefix_derivation_candidates(base)
    yield from place_adjective_candidates(base)
    yield from ify_specific_adjective_candidates(base)
    yield from final_y_adjective_candidates(base)
    yield from ism_family_candidates(base)

    suffixes = (
        ("ness", "derivation", 70),
        ("ment", "derivation", 68),
        ("less", "derivation", 68),
        ("ful", "derivation", 68),
        ("able", "derivation", 66),
        ("ible", "derivation", 58),
        ("al", "derivation", 62),
        ("ial", "derivation", 58),
        ("ic", "derivation", 62),
        ("ical", "derivation", 62),
        ("ive", "derivation", 62),
        ("ous", "derivation", 58),
        ("ity", "derivation", 62),
        ("ism", "derivation", 58),
        ("ist", "agent_noun", 58),
        ("er", "agent_noun", 70),
        ("or", "agent_noun", 62),
        ("tion", "derivation", 58),
        ("sion", "derivation", 58),
        ("ation", "derivation", 62),
        ("ence", "derivation", 58),
        ("ance", "derivation", 58),
        ("ship", "derivation", 54),
        ("hood", "derivation", 54),
        ("dom", "derivation", 54),
        ("ize", "derivation", 58),
        ("ise", "derivation", 58),
        ("ify", "derivation", 58),
    )
    for suffix, relation, confidence in suffixes:
        yield Candidate(apply_suffix(base, suffix), relation, confidence)
    yield from latinate_candidates(base)
    yield from germanic_candidates(base)
    yield from greek_candidates(base)


def negative_prefix_derivation_candidates(base: str) -> Iterator[Candidate]:
    for related in NEGATIVE_PREFIX_DERIVATIONS.get(base, ()):
        yield Candidate(related, "derivation", 88)


def place_adjective_candidates(base: str) -> Iterator[Candidate]:
    if base not in PLACE_ADJECTIVE_BASES:
        return

    for related in PLACE_ADJECTIVE_BASES[base]:
        yield Candidate(related, "derivation", 88)


def final_y_adjective_candidates(base: str) -> Iterator[Candidate]:
    if len(base) < 5 or not base.endswith("y") or base.endswith("ify"):
        return

    stem = base[:-1]
    yield Candidate(f"{stem}ic", "derivation", 76)
    yield Candidate(f"{stem}ical", "derivation", 74)


def ify_specific_adjective_candidates(base: str) -> Iterator[Candidate]:
    if len(base) <= 5 or not base.endswith("ify"):
        return

    yield Candidate(f"{base[:-3]}ific", "derivation", 78)


def ism_family_candidates(base: str) -> Iterator[Candidate]:
    if base.endswith("ism") and len(base) > 5:
        stem = base[:-3]
        yield Candidate(f"{stem}ist", "agent_noun", 76)
        yield Candidate(f"{stem}istic", "derivation", 72)
    if base.endswith("ist") and len(base) > 5:
        stem = base[:-3]
        yield Candidate(f"{stem}ism", "derivation", 76)
        yield Candidate(f"{base}ic", "derivation", 72)


def dialect_candidates(base: str) -> Iterator[Candidate]:
    for left, right in DIALECT_VARIANTS:
        if base == left:
            yield Candidate(right, "spelling_variant", 84)
        elif base == right:
            yield Candidate(left, "spelling_variant", 84)


def prefixed_candidates(base: str) -> Iterator[Candidate]:
    for prefix in PREFIXES:
        yield Candidate(f"{prefix}{base}", "derivation", 46)
    for prefix in PREFIXES:
        if base.startswith(prefix) and len(base) > len(prefix) + 3:
            yield Candidate(base.removeprefix(prefix), "lemma", 44)
    for prefix, assimilated in (("in", "im"), ("in", "il"), ("in", "ir")):
        if base.startswith(prefix):
            stem = base.removeprefix(prefix)
            yield Candidate(f"{assimilated}{stem}", "derivation", 46)


def latinate_candidates(base: str) -> Iterator[Candidate]:
    replacements = (
        ("ate", ("ation", "ative", "ator", "atory", "able")),
        ("ify", ("ification", "ifier", "ifiable")),
        ("ize", ("ization", "izer", "izable")),
        ("ise", ("isation", "iser", "isable")),
        ("able", ("ability",)),
        ("ible", ("ibility",)),
        ("ic", ("icity", "ical", "ics")),
        ("ive", ("ivity",)),
        ("ous", ("osity",)),
        ("al", ("ality",)),
        ("ar", ("arity",)),
        ("ant", ("ance", "ancy")),
        ("ent", ("ence", "ency")),
        ("ile", ("ility",)),
        ("ceive", ("ception", "ceptive", "ceiver")),
        ("duce", ("duction", "ductive", "ducer")),
        ("scribe", ("scription", "scriptive", "scriber")),
        ("pose", ("position", "positive", "poser")),
        ("press", ("pression", "pressive")),
        ("gress", ("gression", "gressive")),
        ("ject", ("jection", "jective", "jector")),
        ("tract", ("traction", "tractive", "tractor")),
        ("dict", ("diction", "dictive")),
        ("vert", ("version", "versive", "versible")),
        ("mit", ("mission", "missive")),
        ("clude", ("clusion", "clusive")),
        ("flect", ("flection", "flexive")),
        ("fuse", ("fusion", "fusive")),
        ("tend", ("tension", "tensive")),
        ("tain", ("tention",)),
        ("late", ("lation", "lative")),
        ("mote", ("motion", "motive")),
        ("vene", ("vention",)),
        ("nounce", ("nunciation",)),
        ("plain", ("planation",)),
        ("quire", ("quisition",)),
        ("cede", ("cession",)),
        ("pel", ("pulsion", "pulsive")),
    )
    for ending, suffixes in replacements:
        if base.endswith(ending) and len(base) > len(ending) + 1:
            stem = base[: -len(ending)]
            for suffix in suffixes:
                yield Candidate(f"{stem}{suffix}", "derivation", 66)


def germanic_candidates(base: str) -> Iterator[Candidate]:
    special = {
        "long": ("length", "strengthen"),
        "strong": ("strength", "strengthen"),
        "wide": ("width", "widen"),
        "deep": ("depth", "deepen"),
        "high": ("height", "heighten"),
        "warm": ("warmth", "warm"),
        "true": ("truth", "truly"),
        "dead": ("death", "deadly"),
        "young": ("youth",),
    }
    for related in special.get(base, ()):
        yield Candidate(related, "derivation", 78)


def greek_candidates(base: str) -> Iterator[Candidate]:
    replacements = (
        ("logy", ("logical", "logist")),
        ("graphy", ("graphic", "grapher")),
        ("meter", ("metry", "metric")),
        ("metry", ("metric", "metrist")),
        ("scope", ("scopy", "scopic")),
        ("nomy", ("nomic", "nomics", "nomist")),
        ("cracy", ("crat", "cratic")),
        ("phobia", ("phobic", "phobe")),
        ("mania", ("maniac", "manic")),
        ("onym", ("onymy", "onymous")),
        ("lysis", ("lytic", "lyze", "lyse")),
        ("osis", ("otic",)),
        ("itis", ("itic",)),
        ("oma", ("omata", "omatous")),
        ("emia", ("emic",)),
    )
    for ending, suffixes in replacements:
        if base.endswith(ending) and len(base) > len(ending) + 2:
            stem = base[: -len(ending)]
            for suffix in suffixes:
                yield Candidate(f"{stem}{suffix}", "derivation", 60)


def plausible_pair(base: str, candidate: Candidate, profile: BaseProfile) -> bool:
    if candidate.confidence >= 100:
        return True
    if candidate.relation == "comparative" and not profile.has_superlative_form:
        return False
    if candidate.relation == "superlative" and not profile.has_comparative_form:
        return False
    if candidate.confidence >= 80:
        return True
    if len(base) <= 4 and candidate.relation == "derivation" and candidate.confidence < 76:
        return False
    if len(base) < 4 or len(candidate.related) < 4:
        return False
    if base in PRODUCTIVE_STOPWORDS or candidate.related in PRODUCTIVE_STOPWORDS:
        return False
    if candidate.related.startswith(base[: min(4, len(base))]):
        return True
    if base.startswith(candidate.related[: min(4, len(candidate.related))]):
        return True
    return candidate.confidence >= 66 and shared_prefix_length(base, candidate.related) >= 3


def plural_or_third_person(base: str) -> str:
    if base.endswith("y") and has_consonant_before_final_y(base):
        return f"{base[:-1]}ies"
    if base.endswith(("s", "sh", "ch", "x", "z", "o")):
        return f"{base}es"
    if base.endswith("f"):
        return f"{base[:-1]}ves"
    if base.endswith("fe"):
        return f"{base[:-2]}ves"
    return f"{base}s"


def past_tense(base: str) -> str:
    if base.endswith("e"):
        return f"{base}d"
    if base.endswith("y") and has_consonant_before_final_y(base):
        return f"{base[:-1]}ied"
    if base.endswith("c"):
        return f"{base}ked"
    if should_double_final_consonant(base):
        return f"{base}{base[-1]}ed"
    return f"{base}ed"


def present_participle(base: str) -> str:
    if base.endswith("ie"):
        return f"{base[:-2]}ying"
    if base.endswith("e") and not base.endswith(("ee", "oe", "ye")):
        return f"{base[:-1]}ing"
    if base.endswith("c"):
        return f"{base}king"
    if should_double_final_consonant(base):
        return f"{base}{base[-1]}ing"
    return f"{base}ing"


def agent_noun(base: str) -> str:
    if base.endswith("e"):
        return f"{base}r"
    if should_double_final_consonant(base):
        return f"{base}{base[-1]}er"
    return f"{base}er"


def comparative(base: str) -> str:
    if base.endswith("y") and has_consonant_before_final_y(base):
        return f"{base[:-1]}ier"
    if base.endswith("e"):
        return f"{base}r"
    if base.endswith("er"):
        return f"{base}er"
    if should_double_final_consonant(base):
        return f"{base}{base[-1]}er"
    return f"{base}er"


def superlative(base: str) -> str:
    if base.endswith("y") and has_consonant_before_final_y(base):
        return f"{base[:-1]}iest"
    if base.endswith("e"):
        return f"{base}st"
    if base.endswith("er"):
        return f"{base}est"
    if should_double_final_consonant(base):
        return f"{base}{base[-1]}est"
    return f"{base}est"


def adverb(base: str) -> str:
    if base == "public":
        return "publicly"
    if base == "true":
        return "truly"
    if base == "due":
        return "duly"
    if base == "whole":
        return "wholly"
    if base == "full":
        return "fully"
    if base.endswith("y"):
        return f"{base[:-1]}ily"
    if base.endswith("le"):
        return f"{base[:-1]}y"
    if base.endswith("ic"):
        return f"{base}ally"
    if base.endswith("al"):
        return f"{base}ly"
    return f"{base}ly"


def apply_suffix(base: str, suffix: str) -> str:
    if suffix == "able" and base.endswith(("ce", "ge")):
        return f"{base}{suffix}"
    if suffix.startswith(("a", "e", "i", "o", "u")) and base.endswith("e"):
        return f"{base[:-1]}{suffix}"
    if suffix not in {"ing", "ish"} and base.endswith("y") and has_consonant_before_final_y(base):
        return f"{base[:-1]}i{suffix}"
    return f"{base}{suffix}"


def normalize_word(surface: str) -> str | None:
    normalized = unicodedata.normalize("NFKC", surface).casefold().strip()
    if len(normalized) < 3 and normalized not in SHORT_IRREGULAR_WORDS:
        return None
    if not all(character.isalpha() for character in normalized):
        return None
    return normalized


def has_consonant_before_final_y(base: str) -> bool:
    return len(base) >= 2 and base[-2] not in VOWELS


def should_double_final_consonant(base: str) -> bool:
    return (
        len(base) >= 3
        and base[-1] not in VOWELS
        and base[-1] not in "wxy"
        and base[-2] in VOWELS
        and base[-3] not in VOWELS
    )


def shared_prefix_length(left: str, right: str) -> int:
    count = 0
    for left_char, right_char in zip(left, right, strict=False):
        if left_char != right_char:
            return count
        count += 1
    return count


def frequency_score(frequency: float) -> float:
    return math.log10(max(frequency, 0.0) + 1.0)


def suspicious_final_e_base(
    base: str,
    words_by_normalized: dict[str, LexiconWord],
) -> bool:
    return len(base) > 4 and base.endswith("e") and base[:-1] in words_by_normalized


def word_key(word: LexiconWord) -> tuple[float, int, str]:
    return (-word.frequency, word.order, word.surface)


def write_rows(path: Path, rows: Iterable[tuple[str, str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file, delimiter="\t", lineterminator="\n")
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
