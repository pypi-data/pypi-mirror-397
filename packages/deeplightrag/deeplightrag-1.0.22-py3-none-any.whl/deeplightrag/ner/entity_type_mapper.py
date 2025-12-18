"""Entity Type Mapper for GLiNER Labels."""

import re
from typing import Dict, Optional


class EntityTypeMapper:
    def __init__(self):
        self.gliner_to_entity_type = {
            # Person
            "person": "PERSON",
            "people": "PERSON",
            "individual": "PERSON",
            "human": "PERSON",
            "name": "PERSON",
            "author": "PERSON",
            "researcher": "PERSON",
            "scientist": "PERSON",
            # Organization
            "organization": "ORGANIZATION",
            "company": "ORGANIZATION",
            "institution": "ORGANIZATION",
            "agency": "ORGANIZATION",
            "business": "ORGANIZATION",
            "corporation": "ORGANIZATION",
            "university": "ORGANIZATION",
            "startup": "ORGANIZATION",
            "government": "ORGANIZATION",
            # Location
            "location": "LOCATION",
            "place": "LOCATION",
            "geographic": "LOCATION",
            "address": "LOCATION",
            "country": "LOCATION",
            "city": "LOCATION",
            "state": "LOCATION",
            "region": "LOCATION",
            # Date/Time
            "date": "DATE_TIME",
            "time": "DATE_TIME",
            "year": "DATE_TIME",
            "period": "DATE_TIME",
            "duration": "DATE_TIME",
            "when": "DATE_TIME",
            "timestamp": "DATE_TIME",
            "datetime": "DATE_TIME",
            # Money
            "money": "MONEY",
            "cost": "MONEY",
            "price": "MONEY",
            "budget": "MONEY",
            "currency": "MONEY",
            "value": "MONEY",
            "amount": "MONEY",
            "expense": "MONEY",
            # Percentage
            "percentage": "PERCENTAGE",
            "percent": "PERCENTAGE",
            "rate": "PERCENTAGE",
            "proportion": "PERCENTAGE",
            "ratio": "PERCENTAGE",
            # Technical
            "technical": "TECHNICAL_TERM",
            "method": "TECHNICAL_TERM",
            "technique": "TECHNICAL_TERM",
            "algorithm": "TECHNICAL_TERM",
            "architecture": "TECHNICAL_TERM",
            "approach": "TECHNICAL_TERM",
            "standard": "TECHNICAL_TERM",
            "specification": "TECHNICAL_TERM",
            "protocol": "TECHNICAL_TERM",
            "procedure": "TECHNICAL_TERM",
            "process": "TECHNICAL_TERM",
            "interface": "TECHNICAL_TERM",
            # Product
            "product": "PRODUCT",
            "software": "PRODUCT",
            "tool": "PRODUCT",
            "application": "PRODUCT",
            "platform": "PRODUCT",
            "service": "PRODUCT",
            "device": "PRODUCT",
            "equipment": "PRODUCT",
            "instrument": "PRODUCT",
            "technology": "PRODUCT",
            "system": "PRODUCT",
            "framework": "PRODUCT",
            "library": "PRODUCT",
            "api": "PRODUCT",
            "language": "PRODUCT",
            "model": "PRODUCT",
            "database": "PRODUCT",
            "project": "PRODUCT",
            "program": "PRODUCT",
            # Concept
            "concept": "CONCEPT",
            "idea": "CONCEPT",
            "theory": "CONCEPT",
            "principle": "CONCEPT",
            "notion": "CONCEPT",
            "paradigm": "CONCEPT",
            "methodology": "CONCEPT",
            "strategy": "CONCEPT",
            "research": "CONCEPT",
            # Event
            "event": "EVENT",
            "meeting": "EVENT",
            "conference": "EVENT",
            "launch": "EVENT",
            "release": "EVENT",
            "announcement": "EVENT",
            "presentation": "EVENT",
            "workshop": "EVENT",
            "initiative": "EVENT",
            # Document
            "document": "DOCUMENT",
            "report": "DOCUMENT",
            "paper": "DOCUMENT",
            "article": "DOCUMENT",
            "reference": "DOCUMENT",
            "publication": "DOCUMENT",
            "study": "DOCUMENT",
            # Metric
            "measurement": "METRIC",
            "quantity": "METRIC",
            "metric": "METRIC",
            "size": "METRIC",
            "dimension": "METRIC",
            "parameter": "METRIC",
            "statistic": "METRIC",
            "figure": "METRIC",
        }

        self.pattern_mappings = [
            (r"^\d{4}$", "DATE_TIME", lambda x: 1900 <= int(x) <= 2100),
            (r"^\d+\.?\d*%$", "PERCENTAGE", None),
            (r"^\d+\.?\d*\s*percent$", "PERCENTAGE", None),
            (r"^\$[\d,]+\.?\d*$", "MONEY", None),
            (r"^\$[\d,]+\.?\d*\s*[mb]?(?:illion)?$", "MONEY", None),
            (r"^\d+-\d+$", "METRIC", None),
            (r"^v?\d+\.\d+(\.\d+)?$", "PRODUCT", None),
        ]

        self.known_entities = {
            # Organizations
            "google": "ORGANIZATION",
            "microsoft": "ORGANIZATION",
            "apple": "ORGANIZATION",
            "amazon": "ORGANIZATION",
            "tesla": "ORGANIZATION",
            "openai": "ORGANIZATION",
            "anthropic": "ORGANIZATION",
            "facebook": "ORGANIZATION",
            "meta": "ORGANIZATION",
            "nvidia": "ORGANIZATION",
            # Products/Technologies
            "tensorflow": "PRODUCT",
            "pytorch": "PRODUCT",
            "keras": "PRODUCT",
            "scikit-learn": "PRODUCT",
            "python": "PRODUCT",
            "javascript": "PRODUCT",
            "java": "PRODUCT",
            "c++": "PRODUCT",
            "opencv": "PRODUCT",
            "huggingface": "PRODUCT",
            "github": "PRODUCT",
            "docker": "PRODUCT",
            "kubernetes": "PRODUCT",
            "aws": "PRODUCT",
            "azure": "PRODUCT",
            "gcp": "PRODUCT",
            # Technical Terms
            "machine learning": "TECHNICAL_TERM",
            "deep learning": "TECHNICAL_TERM",
            "neural network": "TECHNICAL_TERM",
            "artificial intelligence": "TECHNICAL_TERM",
            "ai": "CONCEPT",
        }

    def map_entity_type(self, gliner_label: str, entity_text: str, context: str = "") -> str:
        label = gliner_label.lower().strip()
        text = entity_text.lower().strip()

        if label in self.gliner_to_entity_type:
            return self.gliner_to_entity_type[label]

        for pattern, entity_type, validator in self.pattern_mappings:
            if re.match(pattern, entity_text):
                if validator is None or validator(entity_text):
                    return entity_type

        if text in self.known_entities:
            return self.known_entities[text]

        if "person" in label or "name" in label:
            return "PERSON"
        if any(w in label for w in ["org", "company", "business", "corp", "university"]):
            return "ORGANIZATION"
        if any(w in label for w in ["loc", "place", "address", "country", "city"]):
            return "LOCATION"
        if any(w in label for w in ["date", "time", "year", "when"]):
            return "DATE_TIME"
        if any(w in label for w in ["money", "cost", "price", "$"]):
            return "MONEY"
        if any(w in label for w in ["product", "tool", "software", "app", "platform"]):
            return "PRODUCT"

        if context:
            if entity_text.istitle() and len(entity_text.split()) <= 3:
                return "PERSON"
            if entity_text.isupper() and len(entity_text) <= 10:
                return "ORGANIZATION"

        if self._looks_like_date(entity_text):
            return "DATE_TIME"
        if self._looks_like_money(entity_text):
            return "MONEY"
        if self._looks_like_percentage(entity_text):
            return "PERCENTAGE"

        return "CONCEPT"

    def _looks_like_date(self, text: str) -> bool:
        patterns = [
            r"^\d{4}-\d{2}-\d{2}$",
            r"^\d{1,2}/\d{1,2}/\d{2,4}$",
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}",
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def _looks_like_money(self, text: str) -> bool:
        return bool(re.match(r"^\$[\d,]+\.?\d*|[\d,]+\.?\d*\s*(USD|EUR|GBP|dollars?|euros?)$", text, re.IGNORECASE))

    def _looks_like_percentage(self, text: str) -> bool:
        return bool(re.match(r"^\d+\.?\d*%|^\d+\.?\d*\s*percent$", text, re.IGNORECASE))

    def get_confidence_boost(self, entity_text: str, entity_type: str, context: str = "") -> float:
        boost = 0.0

        if entity_text.istitle() and entity_type in ["PERSON", "ORGANIZATION", "PRODUCT"]:
            boost += 0.1
        if entity_text.isupper() and 2 <= len(entity_text) <= 6:
            if entity_type in ["ORGANIZATION", "TECHNICAL_TERM"]:
                boost += 0.1
        if entity_type == "DATE_TIME" and self._looks_like_date(entity_text):
            boost += 0.1
        elif entity_type == "MONEY" and self._looks_like_money(entity_text):
            boost += 0.1
        elif entity_type == "PERCENTAGE" and self._looks_like_percentage(entity_text):
            boost += 0.1

        return min(boost, 0.3)