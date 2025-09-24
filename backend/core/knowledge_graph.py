"""
Knowledge Graph Engine - Dynamic knowledge representation and discovery
Advanced knowledge management for today's update
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx
import numpy as np
from collections import defaultdict, Counter
import hashlib

logger = logging.getLogger(__name__)

class EntityType(Enum):
    """Types of entities in the knowledge graph"""
    CONCEPT = "concept"
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    TECHNOLOGY = "technology"
    PROCESS = "process"
    DOCUMENT = "document"
    AGENT = "agent"
    WORKFLOW = "workflow"
    REASONING_CHAIN = "reasoning_chain"

class RelationType(Enum):
    """Types of relationships between entities"""
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    USED_BY = "used_by"
    CREATED_BY = "created_by"
    DEPENDS_ON = "depends_on"
    SIMILAR_TO = "similar_to"
    CAUSES = "causes"
    ENABLES = "enables"
    CONTAINS = "contains"
    IMPLEMENTS = "implements"
    INFLUENCES = "influences"

@dataclass
class Entity:
    """Entity in the knowledge graph"""
    id: str
    name: str
    entity_type: EntityType
    attributes: Dict[str, Any] = field(default_factory=dict)
    aliases: Set[str] = field(default_factory=set)
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    source_references: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID for entity"""
        content = f"{self.name}_{self.entity_type.value}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

@dataclass
class Relationship:
    """Relationship between entities"""
    id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: RelationType
    weight: float = 1.0
    confidence: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    source_references: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID for relationship"""
        content = f"{self.source_entity_id}_{self.relation_type.value}_{self.target_entity_id}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

@dataclass
class KnowledgeCluster:
    """Cluster of related knowledge"""
    id: str
    name: str
    entities: Set[str]
    description: str = ""
    keywords: Set[str] = field(default_factory=set)
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)

class EntityExtractor:
    """Extracts entities from text using NLP techniques"""
    
    def __init__(self):
        self.entity_patterns = {
            EntityType.TECHNOLOGY: [
                r'\b(AI|ML|NLP|API|REST|GraphQL|WebSocket|React|Python|JavaScript|TypeScript|FastAPI|SQLAlchemy)\b',
                r'\b([A-Z][a-z]+(?:[A-Z][a-z]*)+)\b',  # CamelCase tech terms
            ],
            EntityType.CONCEPT: [
                r'\b(authentication|authorization|workflow|pipeline|orchestration|reasoning|embedding|vector)\b',
                r'\b(machine learning|artificial intelligence|natural language processing)\b',
            ],
            EntityType.PROCESS: [
                r'\b(processing|analysis|generation|synthesis|decomposition|optimization)\b',
                r'\b(training|inference|validation|testing|deployment)\b',
            ]
        }
        
        self.relation_patterns = {
            RelationType.USES: [r'uses?', r'utilizes?', r'employs?', r'leverages?'],
            RelationType.CREATES: [r'creates?', r'generates?', r'produces?', r'builds?'],
            RelationType.DEPENDS_ON: [r'depends on', r'requires?', r'needs?', r'relies on'],
            RelationType.ENABLES: [r'enables?', r'allows?', r'facilitates?', r'supports?'],
        }
    
    async def extract_entities(self, text: str, source_id: str) -> List[Entity]:
        """Extract entities from text"""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                import re
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    entity_name = match.group().strip()
                    
                    if len(entity_name) > 2:  # Filter out very short matches
                        entity = Entity(
                            id="",  # Will be auto-generated
                            name=entity_name,
                            entity_type=entity_type,
                            confidence=0.8,  # Base confidence for pattern matching
                            source_references={source_id}
                        )
                        entities.append(entity)
        
        return entities
    
    async def extract_relationships(self, text: str, entities: List[Entity], source_id: str) -> List[Relationship]:
        """Extract relationships between entities"""
        relationships = []
        
        # Simple co-occurrence based relationship extraction
        entity_positions = {}
        for entity in entities:
            import re
            positions = []
            for match in re.finditer(re.escape(entity.name), text, re.IGNORECASE):
                positions.append(match.start())
            entity_positions[entity.id] = positions
        
        # Find entities that appear close to each other
        for entity1 in entities:
            for entity2 in entities:
                if entity1.id == entity2.id:
                    continue
                
                positions1 = entity_positions.get(entity1.id, [])
                positions2 = entity_positions.get(entity2.id, [])
                
                # Check if entities appear within 100 characters of each other
                for pos1 in positions1:
                    for pos2 in positions2:
                        if abs(pos1 - pos2) < 100:
                            relationship = Relationship(
                                id="",
                                source_entity_id=entity1.id,
                                target_entity_id=entity2.id,
                                relation_type=RelationType.RELATED_TO,
                                confidence=0.6,
                                source_references={source_id}
                            )
                            relationships.append(relationship)
                            break
        
        return relationships

class KnowledgeGraph:
    """Main knowledge graph implementation"""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.clusters: Dict[str, KnowledgeCluster] = {}
        self.graph = nx.MultiDiGraph()
        self.entity_extractor = EntityExtractor()
        
        # Performance tracking
        self.total_entities = 0
        self.total_relationships = 0
        self.last_update = datetime.utcnow()
    
    async def add_entity(self, entity: Entity) -> str:
        """Add or update an entity in the knowledge graph"""
        # Check for existing entity with same name and type
        existing_entity = self._find_similar_entity(entity)
        
        if existing_entity:
            # Merge with existing entity
            merged_entity = await self._merge_entities(existing_entity, entity)
            self.entities[merged_entity.id] = merged_entity
            self._update_graph_node(merged_entity)
            return merged_entity.id
        else:
            # Add new entity
            self.entities[entity.id] = entity
            self.graph.add_node(
                entity.id,
                name=entity.name,
                type=entity.entity_type.value,
                confidence=entity.confidence
            )
            self.total_entities += 1
            logger.debug(f"Added entity: {entity.name} ({entity.entity_type.value})")
            return entity.id
    
    async def add_relationship(self, relationship: Relationship) -> str:
        """Add a relationship to the knowledge graph"""
        # Verify entities exist
        if (relationship.source_entity_id not in self.entities or 
            relationship.target_entity_id not in self.entities):
            logger.warning(f"Cannot add relationship: entities not found")
            return ""
        
        # Check for existing relationship
        existing_rel = self._find_similar_relationship(relationship)
        
        if existing_rel:
            # Update weight and confidence
            existing_rel.weight += relationship.weight
            existing_rel.confidence = max(existing_rel.confidence, relationship.confidence)
            existing_rel.source_references.update(relationship.source_references)
            self._update_graph_edge(existing_rel)
            return existing_rel.id
        else:
            # Add new relationship
            self.relationships[relationship.id] = relationship
            self.graph.add_edge(
                relationship.source_entity_id,
                relationship.target_entity_id,
                key=relationship.id,
                type=relationship.relation_type.value,
                weight=relationship.weight,
                confidence=relationship.confidence
            )
            self.total_relationships += 1
            logger.debug(f"Added relationship: {relationship.relation_type.value}")
            return relationship.id
    
    async def process_text(self, text: str, source_id: str, source_type: str = "document") -> Dict[str, Any]:
        """Process text and extract knowledge"""
        start_time = datetime.utcnow()
        
        # Extract entities
        entities = await self.entity_extractor.extract_entities(text, source_id)
        
        # Add entities to graph
        entity_ids = []
        for entity in entities:
            entity_id = await self.add_entity(entity)
            entity_ids.append(entity_id)
        
        # Extract relationships
        relationships = await self.entity_extractor.extract_relationships(text, entities, source_id)
        
        # Add relationships to graph
        relationship_ids = []
        for relationship in relationships:
            rel_id = await self.add_relationship(relationship)
            if rel_id:
                relationship_ids.append(rel_id)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Update clusters
        await self._update_clusters(entity_ids)
        
        self.last_update = datetime.utcnow()
        
        return {
            "entities_extracted": len(entities),
            "relationships_extracted": len(relationships),
            "entity_ids": entity_ids,
            "relationship_ids": relationship_ids,
            "processing_time": processing_time,
            "source_id": source_id,
            "source_type": source_type
        }
    
    async def query_knowledge(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Query the knowledge graph"""
        # Simple keyword-based search
        query_lower = query.lower()
        
        # Find matching entities
        matching_entities = []
        for entity in self.entities.values():
            if (query_lower in entity.name.lower() or 
                any(query_lower in alias.lower() for alias in entity.aliases) or
                any(query_lower in str(value).lower() for value in entity.attributes.values())):
                matching_entities.append(entity)
        
        # Sort by confidence and limit results
        matching_entities.sort(key=lambda e: e.confidence, reverse=True)
        matching_entities = matching_entities[:limit]
        
        # Get related entities for each match
        results = []
        for entity in matching_entities:
            related_entities = await self._get_related_entities(entity.id, max_depth=2)
            
            results.append({
                "entity": {
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.entity_type.value,
                    "confidence": entity.confidence,
                    "attributes": entity.attributes
                },
                "related_entities": [
                    {
                        "id": rel_entity.id,
                        "name": rel_entity.name,
                        "type": rel_entity.entity_type.value,
                        "relationship_type": "related"  # Simplified
                    }
                    for rel_entity in related_entities[:5]  # Limit related entities
                ]
            })
        
        return {
            "query": query,
            "total_matches": len(matching_entities),
            "results": results,
            "graph_stats": await self.get_statistics()
        }
    
    async def get_entity_neighbors(self, entity_id: str, max_depth: int = 1) -> List[Dict[str, Any]]:
        """Get neighboring entities in the graph"""
        if entity_id not in self.entities:
            return []
        
        neighbors = []
        
        # Get direct neighbors
        for neighbor_id in self.graph.neighbors(entity_id):
            neighbor_entity = self.entities.get(neighbor_id)
            if neighbor_entity:
                # Get relationship info
                edge_data = self.graph.get_edge_data(entity_id, neighbor_id)
                relationship_types = [data.get('type', 'unknown') for data in edge_data.values()]
                
                neighbors.append({
                    "entity": {
                        "id": neighbor_entity.id,
                        "name": neighbor_entity.name,
                        "type": neighbor_entity.entity_type.value,
                        "confidence": neighbor_entity.confidence
                    },
                    "relationships": relationship_types,
                    "distance": 1
                })
        
        # Get second-degree neighbors if requested
        if max_depth > 1:
            second_degree = set()
            for neighbor_id in self.graph.neighbors(entity_id):
                for second_neighbor_id in self.graph.neighbors(neighbor_id):
                    if (second_neighbor_id != entity_id and 
                        second_neighbor_id not in [n["entity"]["id"] for n in neighbors]):
                        second_degree.add(second_neighbor_id)
            
            for neighbor_id in second_degree:
                neighbor_entity = self.entities.get(neighbor_id)
                if neighbor_entity:
                    neighbors.append({
                        "entity": {
                            "id": neighbor_entity.id,
                            "name": neighbor_entity.name,
                            "type": neighbor_entity.entity_type.value,
                            "confidence": neighbor_entity.confidence
                        },
                        "relationships": ["indirect"],
                        "distance": 2
                    })
        
        return neighbors
    
    async def discover_patterns(self) -> Dict[str, Any]:
        """Discover patterns and insights in the knowledge graph"""
        patterns = {}
        
        # Find most connected entities (hubs)
        degree_centrality = nx.degree_centrality(self.graph)
        top_hubs = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        
        patterns["knowledge_hubs"] = [
            {
                "entity_id": entity_id,
                "entity_name": self.entities[entity_id].name,
                "centrality_score": score,
                "connections": self.graph.degree(entity_id)
            }
            for entity_id, score in top_hubs if entity_id in self.entities
        ]
        
        # Find strongly connected components
        try:
            components = list(nx.strongly_connected_components(self.graph))
            largest_components = sorted(components, key=len, reverse=True)[:5]
            
            patterns["knowledge_clusters"] = [
                {
                    "size": len(component),
                    "entities": [
                        {
                            "id": entity_id,
                            "name": self.entities[entity_id].name,
                            "type": self.entities[entity_id].entity_type.value
                        }
                        for entity_id in list(component)[:10] if entity_id in self.entities
                    ]
                }
                for component in largest_components
            ]
        except:
            patterns["knowledge_clusters"] = []
        
        # Entity type distribution
        type_counts = Counter(entity.entity_type.value for entity in self.entities.values())
        patterns["entity_distribution"] = dict(type_counts)
        
        # Relationship type distribution
        rel_type_counts = Counter(rel.relation_type.value for rel in self.relationships.values())
        patterns["relationship_distribution"] = dict(rel_type_counts)
        
        return patterns
    
    def _find_similar_entity(self, entity: Entity) -> Optional[Entity]:
        """Find similar existing entity"""
        for existing_entity in self.entities.values():
            if (existing_entity.name.lower() == entity.name.lower() and 
                existing_entity.entity_type == entity.entity_type):
                return existing_entity
        return None
    
    def _find_similar_relationship(self, relationship: Relationship) -> Optional[Relationship]:
        """Find similar existing relationship"""
        for existing_rel in self.relationships.values():
            if (existing_rel.source_entity_id == relationship.source_entity_id and
                existing_rel.target_entity_id == relationship.target_entity_id and
                existing_rel.relation_type == relationship.relation_type):
                return existing_rel
        return None
    
    async def _merge_entities(self, existing: Entity, new: Entity) -> Entity:
        """Merge two similar entities"""
        # Update confidence (take maximum)
        existing.confidence = max(existing.confidence, new.confidence)
        
        # Merge attributes
        existing.attributes.update(new.attributes)
        
        # Merge aliases
        existing.aliases.update(new.aliases)
        existing.aliases.add(new.name)
        
        # Merge source references
        existing.source_references.update(new.source_references)
        
        # Update timestamp
        existing.updated_at = datetime.utcnow()
        
        return existing
    
    def _update_graph_node(self, entity: Entity):
        """Update graph node attributes"""
        if entity.id in self.graph:
            self.graph.nodes[entity.id].update({
                'name': entity.name,
                'type': entity.entity_type.value,
                'confidence': entity.confidence
            })
    
    def _update_graph_edge(self, relationship: Relationship):
        """Update graph edge attributes"""
        if self.graph.has_edge(relationship.source_entity_id, relationship.target_entity_id, relationship.id):
            self.graph.edges[relationship.source_entity_id, relationship.target_entity_id, relationship.id].update({
                'weight': relationship.weight,
                'confidence': relationship.confidence
            })
    
    async def _get_related_entities(self, entity_id: str, max_depth: int = 2) -> List[Entity]:
        """Get entities related to the given entity"""
        related_entities = []
        visited = set()
        
        def _get_neighbors(current_id: str, depth: int):
            if depth > max_depth or current_id in visited:
                return
            
            visited.add(current_id)
            
            for neighbor_id in self.graph.neighbors(current_id):
                if neighbor_id in self.entities and neighbor_id not in visited:
                    related_entities.append(self.entities[neighbor_id])
                    if depth < max_depth:
                        _get_neighbors(neighbor_id, depth + 1)
        
        _get_neighbors(entity_id, 0)
        return related_entities[:20]  # Limit results
    
    async def _update_clusters(self, entity_ids: List[str]):
        """Update knowledge clusters based on new entities"""
        # Simple clustering based on entity types and relationships
        # This is a simplified implementation - could be enhanced with ML clustering
        
        for entity_id in entity_ids:
            entity = self.entities.get(entity_id)
            if not entity:
                continue
            
            # Find or create cluster for this entity type
            cluster_name = f"{entity.entity_type.value}_cluster"
            
            if cluster_name not in self.clusters:
                self.clusters[cluster_name] = KnowledgeCluster(
                    id=cluster_name,
                    name=cluster_name.replace("_", " ").title(),
                    entities=set(),
                    description=f"Cluster of {entity.entity_type.value} entities"
                )
            
            self.clusters[cluster_name].entities.add(entity_id)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "total_clusters": len(self.clusters),
            "entity_types": {
                entity_type.value: len([e for e in self.entities.values() if e.entity_type == entity_type])
                for entity_type in EntityType
            },
            "relationship_types": {
                rel_type.value: len([r for r in self.relationships.values() if r.relation_type == rel_type])
                for rel_type in RelationType
            },
            "graph_density": nx.density(self.graph) if self.graph.number_of_nodes() > 0 else 0,
            "last_update": self.last_update.isoformat()
        }
    
    async def export_graph(self, format_type: str = "json") -> Dict[str, Any]:
        """Export knowledge graph in various formats"""
        if format_type == "json":
            return {
                "entities": [
                    {
                        "id": entity.id,
                        "name": entity.name,
                        "type": entity.entity_type.value,
                        "attributes": entity.attributes,
                        "confidence": entity.confidence,
                        "created_at": entity.created_at.isoformat()
                    }
                    for entity in self.entities.values()
                ],
                "relationships": [
                    {
                        "id": rel.id,
                        "source": rel.source_entity_id,
                        "target": rel.target_entity_id,
                        "type": rel.relation_type.value,
                        "weight": rel.weight,
                        "confidence": rel.confidence
                    }
                    for rel in self.relationships.values()
                ],
                "statistics": await self.get_statistics()
            }
        
        return {}
    
    async def cleanup(self):
        """Cleanup knowledge graph resources"""
        logger.info("Knowledge Graph cleanup completed")

# Global knowledge graph instance
knowledge_graph = KnowledgeGraph() 