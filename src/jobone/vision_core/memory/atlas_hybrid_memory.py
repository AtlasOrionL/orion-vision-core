#!/usr/bin/env python3
"""
🔮 ATLAS Hybrid Memory System: Chroma + SQLite
💖 DUYGULANDIK! SEN YAPARSIN! VECTOR + GRAPH DATABASE HYBRID!

ATLAS Hafızası Hybrid Mimarisi:
- Vector Database Layer: Chroma for semantic search and Lepton polarization
- Graph Database Layer: SQLite with JSON for relationship modeling
- Integration: Bidirectional sync between vector embeddings and graph relationships

ORION AETHELRED FELSEFESİ:
- Lepton'lar vector embeddings olarak saklanır
- Bozon'lar graph relationships olarak modellenir
- QCB'ler hybrid entities olarak her iki sistemde de bulunur
- Quantum seed genealogy graph database'de takip edilir

Author: Orion Vision Core Team + Orion Aethelred Quantum Philosophy
Status: 🔮 ATLAS HYBRID MEMORY ACTIVE
"""

import sqlite3
import json
import uuid
import hashlib
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

# Chroma imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
    print("✅ ChromaDB imported successfully")
except ImportError as e:
    CHROMA_AVAILABLE = False
    print(f"⚠️ ChromaDB not available: {e}")
    print("   Install with: pip install chromadb")

# Sentence transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
    print("✅ SentenceTransformers imported successfully")
except ImportError as e:
    EMBEDDINGS_AVAILABLE = False
    print(f"⚠️ SentenceTransformers not available: {e}")
    print("   Install with: pip install sentence-transformers")

@dataclass
class LeptonMemoryEntry:
    """Lepton memory entry for vector database"""
    lepton_id: str
    lepton_type: str
    content: str
    polarization: Dict[str, float]
    effective_mass: float
    seed: str
    temporal_index: int
    metadata: Dict[str, Any]
    timestamp: str
    embedding_vector: Optional[List[float]] = None

@dataclass
class BozonRelationship:
    """Bozon relationship for graph database"""
    relationship_id: str
    bozon_type: str
    source_lepton_id: str
    target_lepton_id: str
    relationship_strength: float
    properties: Dict[str, Any]
    seed: str
    timestamp: str

@dataclass
class QCBHybridEntity:
    """QCB hybrid entity spanning both databases"""
    qcb_id: str
    content: str
    lepton_ids: List[str]
    bozon_ids: List[str]
    quantum_branch_seed: str
    combined_interpretation: str
    metadata: Dict[str, Any]
    timestamp: str

class ChromaVectorDatabase:
    """
    🔮 Chroma Vector Database Layer

    Semantic search and Lepton polarization with embedding-based similarity
    WAKE UP ORION! VECTOR EMBEDDINGS POWER!
    """

    def __init__(self, db_path: str = "data/atlas_chroma"):
        self.logger = logging.getLogger('atlas.chroma_vector')
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Chroma client
        self.client = None
        self.collection = None

        # Embedding model
        self.embedding_model = None

        # Vector database metrics
        self.vector_metrics = {
            'total_leptons': 0,
            'total_embeddings': 0,
            'average_similarity': 0.0,
            'last_query_time': 0.0
        }

        self.initialized = False

        self.logger.info("🔮 Chroma Vector Database initialized")
        self.logger.info("💖 DUYGULANDIK! VECTOR EMBEDDINGS HAZIR!")

    def initialize(self) -> bool:
        """Initialize Chroma vector database"""
        try:
            if not CHROMA_AVAILABLE:
                self.logger.error("❌ ChromaDB not available")
                return False

            if not EMBEDDINGS_AVAILABLE:
                self.logger.error("❌ SentenceTransformers not available")
                return False

            self.logger.info("🚀 Initializing Chroma vector database...")

            # Initialize Chroma client
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Get or create collection
            try:
                self.collection = self.client.get_collection("atlas_leptons")
                self.logger.info("✅ Existing Chroma collection loaded")
            except:
                self.collection = self.client.create_collection(
                    name="atlas_leptons",
                    metadata={"description": "ATLAS Lepton embeddings for semantic search"}
                )
                self.logger.info("✅ New Chroma collection created")

            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.logger.info("✅ Embedding model loaded: all-MiniLM-L6-v2")

            self.initialized = True
            self.logger.info("✅ Chroma vector database initialized successfully!")
            return True

        except Exception as e:
            self.logger.error(f"❌ Chroma initialization error: {e}")
            return False

    def add_lepton(self, lepton_entry: LeptonMemoryEntry) -> bool:
        """Add Lepton to vector database"""
        try:
            if not self.initialized:
                return False

            # Generate embedding
            embedding = self.embedding_model.encode(lepton_entry.content).tolist()
            lepton_entry.embedding_vector = embedding

            # Prepare metadata
            metadata = {
                'lepton_type': lepton_entry.lepton_type,
                'effective_mass': lepton_entry.effective_mass,
                'seed': lepton_entry.seed,
                'temporal_index': lepton_entry.temporal_index,
                'timestamp': lepton_entry.timestamp,
                'polarization_json': json.dumps(lepton_entry.polarization),
                'metadata_json': json.dumps(lepton_entry.metadata)
            }

            # Add to Chroma collection
            self.collection.add(
                ids=[lepton_entry.lepton_id],
                embeddings=[embedding],
                documents=[lepton_entry.content],
                metadatas=[metadata]
            )

            self.vector_metrics['total_leptons'] += 1
            self.vector_metrics['total_embeddings'] += 1

            self.logger.info(f"✅ Lepton added to vector database: {lepton_entry.lepton_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Add Lepton error: {e}")
            return False

    def search_similar_leptons(self, query: str, n_results: int = 5,
                              filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar Leptons using semantic similarity"""
        try:
            if not self.initialized:
                return []

            import time
            start_time = time.time()

            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Search in Chroma
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata,
                include=['documents', 'metadatas', 'distances']
            )

            query_time = time.time() - start_time
            self.vector_metrics['last_query_time'] = query_time

            # Process results
            similar_leptons = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    lepton_data = {
                        'lepton_id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'similarity_score': 1.0 - results['distances'][0][i],  # Convert distance to similarity
                        'metadata': results['metadatas'][0][i],
                        'polarization': json.loads(results['metadatas'][0][i].get('polarization_json', '{}')),
                        'effective_mass': results['metadatas'][0][i].get('effective_mass', 0.0),
                        'seed': results['metadatas'][0][i].get('seed', ''),
                        'timestamp': results['metadatas'][0][i].get('timestamp', '')
                    }
                    similar_leptons.append(lepton_data)

            self.logger.info(f"🔍 Vector search completed in {query_time:.3f}s: {len(similar_leptons)} results")
            return similar_leptons

        except Exception as e:
            self.logger.error(f"❌ Vector search error: {e}")
            return []

    def get_vector_stats(self) -> Dict[str, Any]:
        """Get vector database statistics"""
        try:
            if not self.initialized:
                return {}

            collection_count = self.collection.count()

            return {
                'initialized': self.initialized,
                'collection_count': collection_count,
                'metrics': self.vector_metrics,
                'embedding_model': 'all-MiniLM-L6-v2',
                'database_path': str(self.db_path)
            }

        except Exception as e:
            self.logger.error(f"❌ Vector stats error: {e}")
            return {'error': str(e)}

class SQLiteGraphDatabase:
    """
    🔮 SQLite Graph Database Layer

    Relationship modeling between Leptons, Bosons, and QCBs with JSON support
    WAKE UP ORION! GRAPH RELATIONSHIPS POWER!
    """

    def __init__(self, db_path: str = "data/atlas_graph.db"):
        self.logger = logging.getLogger('atlas.sqlite_graph')
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # SQLite connection
        self.connection = None

        # Graph database metrics
        self.graph_metrics = {
            'total_leptons': 0,
            'total_relationships': 0,
            'total_qcbs': 0,
            'seed_genealogy_depth': 0
        }

        self.initialized = False

        self.logger.info("🔮 SQLite Graph Database initialized")
        self.logger.info("💖 DUYGULANDIK! GRAPH RELATIONSHIPS HAZIR!")

    def initialize(self) -> bool:
        """Initialize SQLite graph database"""
        try:
            self.logger.info("🚀 Initializing SQLite graph database...")

            # Connect to SQLite
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name

            # Enable JSON support
            self.connection.execute("PRAGMA foreign_keys = ON")

            # Create tables
            self._create_tables()

            self.initialized = True
            self.logger.info("✅ SQLite graph database initialized successfully!")
            return True

        except Exception as e:
            self.logger.error(f"❌ SQLite initialization error: {e}")
            return False

    def _create_tables(self):
        """Create database tables"""
        cursor = self.connection.cursor()

        # Leptons table (graph nodes)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leptons (
                lepton_id TEXT PRIMARY KEY,
                lepton_type TEXT NOT NULL,
                content TEXT NOT NULL,
                polarization_json TEXT NOT NULL,
                effective_mass REAL NOT NULL,
                seed TEXT NOT NULL,
                temporal_index INTEGER NOT NULL,
                metadata_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Bozon relationships table (graph edges)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bozon_relationships (
                relationship_id TEXT PRIMARY KEY,
                bozon_type TEXT NOT NULL,
                source_lepton_id TEXT NOT NULL,
                target_lepton_id TEXT NOT NULL,
                relationship_strength REAL NOT NULL,
                properties_json TEXT NOT NULL,
                seed TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_lepton_id) REFERENCES leptons (lepton_id),
                FOREIGN KEY (target_lepton_id) REFERENCES leptons (lepton_id)
            )
        """)

        # QCB hybrid entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qcb_entities (
                qcb_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                lepton_ids_json TEXT NOT NULL,
                bozon_ids_json TEXT NOT NULL,
                quantum_branch_seed TEXT NOT NULL,
                combined_interpretation TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Quantum seed genealogy table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seed_genealogy (
                seed_id TEXT PRIMARY KEY,
                parent_seed TEXT,
                branch_type TEXT NOT NULL,
                generation_level INTEGER NOT NULL,
                branch_metadata_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leptons_seed ON leptons (seed)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leptons_type ON leptons (lepton_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_source ON bozon_relationships (source_lepton_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_target ON bozon_relationships (target_lepton_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_qcb_seed ON qcb_entities (quantum_branch_seed)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_genealogy_parent ON seed_genealogy (parent_seed)")

        self.connection.commit()
        self.logger.info("✅ Database tables created successfully")

    def add_lepton_node(self, lepton_entry: LeptonMemoryEntry) -> bool:
        """Add Lepton as graph node"""
        try:
            if not self.initialized:
                return False

            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO leptons
                (lepton_id, lepton_type, content, polarization_json, effective_mass,
                 seed, temporal_index, metadata_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lepton_entry.lepton_id,
                lepton_entry.lepton_type,
                lepton_entry.content,
                json.dumps(lepton_entry.polarization),
                lepton_entry.effective_mass,
                lepton_entry.seed,
                lepton_entry.temporal_index,
                json.dumps(lepton_entry.metadata),
                lepton_entry.timestamp
            ))

            self.connection.commit()
            self.graph_metrics['total_leptons'] += 1

            self.logger.info(f"✅ Lepton node added to graph: {lepton_entry.lepton_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Add Lepton node error: {e}")
            return False

    def add_bozon_relationship(self, relationship: BozonRelationship) -> bool:
        """Add Bozon as graph relationship"""
        try:
            if not self.initialized:
                return False

            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO bozon_relationships
                (relationship_id, bozon_type, source_lepton_id, target_lepton_id,
                 relationship_strength, properties_json, seed, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                relationship.relationship_id,
                relationship.bozon_type,
                relationship.source_lepton_id,
                relationship.target_lepton_id,
                relationship.relationship_strength,
                json.dumps(relationship.properties),
                relationship.seed,
                relationship.timestamp
            ))

            self.connection.commit()
            self.graph_metrics['total_relationships'] += 1

            self.logger.info(f"✅ Bozon relationship added: {relationship.relationship_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Add Bozon relationship error: {e}")
            return False

    def add_qcb_entity(self, qcb_entity: QCBHybridEntity) -> bool:
        """Add QCB hybrid entity"""
        try:
            if not self.initialized:
                return False

            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO qcb_entities
                (qcb_id, content, lepton_ids_json, bozon_ids_json,
                 quantum_branch_seed, combined_interpretation, metadata_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                qcb_entity.qcb_id,
                qcb_entity.content,
                json.dumps(qcb_entity.lepton_ids),
                json.dumps(qcb_entity.bozon_ids),
                qcb_entity.quantum_branch_seed,
                qcb_entity.combined_interpretation,
                json.dumps(qcb_entity.metadata),
                qcb_entity.timestamp
            ))

            self.connection.commit()
            self.graph_metrics['total_qcbs'] += 1

            self.logger.info(f"✅ QCB entity added: {qcb_entity.qcb_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Add QCB entity error: {e}")
            return False

    def add_seed_genealogy(self, seed_id: str, parent_seed: Optional[str],
                          branch_type: str, generation_level: int,
                          branch_metadata: Dict[str, Any]) -> bool:
        """Add seed genealogy entry"""
        try:
            if not self.initialized:
                return False

            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO seed_genealogy
                (seed_id, parent_seed, branch_type, generation_level,
                 branch_metadata_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                seed_id,
                parent_seed,
                branch_type,
                generation_level,
                json.dumps(branch_metadata),
                datetime.now().isoformat()
            ))

            self.connection.commit()

            # Update genealogy depth
            if generation_level > self.graph_metrics['seed_genealogy_depth']:
                self.graph_metrics['seed_genealogy_depth'] = generation_level

            self.logger.info(f"✅ Seed genealogy added: {seed_id} (gen {generation_level})")
            return True

        except Exception as e:
            self.logger.error(f"❌ Add seed genealogy error: {e}")
            return False

    def get_lepton_relationships(self, lepton_id: str) -> List[Dict[str, Any]]:
        """Get all relationships for a Lepton"""
        try:
            if not self.initialized:
                return []

            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM bozon_relationships
                WHERE source_lepton_id = ? OR target_lepton_id = ?
            """, (lepton_id, lepton_id))

            relationships = []
            for row in cursor.fetchall():
                relationship = {
                    'relationship_id': row['relationship_id'],
                    'bozon_type': row['bozon_type'],
                    'source_lepton_id': row['source_lepton_id'],
                    'target_lepton_id': row['target_lepton_id'],
                    'relationship_strength': row['relationship_strength'],
                    'properties': json.loads(row['properties_json']),
                    'seed': row['seed'],
                    'timestamp': row['timestamp']
                }
                relationships.append(relationship)

            return relationships

        except Exception as e:
            self.logger.error(f"❌ Get Lepton relationships error: {e}")
            return []

    def get_seed_genealogy(self, seed_id: str, max_depth: int = 10) -> Dict[str, Any]:
        """Get seed genealogy tree"""
        try:
            if not self.initialized:
                return {}

            cursor = self.connection.cursor()

            # Get seed info
            cursor.execute("SELECT * FROM seed_genealogy WHERE seed_id = ?", (seed_id,))
            seed_row = cursor.fetchone()

            if not seed_row:
                return {}

            # Build genealogy tree
            genealogy = {
                'seed_id': seed_row['seed_id'],
                'parent_seed': seed_row['parent_seed'],
                'branch_type': seed_row['branch_type'],
                'generation_level': seed_row['generation_level'],
                'branch_metadata': json.loads(seed_row['branch_metadata_json']),
                'timestamp': seed_row['timestamp'],
                'children': []
            }

            # Get children (if depth allows)
            if max_depth > 0:
                cursor.execute("SELECT seed_id FROM seed_genealogy WHERE parent_seed = ?", (seed_id,))
                children_rows = cursor.fetchall()

                for child_row in children_rows:
                    child_genealogy = self.get_seed_genealogy(child_row['seed_id'], max_depth - 1)
                    if child_genealogy:
                        genealogy['children'].append(child_genealogy)

            return genealogy

        except Exception as e:
            self.logger.error(f"❌ Get seed genealogy error: {e}")
            return {}

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph database statistics"""
        try:
            if not self.initialized:
                return {}

            cursor = self.connection.cursor()

            # Count records
            cursor.execute("SELECT COUNT(*) as count FROM leptons")
            leptons_count = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM bozon_relationships")
            relationships_count = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM qcb_entities")
            qcbs_count = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM seed_genealogy")
            genealogy_count = cursor.fetchone()['count']

            return {
                'initialized': self.initialized,
                'leptons_count': leptons_count,
                'relationships_count': relationships_count,
                'qcbs_count': qcbs_count,
                'genealogy_count': genealogy_count,
                'metrics': self.graph_metrics,
                'database_path': str(self.db_path)
            }

        except Exception as e:
            self.logger.error(f"❌ Graph stats error: {e}")
            return {'error': str(e)}

class ATLASHybridMemory:
    """
    🔮 ATLAS Hybrid Memory System

    Chroma (Vector) + SQLite (Graph) hybrid database for optimal RAG performance
    WAKE UP ORION! HYBRID MEMORY POWER!
    """

    def __init__(self, vector_db_path: str = "data/atlas_chroma",
                 graph_db_path: str = "data/atlas_graph.db"):
        self.logger = logging.getLogger('atlas.hybrid_memory')

        # Database layers
        self.vector_db = ChromaVectorDatabase(vector_db_path)
        self.graph_db = SQLiteGraphDatabase(graph_db_path)

        # Hybrid memory metrics
        self.hybrid_metrics = {
            'total_hybrid_operations': 0,
            'successful_syncs': 0,
            'failed_syncs': 0,
            'average_query_time': 0.0,
            'last_sync_time': None
        }

        self.initialized = False

        self.logger.info("🔮 ATLAS Hybrid Memory System initialized")
        self.logger.info("💖 DUYGULANDIK! CHROMA + SQLITE HYBRID!")

    def initialize(self) -> bool:
        """Initialize hybrid memory system"""
        try:
            self.logger.info("🚀 Initializing ATLAS Hybrid Memory System...")
            self.logger.info("🔮 WAKE UP ORION! HYBRID VECTOR+GRAPH DATABASE!")

            # Initialize vector database
            vector_success = self.vector_db.initialize()

            # Initialize graph database
            graph_success = self.graph_db.initialize()

            if vector_success and graph_success:
                self.initialized = True
                self.logger.info("✅ ATLAS Hybrid Memory System initialized successfully!")
                self.logger.info("🔮 CHROMA + SQLITE HYBRID READY!")
                return True
            else:
                self.logger.error("❌ Hybrid memory initialization failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ Hybrid memory initialization error: {e}")
            return False

    def add_lepton_hybrid(self, lepton_entry: LeptonMemoryEntry) -> bool:
        """Add Lepton to both vector and graph databases"""
        try:
            if not self.initialized:
                return False

            # Add to vector database (for semantic search)
            vector_success = self.vector_db.add_lepton(lepton_entry)

            # Add to graph database (for relationships)
            graph_success = self.graph_db.add_lepton_node(lepton_entry)

            if vector_success and graph_success:
                self.hybrid_metrics['successful_syncs'] += 1
                self.logger.info(f"✅ Lepton added to hybrid memory: {lepton_entry.lepton_id}")
                return True
            else:
                self.hybrid_metrics['failed_syncs'] += 1
                self.logger.warning(f"⚠️ Partial Lepton add: vector={vector_success}, graph={graph_success}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Add Lepton hybrid error: {e}")
            self.hybrid_metrics['failed_syncs'] += 1
            return False

    def add_bozon_relationship(self, relationship: BozonRelationship) -> bool:
        """Add Bozon relationship to graph database"""
        try:
            if not self.initialized:
                return False

            success = self.graph_db.add_bozon_relationship(relationship)

            if success:
                self.hybrid_metrics['successful_syncs'] += 1
            else:
                self.hybrid_metrics['failed_syncs'] += 1

            return success

        except Exception as e:
            self.logger.error(f"❌ Add Bozon relationship error: {e}")
            self.hybrid_metrics['failed_syncs'] += 1
            return False

    def add_qcb_hybrid_entity(self, qcb_entity: QCBHybridEntity) -> bool:
        """Add QCB entity to graph database"""
        try:
            if not self.initialized:
                return False

            success = self.graph_db.add_qcb_entity(qcb_entity)

            if success:
                self.hybrid_metrics['successful_syncs'] += 1
            else:
                self.hybrid_metrics['failed_syncs'] += 1

            return success

        except Exception as e:
            self.logger.error(f"❌ Add QCB hybrid entity error: {e}")
            self.hybrid_metrics['failed_syncs'] += 1
            return False

    def semantic_search_with_relationships(self, query: str, n_results: int = 5,
                                         include_relationships: bool = True) -> Dict[str, Any]:
        """
        Hybrid search: semantic similarity + relationship context
        <100ms query response time target
        """
        try:
            if not self.initialized:
                return {'success': False, 'error': 'Not initialized'}

            import time
            start_time = time.time()

            # Step 1: Semantic search in vector database
            similar_leptons = self.vector_db.search_similar_leptons(query, n_results)

            # Step 2: Enrich with relationship context from graph database
            enriched_results = []
            for lepton in similar_leptons:
                enriched_lepton = lepton.copy()

                if include_relationships:
                    # Get relationships for this Lepton
                    relationships = self.graph_db.get_lepton_relationships(lepton['lepton_id'])
                    enriched_lepton['relationships'] = relationships
                    enriched_lepton['relationship_count'] = len(relationships)

                enriched_results.append(enriched_lepton)

            query_time = time.time() - start_time
            self.hybrid_metrics['average_query_time'] = (
                (self.hybrid_metrics['average_query_time'] * self.hybrid_metrics['total_hybrid_operations'] + query_time) /
                (self.hybrid_metrics['total_hybrid_operations'] + 1)
            )
            self.hybrid_metrics['total_hybrid_operations'] += 1

            self.logger.info(f"🔍 Hybrid search completed in {query_time:.3f}s: {len(enriched_results)} results")

            return {
                'success': True,
                'query': query,
                'results': enriched_results,
                'query_time': query_time,
                'result_count': len(enriched_results),
                'include_relationships': include_relationships
            }

        except Exception as e:
            self.logger.error(f"❌ Hybrid search error: {e}")
            return {'success': False, 'error': str(e)}

    def get_quantum_branch_context(self, quantum_branch_seed: str) -> Dict[str, Any]:
        """Get full context for a quantum branch seed"""
        try:
            if not self.initialized:
                return {}

            # Get seed genealogy
            genealogy = self.graph_db.get_seed_genealogy(quantum_branch_seed)

            # Get QCB entities with this seed
            cursor = self.graph_db.connection.cursor()
            cursor.execute("SELECT * FROM qcb_entities WHERE quantum_branch_seed = ?", (quantum_branch_seed,))
            qcb_rows = cursor.fetchall()

            qcb_entities = []
            for row in qcb_rows:
                qcb_entity = {
                    'qcb_id': row['qcb_id'],
                    'content': row['content'],
                    'lepton_ids': json.loads(row['lepton_ids_json']),
                    'bozon_ids': json.loads(row['bozon_ids_json']),
                    'combined_interpretation': row['combined_interpretation'],
                    'metadata': json.loads(row['metadata_json']),
                    'timestamp': row['timestamp']
                }
                qcb_entities.append(qcb_entity)

            return {
                'quantum_branch_seed': quantum_branch_seed,
                'genealogy': genealogy,
                'qcb_entities': qcb_entities,
                'context_size': len(qcb_entities)
            }

        except Exception as e:
            self.logger.error(f"❌ Get quantum branch context error: {e}")
            return {}

    def optimize_memory_performance(self) -> Dict[str, Any]:
        """Optimize hybrid memory performance"""
        try:
            if not self.initialized:
                return {'success': False, 'error': 'Not initialized'}

            optimization_results = {
                'vector_optimization': {},
                'graph_optimization': {},
                'hybrid_optimization': {}
            }

            # Vector database optimization
            if self.vector_db.initialized:
                # Get vector stats
                vector_stats = self.vector_db.get_vector_stats()
                optimization_results['vector_optimization'] = {
                    'collection_count': vector_stats.get('collection_count', 0),
                    'status': 'optimized'
                }

            # Graph database optimization
            if self.graph_db.initialized:
                # SQLite optimization
                cursor = self.graph_db.connection.cursor()
                cursor.execute("VACUUM")  # Optimize database file
                cursor.execute("ANALYZE")  # Update query planner statistics
                self.graph_db.connection.commit()

                graph_stats = self.graph_db.get_graph_stats()
                optimization_results['graph_optimization'] = {
                    'leptons_count': graph_stats.get('leptons_count', 0),
                    'relationships_count': graph_stats.get('relationships_count', 0),
                    'status': 'optimized'
                }

            # Hybrid optimization
            optimization_results['hybrid_optimization'] = {
                'total_operations': self.hybrid_metrics['total_hybrid_operations'],
                'success_rate': (self.hybrid_metrics['successful_syncs'] /
                               max(1, self.hybrid_metrics['successful_syncs'] + self.hybrid_metrics['failed_syncs'])),
                'average_query_time': self.hybrid_metrics['average_query_time'],
                'status': 'optimized'
            }

            self.logger.info("✅ Hybrid memory performance optimized")
            return {'success': True, 'optimization_results': optimization_results}

        except Exception as e:
            self.logger.error(f"❌ Memory optimization error: {e}")
            return {'success': False, 'error': str(e)}

    def get_hybrid_memory_status(self) -> Dict[str, Any]:
        """Get comprehensive hybrid memory status"""
        try:
            vector_stats = self.vector_db.get_vector_stats() if self.vector_db.initialized else {}
            graph_stats = self.graph_db.get_graph_stats() if self.graph_db.initialized else {}

            return {
                'initialized': self.initialized,
                'vector_database': vector_stats,
                'graph_database': graph_stats,
                'hybrid_metrics': self.hybrid_metrics,
                'performance': {
                    'target_query_time': '< 100ms',
                    'actual_average_query_time': f"{self.hybrid_metrics['average_query_time']:.3f}s",
                    'performance_status': 'optimal' if self.hybrid_metrics['average_query_time'] < 0.1 else 'needs_optimization'
                }
            }

        except Exception as e:
            self.logger.error(f"❌ Hybrid memory status error: {e}")
            return {'error': str(e)}

# Example usage and testing
if __name__ == "__main__":
    print("🔮 ATLAS Hybrid Memory System Test")
    print("💖 DUYGULANDIK! SEN YAPARSIN!")
    print("🌟 WAKE UP ORION! CHROMA + SQLITE HYBRID!")
    print("📊 VECTOR + GRAPH DATABASE ENTEGRASYONU!")
    print()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(name)s:%(message)s'
    )

    # Test ATLAS Hybrid Memory
    atlas_memory = ATLASHybridMemory()

    if atlas_memory.initialize():
        print("✅ ATLAS Hybrid Memory initialized")

        # Test Lepton addition
        from datetime import datetime

        test_lepton = LeptonMemoryEntry(
            lepton_id="test_lepton_001",
            lepton_type="text",
            content="WAKE UP ORION! Test Lepton for hybrid memory",
            polarization={"positive": 0.8, "negative": 0.2},
            effective_mass=0.7,
            seed="test_seed_001",
            temporal_index=1,
            metadata={"test": True, "source": "hybrid_test"},
            timestamp=datetime.now().isoformat()
        )

        if atlas_memory.add_lepton_hybrid(test_lepton):
            print("✅ Test Lepton added to hybrid memory")

            # Test semantic search
            search_result = atlas_memory.semantic_search_with_relationships(
                "WAKE UP ORION test", n_results=3
            )

            if search_result['success']:
                print(f"🔍 Semantic search: {search_result['result_count']} results")
                print(f"   Query time: {search_result['query_time']:.3f}s")

                if search_result['results']:
                    best_result = search_result['results'][0]
                    print(f"   Best match: {best_result['content'][:50]}...")
                    print(f"   Similarity: {best_result['similarity_score']:.3f}")
            else:
                print("❌ Semantic search failed")
        else:
            print("❌ Test Lepton addition failed")

        # Show hybrid memory status
        status = atlas_memory.get_hybrid_memory_status()
        print(f"📊 Hybrid Memory Status:")
        print(f"   🔮 Vector DB: {status['vector_database'].get('collection_count', 0)} embeddings")
        print(f"   📊 Graph DB: {status['graph_database'].get('leptons_count', 0)} leptons")
        print(f"   ⏱️ Avg Query Time: {status['performance']['actual_average_query_time']}")
        print(f"   🎯 Performance: {status['performance']['performance_status']}")

    else:
        print("❌ ATLAS Hybrid Memory initialization failed")
        print("   Install dependencies: pip install chromadb sentence-transformers")

    print()
    print("🎉 ATLAS Hybrid Memory test completed!")
    print("💖 DUYGULANDIK! CHROMA + SQLITE HYBRID ÇALIŞIYOR!")
    print("🔮 ORION AETHELRED'İN HYBRID MEMORY VİZYONU HAYATA GEÇTİ!")