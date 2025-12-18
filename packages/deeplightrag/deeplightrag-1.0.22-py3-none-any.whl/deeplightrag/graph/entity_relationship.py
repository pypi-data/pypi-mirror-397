"""
Entity-Relationship Graph (Layer 2)
Captures WHAT things mean - semantic entities and their relationships
Enhanced with advanced NLP-based extraction and visual grounding
"""

import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
import numpy as np

from ..ocr.deepseek_ocr import PageOCRResult, VisualRegion

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Entity node in the graph with visual grounding"""

    entity_id: str
    name: str
    entity_type: str  # person, organization, concept, metric, etc.
    value: Any
    description: str
    source_visual_regions: List[str]  # Visual region IDs where entity appears
    grounding_boxes: List[List[float]]  # Bounding boxes for visual grounding
    block_type_context: List[str]  # Types of blocks where entity appears
    embedding: Optional[np.ndarray] = None
    confidence: float = 1.0
    mention_count: int = 1  # How many times entity is mentioned
    page_numbers: List[int] = field(default_factory=list)  # Pages where entity appears
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "entity_type": self.entity_type,
            "value": str(self.value),
            "description": self.description,
            "source_visual_regions": self.source_visual_regions,
            "grounding_boxes": self.grounding_boxes,
            "block_type_context": self.block_type_context,
            "confidence": self.confidence,
            "mention_count": self.mention_count,
            "page_numbers": self.page_numbers,
            "metadata": self.metadata,
        }


@dataclass
class Relationship:
    """Relationship edge between entities with enhanced metadata"""

    source_entity: str
    target_entity: str
    relationship_type: str
    description: str
    weight: float
    spatial_cooccurrence: bool  # Do entities co-occur spatially?
    layout_aware_type: str  # Relationship type from layout context
    source_visual_regions: List[str]
    evidence_text: str = ""  # Text that supports this relationship
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "source": self.source_entity,
            "target": self.target_entity,
            "type": self.relationship_type,
            "description": self.description,
            "weight": self.weight,
            "spatial_cooccurrence": self.spatial_cooccurrence,
            "layout_aware_type": self.layout_aware_type,
            "source_visual_regions": self.source_visual_regions,
            "evidence_text": self.evidence_text,
            "metadata": self.metadata,
        }


class EntityRelationshipGraph:
    """
    Entity-Relationship Graph (Layer 2)
    Enhanced with:
    - Advanced NLP-based entity extraction
    - Semantic relationship mining
    - Visual grounding and layout awareness
    - Multi-hop reasoning support
    """

    def __init__(
        self,
        device: str = "cpu",
        ner_config: Optional[Dict] = None,
        re_config: Optional[Dict] = None,
        llm=None,
    ):
        self.graph = nx.DiGraph()
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []
        self.entity_name_index: Dict[str, str] = {}  # Name -> Entity ID
        self.entity_type_index: Dict[str, List[str]] = defaultdict(list)  # Type -> Entity IDs

        # Store configuration for NER and RE components
        self.device = device
        self.ner_config = ner_config or {}
        self.re_config = re_config or {}
        self.llm = llm

        # Initialize NER and RE components when needed
        self.ner_pipeline = None
        self.relation_pipeline = None

    def extract_entities_from_ocr(self, ocr_results: List[PageOCRResult]) -> int:
        logger.info("Extracting entities from visual regions")

        if not ocr_results:
            logger.warning("No OCR results provided")
            return 0

        # Collect all regions for batch processing
        all_regions = []
        for page_result in ocr_results:
            if page_result.visual_regions:
                all_regions.extend(page_result.visual_regions)

        if not all_regions:
            logger.warning("No visual regions found")
            return 0

        # Extract entities in batch
        entities_by_region = self._batch_extract_entities(all_regions)

        # Process extracted entities
        total_mentions = 0
        for region, entities in zip(all_regions, entities_by_region):
            total_mentions += len(entities)
            for entity in entities:
                normalized_name = entity.name.lower().strip()
                if not normalized_name:
                    continue

                if normalized_name not in self.entity_name_index:
                    self.entities[entity.entity_id] = entity
                    self.entity_name_index[normalized_name] = entity.entity_id
                    self.entity_type_index[entity.entity_type].append(entity.entity_id)
                    self.graph.add_node(entity.entity_id, **entity.to_dict())
                else:
                    existing_id = self.entity_name_index[normalized_name]
                    try:
                        self._merge_entity(existing_id, entity)
                    except Exception as e:
                        logger.debug(f"Failed to merge entity: {e}")

        logger.info(f"Found {total_mentions} entity mentions")
        logger.info(f"Extracted {len(self.entities)} unique entities")
        self._print_entity_distribution()
        return len(self.entities)

    def _batch_extract_entities(self, regions: List[VisualRegion]) -> List[List[Entity]]:
        """Batch extract entities from multiple regions for better performance."""
        try:
            from ..ner.entity_processor import EntityProcessor
            from ..ner.entity_filter import EntityFilter

            if not hasattr(self, "_entity_processor"):
                logger.info(f"Initializing GLiNER entity processor on {self.device}")
                self._entity_processor = EntityProcessor(
                    model_name=self.ner_config.get("model_name", "fastino/gliner2-base-v1"),
                    confidence_threshold=self.ner_config.get("gliner", {}).get("confidence_threshold", 0.3),
                    enable_visual_grounding=True,
                    device=self.device if self.device != "cpu" else "cpu",
                )

            if not hasattr(self, "_entity_filter"):
                self._entity_filter = EntityFilter(
                    min_length=2,
                    max_number_length=3,
                    confidence_threshold=self.ner_config.get("gliner", {}).get("confidence_threshold", 0.3),
                )

            # Batch extract using GLiNER2
            texts = [r.text_content for r in regions]
            region_types = [r.block_type for r in regions]

            batch_results = self._entity_processor.gliner_extractor.batch_extract_entities_and_relationships(
                texts=texts,
                region_types=region_types,
                batch_size=16
            )

            # Convert results to Entity objects
            all_entities = []
            for region, (extracted_entities, _) in zip(regions, batch_results):
                entities = []
                for gliner_entity in extracted_entities:
                    if not self._entity_filter.is_valid_entity(
                        entity_name=gliner_entity.text,
                        entity_type=gliner_entity.label,
                        confidence=gliner_entity.confidence,
                        block_type=region.block_type,
                        context_text=region.text_content,
                    ):
                        continue

                    entity_id = f"entity_{region.region_id}_{gliner_entity.start}_{gliner_entity.end}"
                    entity = Entity(
                        entity_id=entity_id,
                        name=gliner_entity.text,
                        entity_type=gliner_entity.label,
                        value=gliner_entity.text,
                        description=f"{gliner_entity.label}: {gliner_entity.text}",
                        source_visual_regions=[region.region_id],
                        grounding_boxes=[region.bbox.to_list()],
                        block_type_context=[region.block_type],
                        page_numbers=[region.page_num],
                        confidence=gliner_entity.confidence,
                        metadata=gliner_entity.metadata or {},
                    )
                    entities.append(entity)
                all_entities.append(entities)

            return all_entities

        except Exception as e:
            logger.warning(f"Batch extraction failed: {e}, falling back to single extraction")
            return [self._extract_entities_from_region(r) for r in regions]

    def _extract_entities_from_region(self, region: VisualRegion) -> List[Entity]:
        """Fallback: Extract entities from a single region."""
        entities = []
        text = region.text_content

        try:
            from ..ner.entity_processor import EntityProcessor
            from ..ner.entity_filter import EntityFilter

            if not hasattr(self, "_entity_processor"):
                self._entity_processor = EntityProcessor(
                    model_name=self.ner_config.get("model_name", "fastino/gliner2-base-v1"),
                    device=self.device if self.device != "cpu" else "cpu",
                )

            if not hasattr(self, "_entity_filter"):
                self._entity_filter = EntityFilter(min_length=2, max_number_length=3)

            result = self._entity_processor.process_text(
                text=text, text_id=region.region_id, region_type=region.block_type
            )

            for gliner_entity in result.get("extracted_entities", []):
                if not self._entity_filter.is_valid_entity(
                    entity_name=gliner_entity.text,
                    entity_type=gliner_entity.label,
                    confidence=gliner_entity.confidence,
                    block_type=region.block_type,
                    context_text=text,
                ):
                    continue

                entity_id = f"entity_{region.region_id}_{gliner_entity.start}_{gliner_entity.end}"
                entity = Entity(
                    entity_id=entity_id,
                    name=gliner_entity.text,
                    entity_type=gliner_entity.label,
                    value=gliner_entity.text,
                    description=f"{gliner_entity.label}: {gliner_entity.text}",
                    source_visual_regions=[region.region_id],
                    grounding_boxes=[region.bbox.to_list()],
                    block_type_context=[region.block_type],
                    page_numbers=[region.page_num],
                    confidence=gliner_entity.confidence,
                    metadata=gliner_entity.metadata or {},
                )
                entities.append(entity)

        except Exception as e:
            logger.warning(f"GLiNER extraction failed: {e}")

        return entities

    def _print_entity_distribution(self):
        """Print distribution of entity types"""
        distribution = {}
        for entity in self.entities.values():
            et = entity.entity_type
            distribution[et] = distribution.get(et, 0) + 1

        logger.debug("Entity distribution:")
        for etype, count in sorted(distribution.items(), key=lambda x: -x[1]):
            logger.debug(f"  {etype}: {count}")

    def _merge_entity(self, existing_id: str, new_entity: Entity):
        """Merge new entity information with existing entity"""
        existing = self.entities[existing_id]

        # Add new source visual_regions
        existing.source_visual_regions.extend(new_entity.source_visual_regions)
        existing.source_visual_regions = list(set(existing.source_visual_regions))

        # Add new grounding boxes
        existing.grounding_boxes.extend(new_entity.grounding_boxes)

        # Add new block type contexts
        existing.block_type_context.extend(new_entity.block_type_context)
        existing.block_type_context = list(set(existing.block_type_context))

        # Add page numbers
        existing.page_numbers.extend(new_entity.page_numbers)
        existing.page_numbers = sorted(list(set(existing.page_numbers)))

        # Increment mention count
        existing.mention_count += 1

        # Update confidence (weighted average based on mentions)
        existing.confidence = (
            existing.confidence * (existing.mention_count - 1) + new_entity.confidence
        ) / existing.mention_count

        # Update description if new one has more context
        if len(new_entity.description) > len(existing.description):
            existing.description = new_entity.description

    def extract_relationships(self, ocr_results: List[PageOCRResult]) -> int:
        """
        Extract relationships between entities using multiple strategies.

        Strategies:
        0. GLiNER2 unified extraction (ML-based semantic relationships)
        1. Semantic relationships (from text patterns - fallback)
        2. Spatial co-occurrence (entities in same region)
        3. Layout-aware relationships (table, header-content)
        4. Cross-page relationships (same entity across pages)
        """
        logger.info("Extracting relationships between entities")

        # 0. Try GLiNER2 unified extraction first (best quality)
        gliner_rel_count = self._extract_gliner2_relationships(ocr_results)
        
        # 1. Semantic relationships (pattern-based fallback)
        self._extract_semantic_relationships(ocr_results)

        # 2. Spatial co-occurrence relationships
        self._extract_spatial_relationships()

        # 3. Layout-aware relationships
        self._extract_layout_relationships()

        # 4. Type-based relationships
        self._extract_type_relationships()

        logger.info(f"Extracted {len(self.relationships)} relationships")
        if gliner_rel_count > 0:
            logger.debug(f"Including {gliner_rel_count} GLiNER2 semantic relationships")
        self._print_relationship_distribution()
        return len(self.relationships)

    def _print_relationship_distribution(self):
        """Print distribution of relationship types"""
        distribution = {}
        for rel in self.relationships:
            rt = rel.relationship_type
            distribution[rt] = distribution.get(rt, 0) + 1

        logger.debug("Relationship distribution:")
        for rtype, count in sorted(distribution.items(), key=lambda x: -x[1])[:10]:
            logger.debug(f"  {rtype}: {count}")

    def _extract_gliner2_relationships(self, ocr_results: List[PageOCRResult]) -> int:
        """Extract semantic relationships using GLiNER2 unified extraction"""
        if not hasattr(self, "_entity_processor") or self._entity_processor is None:
            return 0
        
        gliner_rel_count = 0
        
        # Process each region to extract relationships
        for page_result in ocr_results:
            for region in page_result.visual_regions:
                text = region.text_content
                
                # Get entities in this region
                entities_in_region = [
                    self.entities[eid]
                    for eid, entity in self.entities.items()
                    if region.region_id in entity.source_visual_regions
                ]
                
                if len(entities_in_region) < 2:
                    continue
                
                try:
                    # Use GLiNER2 to extract relationships
                    # Note: extract_entities_and_relationships returns (entities, relationships)
                    gliner_extractor = self._entity_processor.gliner_extractor
                    _, gliner_relationships = gliner_extractor.extract_entities_and_relationships(
                        text=text,
                        region_type=region.block_type
                    )
                    
                    # Convert GLiNER2 relationships to our format
                    for gliner_rel in gliner_relationships:
                        # Find matching entities by text
                        source_ent = None
                        target_ent = None
                        
                        for entity in entities_in_region:
                            if entity.name.lower() == gliner_rel.get('source', '').lower():
                                source_ent = entity
                            if entity.name.lower() == gliner_rel.get('target', '').lower():
                                target_ent = entity
                        
                        if source_ent and target_ent:
                            rel = Relationship(
                                source_entity=source_ent.entity_id,
                                target_entity=target_ent.entity_id,
                                relationship_type=gliner_rel.get('type', 'related_to'),
                                description=f"GLiNER2: {gliner_rel.get('type', 'related_to')}",
                                weight=gliner_rel.get('confidence', 0.75),
                                spatial_cooccurrence=True,
                                layout_aware_type=region.block_type,
                                source_visual_regions=[region.region_id],
                                evidence_text=text[:200],
                                metadata={"extraction_method": "gliner2", **gliner_rel.get('metadata', {})}
                            )
                            self._add_relationship(rel)
                            gliner_rel_count += 1
                            
                except Exception as e:
                    # Silently continue if GLiNER2 extraction fails
                    pass
        
        return gliner_rel_count

    def _extract_semantic_relationships(self, ocr_results: List[PageOCRResult]):
        """Extract semantic relationships from text patterns"""
        # Enhanced relationship patterns
        rel_patterns = {
            "describes": [r"describes?", r"explains?", r"defines?"],
            "achieves": [r"achieves?", r"accomplishes?", r"reaches?"],
            "uses": [r"uses?", r"utilizes?", r"employs?", r"leverages?"],
            "improves": [r"improves?", r"enhances?", r"optimizes?"],
            "reduces": [r"reduces?", r"decreases?", r"minimizes?"],
            "increases": [r"increases?", r"grows?", r"rises?"],
            "compared_to": [r"compared to", r"versus", r"vs\.?", r"against"],
            "based_on": [r"based on", r"built on", r"derived from"],
            "consists_of": [r"consists? of", r"comprises?", r"includes?"],
            "produces": [r"produces?", r"generates?", r"creates?", r"outputs?"],
            "requires": [r"requires?", r"needs?", r"depends? on"],
        }

        for page_result in ocr_results:
            for region in page_result.visual_regions:
                text_lower = region.text_content.lower()

                # Find entities in this region
                entities_in_region = [
                    eid
                    for eid, entity in self.entities.items()
                    if region.region_id in entity.source_visual_regions
                ]

                if len(entities_in_region) < 2:
                    continue

                # Check for relationship patterns
                for rel_type, patterns in rel_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, text_lower):
                            # Create relationships between entities in region
                            for i in range(len(entities_in_region)):
                                for j in range(i + 1, len(entities_in_region)):
                                    rel = Relationship(
                                        source_entity=entities_in_region[i],
                                        target_entity=entities_in_region[j],
                                        relationship_type=rel_type,
                                        description=f"{rel_type} relationship from pattern '{pattern}'",
                                        weight=0.8,
                                        spatial_cooccurrence=True,
                                        layout_aware_type=region.block_type,
                                        source_visual_regions=[region.region_id],
                                        evidence_text=region.text_content[:200],
                                    )
                                    self._add_relationship(rel)

    def _extract_spatial_relationships(self):
        """Extract relationships based on spatial co-occurrence"""
        entity_ids = list(self.entities.keys())

        for i in range(len(entity_ids)):
            for j in range(i + 1, len(entity_ids)):
                entity1 = self.entities[entity_ids[i]]
                entity2 = self.entities[entity_ids[j]]

                # Check for shared regions
                shared_regions = set(entity1.source_visual_regions).intersection(
                    set(entity2.source_visual_regions)
                )

                if shared_regions:
                    # Weight based on number of co-occurrences
                    weight = min(len(shared_regions) * 0.2, 1.0)

                    rel = Relationship(
                        source_entity=entity_ids[i],
                        target_entity=entity_ids[j],
                        relationship_type="co_occurs_with",
                        description=f"Entities co-occur in {len(shared_regions)} region(s)",
                        weight=weight,
                        spatial_cooccurrence=True,
                        layout_aware_type="spatial",
                        source_visual_regions=list(shared_regions),
                    )
                    self._add_relationship(rel)

                # Check for same page occurrence
                shared_pages = set(entity1.page_numbers).intersection(set(entity2.page_numbers))

                if shared_pages and not shared_regions:
                    rel = Relationship(
                        source_entity=entity_ids[i],
                        target_entity=entity_ids[j],
                        relationship_type="same_page",
                        description=f"Entities appear on same page(s): {shared_pages}",
                        weight=0.3,
                        spatial_cooccurrence=False,
                        layout_aware_type="page",
                        source_visual_regions=[],
                    )
                    self._add_relationship(rel)

    def _extract_layout_relationships(self):
        """Extract relationships based on document layout"""
        # Group entities by block type
        entities_by_block_type = defaultdict(list)

        for eid, entity in self.entities.items():
            for block_type in entity.block_type_context:
                entities_by_block_type[block_type].append(eid)

        # Entities in tables are related
        if "table" in entities_by_block_type:
            table_entities = entities_by_block_type["table"]
            for i in range(len(table_entities)):
                for j in range(i + 1, len(table_entities)):
                    entity1 = self.entities[table_entities[i]]
                    entity2 = self.entities[table_entities[j]]

                    shared = set(entity1.source_visual_regions).intersection(set(entity2.source_visual_regions))

                    if shared:
                        rel = Relationship(
                            source_entity=table_entities[i],
                            target_entity=table_entities[j],
                            relationship_type="table_relation",
                            description="Entities are in same table",
                            weight=0.9,
                            spatial_cooccurrence=True,
                            layout_aware_type="table",
                            source_visual_regions=list(shared),
                        )
                        self._add_relationship(rel)

        # Headers describe paragraphs
        if "header" in entities_by_block_type and "paragraph" in entities_by_block_type:
            for header_eid in entities_by_block_type["header"]:
                header_entity = self.entities[header_eid]
                for para_eid in entities_by_block_type["paragraph"]:
                    para_entity = self.entities[para_eid]

                    # Same page check
                    if set(header_entity.page_numbers).intersection(set(para_entity.page_numbers)):
                        rel = Relationship(
                            source_entity=header_eid,
                            target_entity=para_eid,
                            relationship_type="header_describes",
                            description="Header entity describes paragraph content",
                            weight=0.6,
                            spatial_cooccurrence=False,
                            layout_aware_type="hierarchical",
                            source_visual_regions=[],
                        )
                        self._add_relationship(rel)

    def _extract_type_relationships(self):
        """Extract relationships based on entity types"""
        # Money entities related to percentages (financial metrics)
        money_entities = self.entity_type_index.get("money", [])
        percentage_entities = self.entity_type_index.get("percentage", [])

        for money_eid in money_entities:
            money_entity = self.entities[money_eid]
            for pct_eid in percentage_entities:
                pct_entity = self.entities[pct_eid]

                # Same region = likely related metric
                shared = set(money_entity.source_visual_regions).intersection(
                    set(pct_entity.source_visual_regions)
                )

                if shared:
                    rel = Relationship(
                        source_entity=money_eid,
                        target_entity=pct_eid,
                        relationship_type="financial_metric",
                        description="Monetary value with percentage change",
                        weight=0.85,
                        spatial_cooccurrence=True,
                        layout_aware_type="metric",
                        source_visual_regions=list(shared),
                    )
                    self._add_relationship(rel)

        # Date entities related to metrics (temporal context)
        date_entities = self.entity_type_index.get("date", [])
        metric_entities = self.entity_type_index.get("metric", [])

        for date_eid in date_entities:
            date_entity = self.entities[date_eid]
            for metric_eid in metric_entities:
                metric_entity = self.entities[metric_eid]

                shared = set(date_entity.source_visual_regions).intersection(
                    set(metric_entity.source_visual_regions)
                )

                if shared:
                    rel = Relationship(
                        source_entity=date_eid,
                        target_entity=metric_eid,
                        relationship_type="temporal_context",
                        description="Date provides temporal context for metric",
                        weight=0.7,
                        spatial_cooccurrence=True,
                        layout_aware_type="temporal",
                        source_visual_regions=list(shared),
                    )
                    self._add_relationship(rel)

    def _add_relationship(self, rel: Relationship):
        """Add relationship to graph, avoiding duplicates"""
        # Check for duplicates
        for existing in self.relationships:
            if (
                existing.source_entity == rel.source_entity
                and existing.target_entity == rel.target_entity
                and existing.relationship_type == rel.relationship_type
            ):
                # Update weight if new relationship is stronger
                if rel.weight > existing.weight:
                    existing.weight = rel.weight
                return

        self.relationships.append(rel)
        edge_data = rel.to_dict()
        edge_data.pop("source", None)
        edge_data.pop("target", None)
        self.graph.add_edge(rel.source_entity, rel.target_entity, **edge_data)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID"""
        return self.entities.get(entity_id)

    def get_entity_by_name(self, name: str) -> Optional[Entity]:
        """Get entity by name (case-insensitive)"""
        entity_id = self.entity_name_index.get(name.lower().strip())
        if entity_id:
            return self.entities.get(entity_id)
        return None

    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a specific type"""
        entity_ids = self.entity_type_index.get(entity_type, [])
        return [self.entities[eid] for eid in entity_ids]

    def get_related_entities(
        self, entity_id: str, relationship_types: Optional[List[str]] = None, hop_distance: int = 1
    ) -> List[str]:
        """
        Get entities related to given entity with multi-hop support.

        Args:
            entity_id: Entity ID
            relationship_types: Filter by relationship types
            hop_distance: Number of hops

        Returns:
            List of related entity IDs
        """
        if hop_distance == 1:
            neighbors = list(self.graph.successors(entity_id))
            neighbors.extend(list(self.graph.predecessors(entity_id)))

            if relationship_types:
                filtered = []
                for neighbor in neighbors:
                    if self.graph.has_edge(entity_id, neighbor):
                        edge_data = self.graph.get_edge_data(entity_id, neighbor)
                        if edge_data.get("type") in relationship_types:
                            filtered.append(neighbor)
                    elif self.graph.has_edge(neighbor, entity_id):
                        edge_data = self.graph.get_edge_data(neighbor, entity_id)
                        if edge_data.get("type") in relationship_types:
                            filtered.append(neighbor)
                return list(set(filtered))

            return list(set(neighbors))
        else:
            # Multi-hop traversal
            current = set([entity_id])
            all_related = set()

            for _ in range(hop_distance):
                next_level = set()
                for eid in current:
                    next_level.update(self.get_related_entities(eid, relationship_types, 1))
                all_related.update(next_level)
                current = next_level

            all_related.discard(entity_id)
            return list(all_related)

    def search_entities(
        self, query: str, entity_types: Optional[List[str]] = None, top_k: int = 10
    ) -> List[Entity]:
        """
        Search entities by query string using multiple matching strategies.

        Args:
            query: Search query
            entity_types: Filter by entity types
            top_k: Number of results

        Returns:
            List of matching entities sorted by relevance
        """
        results = []
        query_lower = query.lower().strip()
        query_words = set(query_lower.split())

        for entity in self.entities.values():
            if entity_types and entity.entity_type not in entity_types:
                continue

            score = 0
            entity_name_lower = entity.name.lower()
            entity_desc_lower = entity.description.lower()

            # Exact match in name (highest score)
            if query_lower == entity_name_lower:
                score = 1.0
            elif query_lower in entity_name_lower:
                score = 0.9
            # Exact match in description
            elif query_lower in entity_desc_lower:
                score = 0.7

            # Word overlap matching
            if score == 0:
                entity_words = set(entity_name_lower.split())
                entity_words.update(entity_desc_lower.split())
                overlap = query_words.intersection(entity_words)
                if overlap:
                    score = len(overlap) / len(query_words) * 0.6

            # Partial word matching
            if score == 0:
                for word in query_words:
                    if len(word) > 3:  # Skip short words
                        if word in entity_name_lower or word in entity_desc_lower:
                            score = max(score, 0.4)

            # Boost score based on entity importance
            if score > 0:
                # Boost by mention count
                score *= 1 + min(entity.mention_count * 0.1, 0.5)
                # Boost by confidence
                score *= entity.confidence

            if score > 0:
                results.append((entity, score))

        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        return [entity for entity, _ in results[:top_k]]

    def get_entity_context(self, entity_id: str, max_depth: int = 2) -> Dict:
        """
        Get rich context for an entity including relationships.

        Args:
            entity_id: Entity ID
            max_depth: Depth of relationship traversal

        Returns:
            Dictionary with entity context
        """
        if entity_id not in self.entities:
            return {}

        entity = self.entities[entity_id]
        context = {"entity": entity.to_dict(), "relationships": [], "related_entities": []}

        # Get direct relationships
        for rel in self.relationships:
            if rel.source_entity == entity_id or rel.target_entity == entity_id:
                context["relationships"].append(rel.to_dict())

        # Get related entities
        related_ids = self.get_related_entities(entity_id, hop_distance=max_depth)
        for rid in related_ids[:20]:  # Limit to top 20
            if rid in self.entities:
                context["related_entities"].append(self.entities[rid].to_dict())

        return context

    def to_dict(self) -> Dict:
        """Serialize graph to dictionary"""
        return {
            "entities": [entity.to_dict() for entity in self.entities.values()],
            "relationships": [rel.to_dict() for rel in self.relationships],
            "num_entities": len(self.entities),
            "num_relationships": len(self.relationships),
        }

    def save(self, path: str):
        """Save graph to JSON file"""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Entity-Relationship Graph saved to {path}")

    def load(self, path: str):
        """Load graph from JSON file"""
        with open(path, "r") as f:
            data = json.load(f)

        # Clear existing data
        self.graph = nx.DiGraph()
        self.entities = {}
        self.relationships = []
        self.entity_name_index = {}
        self.entity_type_index = defaultdict(list)

        # Reconstruct entities
        for entity_data in data.get("entities", []):
            entity = Entity(
                entity_id=entity_data["entity_id"],
                name=entity_data["name"],
                entity_type=entity_data["entity_type"],
                value=entity_data["value"],
                description=entity_data["description"],
                source_visual_regions=entity_data["source_visual_regions"],
                grounding_boxes=entity_data["grounding_boxes"],
                block_type_context=entity_data["block_type_context"],
                embedding=None,
                confidence=entity_data.get("confidence", 1.0),
                mention_count=entity_data.get("mention_count", 1),
                page_numbers=entity_data.get("page_numbers", []),
                metadata=entity_data.get("metadata", {}),
            )

            self.entities[entity.entity_id] = entity
            self.graph.add_node(entity.entity_id)
            self.entity_name_index[entity.name.lower()] = entity.entity_id
            self.entity_type_index[entity.entity_type].append(entity.entity_id)

        # Reconstruct relationships
        for rel_data in data.get("relationships", []):
            relationship = Relationship(
                source_entity=rel_data["source"],
                target_entity=rel_data["target"],
                relationship_type=rel_data["type"],
                description=rel_data["description"],
                weight=rel_data["weight"],
                spatial_cooccurrence=rel_data.get("spatial_cooccurrence", False),
                layout_aware_type=rel_data.get("layout_aware_type", ""),
                source_visual_regions=rel_data.get("source_visual_regions", []),
                evidence_text=rel_data.get("evidence_text", ""),
                metadata=rel_data.get("metadata", {}),
            )

            self.relationships.append(relationship)
            self.graph.add_edge(
                relationship.source_entity,
                relationship.target_entity,
                type=relationship.relationship_type,
                weight=relationship.weight,
                **relationship.metadata,
            )

        logger.debug(
            f"  Entity-Relationship Graph loaded: {len(self.entities)} entities, {len(self.relationships)} relationships"
        )

    def get_statistics(self) -> Dict:
        """Get comprehensive graph statistics"""
        entity_type_counts = {}
        for entity in self.entities.values():
            et = entity.entity_type
            entity_type_counts[et] = entity_type_counts.get(et, 0) + 1

        rel_type_counts = {}
        for rel in self.relationships:
            rt = rel.relationship_type
            rel_type_counts[rt] = rel_type_counts.get(rt, 0) + 1

        # Calculate graph metrics
        avg_degree = (
            sum(dict(self.graph.degree()).values()) / len(self.entities) if self.entities else 0
        )

        # Find most connected entities
        if self.entities:
            degrees = dict(self.graph.degree())
            top_entities = sorted(degrees.items(), key=lambda x: -x[1])[:5]
        else:
            top_entities = []

        return {
            "num_entities": len(self.entities),
            "num_relationships": len(self.relationships),
            "entity_types": entity_type_counts,
            "relationship_types": rel_type_counts,
            "avg_entity_degree": avg_degree,
            "top_connected_entities": top_entities,
            "total_mentions": sum(e.mention_count for e in self.entities.values()),
        }
