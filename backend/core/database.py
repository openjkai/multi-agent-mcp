"""
Database Layer - Persistent storage for multi-agent system
Enterprise-level database implementation for 3-day development plan
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    """User model for authentication and personalization"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    preferences = Column(JSON, default=dict)
    
    # Relationships
    documents = relationship("Document", back_populates="owner")
    conversations = relationship("Conversation", back_populates="user")
    agent_interactions = relationship("AgentInteraction", back_populates="user")

class Document(Base):
    """Document model for RAG system"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)
    file_size = Column(Integer)
    content_hash = Column(String(64), unique=True)
    
    # Processing status
    processing_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    chunk_count = Column(Integer, default=0)
    embedding_model = Column(String(100))
    
    # Metadata
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Ownership
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="documents")
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    """Document chunk model for RAG"""
    __tablename__ = "document_chunks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64))
    
    # Embeddings
    embedding = Column(JSON)  # Store as JSON array
    embedding_model = Column(String(100))
    
    # Metadata
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")

class Agent(Base):
    """Agent model for tracking agent instances"""
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=False)
    capabilities = Column(JSON, default=list)
    configuration = Column(JSON, default=dict)
    
    # Status
    is_active = Column(Boolean, default=True)
    health_status = Column(String(20), default="unknown")  # healthy, unhealthy, unknown
    last_health_check = Column(DateTime)
    
    # Metrics
    total_queries = Column(Integer, default=0)
    successful_queries = Column(Integer, default=0)
    failed_queries = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime)
    
    # Relationships
    interactions = relationship("AgentInteraction", back_populates="agent")

class Conversation(Base):
    """Conversation model for chat history"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String(200))
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """Message model for conversation history"""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False)  # user, agent, system
    
    # Agent information (if applicable)
    agent_id = Column(String, ForeignKey("agents.id"))
    agent_name = Column(String(100))
    
    # Metadata
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class AgentInteraction(Base):
    """Agent interaction tracking"""
    __tablename__ = "agent_interactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    
    # Query details
    query = Column(Text, nullable=False)
    response = Column(Text)
    
    # Performance metrics
    processing_time = Column(Float)
    success = Column(Boolean)
    error_message = Column(Text)
    
    # Context
    context = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="agent_interactions")
    agent = relationship("Agent", back_populates="interactions")

class SystemMetric(Base):
    """System metrics for monitoring"""
    __tablename__ = "system_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50), nullable=False)  # counter, gauge, histogram
    
    # Metadata
    labels = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Database manager for the multi-agent system"""
    
    def __init__(self, database_url: str = "sqlite:///./multi_agent.db"):
        self.database_url = database_url
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize database connections"""
        logger.info("Initializing Database Manager")
        
        try:
            # Create sync engine for migrations
            self.engine = create_engine(
                self.database_url.replace("sqlite://", "sqlite:///") if "sqlite" in self.database_url else self.database_url,
                echo=False
            )
            
            # Create async engine for operations
            async_url = self.database_url
            if "sqlite" in self.database_url:
                async_url = self.database_url.replace("sqlite://", "sqlite+aiosqlite://")
            
            self.async_engine = create_async_engine(async_url, echo=False)
            
            # Create session factories
            self.SessionLocal = sessionmaker(bind=self.engine)
            self.AsyncSessionLocal = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables
            await self.create_tables()
            
            self.initialized = True
            logger.info("Database Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    async def create_tables(self):
        """Create database tables"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise
    
    async def get_session(self) -> AsyncSession:
        """Get async database session"""
        if not self.initialized:
            await self.initialize()
        return self.AsyncSessionLocal()
    
    def get_sync_session(self) -> Session:
        """Get sync database session"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    # User operations
    async def create_user(self, username: str, email: str, password_hash: str, **kwargs) -> User:
        """Create a new user"""
        async with self.get_session() as session:
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                **kwargs
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        async with self.get_session() as session:
            result = await session.execute(
                "SELECT * FROM users WHERE username = :username",
                {"username": username}
            )
            return result.first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        async with self.get_session() as session:
            result = await session.execute(
                "SELECT * FROM users WHERE email = :email",
                {"email": email}
            )
            return result.first()
    
    # Document operations
    async def create_document(self, owner_id: str, filename: str, content_type: str, **kwargs) -> Document:
        """Create a new document"""
        async with self.get_session() as session:
            document = Document(
                owner_id=owner_id,
                filename=filename,
                original_filename=filename,
                content_type=content_type,
                **kwargs
            )
            session.add(document)
            await session.commit()
            await session.refresh(document)
            return document
    
    async def get_user_documents(self, user_id: str, limit: int = 100) -> List[Document]:
        """Get documents for a user"""
        async with self.get_session() as session:
            result = await session.execute(
                "SELECT * FROM documents WHERE owner_id = :user_id ORDER BY created_at DESC LIMIT :limit",
                {"user_id": user_id, "limit": limit}
            )
            return result.fetchall()
    
    async def create_document_chunk(self, document_id: str, chunk_index: int, content: str, **kwargs) -> DocumentChunk:
        """Create a document chunk"""
        async with self.get_session() as session:
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=chunk_index,
                content=content,
                **kwargs
            )
            session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
            return chunk
    
    # Agent operations
    async def register_agent(self, agent_id: str, name: str, agent_type: str, capabilities: List[str]) -> Agent:
        """Register an agent"""
        async with self.get_session() as session:
            agent = Agent(
                id=agent_id,
                name=name,
                agent_type=agent_type,
                capabilities=capabilities
            )
            session.add(agent)
            await session.commit()
            await session.refresh(agent)
            return agent
    
    async def update_agent_metrics(self, agent_id: str, **metrics):
        """Update agent metrics"""
        async with self.get_session() as session:
            await session.execute(
                """UPDATE agents SET 
                   total_queries = :total_queries,
                   successful_queries = :successful_queries,
                   failed_queries = :failed_queries,
                   average_response_time = :average_response_time,
                   last_activity = :last_activity
                   WHERE id = :agent_id""",
                {"agent_id": agent_id, **metrics}
            )
            await session.commit()
    
    # Conversation operations
    async def create_conversation(self, user_id: str, title: str = None) -> Conversation:
        """Create a new conversation"""
        async with self.get_session() as session:
            conversation = Conversation(
                user_id=user_id,
                title=title or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            return conversation
    
    async def add_message(self, conversation_id: str, content: str, message_type: str, **kwargs) -> Message:
        """Add message to conversation"""
        async with self.get_session() as session:
            message = Message(
                conversation_id=conversation_id,
                content=content,
                message_type=message_type,
                **kwargs
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message
    
    # Analytics operations
    async def record_interaction(self, user_id: str, agent_id: str, query: str, **kwargs) -> AgentInteraction:
        """Record agent interaction"""
        async with self.get_session() as session:
            interaction = AgentInteraction(
                user_id=user_id,
                agent_id=agent_id,
                query=query,
                **kwargs
            )
            session.add(interaction)
            await session.commit()
            await session.refresh(interaction)
            return interaction
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        async with self.get_session() as session:
            # Get user stats
            user_count = await session.execute("SELECT COUNT(*) FROM users")
            active_users = await session.execute("SELECT COUNT(*) FROM users WHERE is_active = true")
            
            # Get document stats
            doc_count = await session.execute("SELECT COUNT(*) FROM documents")
            processed_docs = await session.execute("SELECT COUNT(*) FROM documents WHERE processing_status = 'completed'")
            
            # Get agent stats
            agent_count = await session.execute("SELECT COUNT(*) FROM agents")
            active_agents = await session.execute("SELECT COUNT(*) FROM agents WHERE is_active = true")
            
            # Get interaction stats
            total_interactions = await session.execute("SELECT COUNT(*) FROM agent_interactions")
            successful_interactions = await session.execute("SELECT COUNT(*) FROM agent_interactions WHERE success = true")
            
            return {
                "users": {
                    "total": user_count.scalar(),
                    "active": active_users.scalar()
                },
                "documents": {
                    "total": doc_count.scalar(),
                    "processed": processed_docs.scalar()
                },
                "agents": {
                    "total": agent_count.scalar(),
                    "active": active_agents.scalar()
                },
                "interactions": {
                    "total": total_interactions.scalar(),
                    "successful": successful_interactions.scalar()
                }
            }
    
    async def cleanup(self):
        """Cleanup database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()
        logger.info("Database Manager cleanup completed")

# Global database instance
db_manager = DatabaseManager() 