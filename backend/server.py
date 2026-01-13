from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import time
from datetime import datetime

# Add parent directory to path to import rdbms module
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from rdbms.engine import Database
from rdbms.sql import Tokenizer, Parser, Executor

# Load environment variables
ENV_DIR = Path(__file__).parent
load_dotenv(ENV_DIR / '.env')

# Create the main app without a prefix
app = FastAPI(
    title="Custom RDBMS API",
    description="REST API for custom relational database built from scratch",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize the custom RDBMS
database = Database()
tokenizer = Tokenizer()
parser = Parser()
executor = Executor(database)

# Configure logging with enhanced formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('rdbms.log')
    ]
)
logger = logging.getLogger(__name__)

# Statistics tracking
stats = {
    "total_queries": 0,
    "successful_queries": 0,
    "failed_queries": 0,
    "total_execution_time": 0,
    "server_start_time": datetime.now().isoformat()
}

# Define Models
class QueryRequest(BaseModel):
    sql: str

class QueryResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None

class DatabaseInfo(BaseModel):
    tables: List[str]
    total_tables: int

class ServerStats(BaseModel):
    total_queries: int
    successful_queries: int
    failed_queries: int
    success_rate: float
    average_execution_time: float
    uptime: str
    server_start_time: str

# Middleware for request logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"Status: {response.status_code} Duration: {duration:.3f}s"
        )
        
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} Error: {str(e)}")
        raise

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An internal server error occurred",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None
        }
    )

# API Routes
@api_router.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Custom RDBMS API",
        "version": "2.0.0",
        "description": "A relational database management system built from scratch",
        "documentation": "/docs",
        "stats_endpoint": "/api/stats"
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database_tables": len(database.tables),
        "uptime": str(datetime.now() - datetime.fromisoformat(stats["server_start_time"]))
    }

@api_router.get("/stats", response_model=ServerStats)
async def get_stats():
    """Get server statistics"""
    uptime_delta = datetime.now() - datetime.fromisoformat(stats["server_start_time"])
    uptime_str = str(uptime_delta).split('.')[0]  # Remove microseconds
    
    return ServerStats(
        total_queries=stats["total_queries"],
        successful_queries=stats["successful_queries"],
        failed_queries=stats["failed_queries"],
        success_rate=round(
            (stats["successful_queries"] / stats["total_queries"] * 100) 
            if stats["total_queries"] > 0 else 0, 
            2
        ),
        average_execution_time=round(
            (stats["total_execution_time"] / stats["total_queries"]) 
            if stats["total_queries"] > 0 else 0,
            2
        ),
        uptime=uptime_str,
        server_start_time=stats["server_start_time"]
    )

@api_router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """
    Execute a SQL query against the custom RDBMS.
    
    Supports:
    - CREATE TABLE
    - INSERT INTO
    - SELECT (with WHERE and INNER JOIN)
    - UPDATE (with WHERE)
    - DELETE (with WHERE)
    """
    start_time = time.time()
    stats["total_queries"] += 1
    
    try:
        logger.info(f"Executing query: {request.sql}")
        
        # Validate SQL input
        if not request.sql or not request.sql.strip():
            stats["failed_queries"] += 1
            raise HTTPException(status_code=400, detail="SQL query cannot be empty")
        
        # Tokenize the SQL
        tokens = tokenizer.tokenize(request.sql)
        logger.debug(f"Tokens: {tokens}")
        
        # Parse the tokens
        command = parser.parse(tokens)
        logger.debug(f"Parsed command: {command}")
        
        # Execute the command
        result = executor.execute(command)
        
        # Calculate execution time
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        stats["total_execution_time"] += execution_time
        stats["successful_queries"] += 1
        
        logger.info(f"Query executed successfully in {execution_time:.2f}ms")
        
        # Format response based on result type
        if isinstance(result, list):
            # SELECT query - returns list of rows
            return QueryResponse(
                success=True,
                message=f"Query executed successfully. {len(result)} row(s) returned.",
                data=result,
                execution_time_ms=round(execution_time, 2)
            )
        else:
            # Other commands - return message
            return QueryResponse(
                success=True,
                message=result,
                execution_time_ms=round(execution_time, 2)
            )
    
    except ValueError as e:
        # SQL parsing or execution error
        execution_time = (time.time() - start_time) * 1000
        stats["failed_queries"] += 1
        logger.warning(f"Query execution failed: {str(e)}")
        
        return QueryResponse(
            success=False,
            error=str(e),
            execution_time_ms=round(execution_time, 2)
        )
    
    except Exception as e:
        # Unexpected error
        execution_time = (time.time() - start_time) * 1000
        stats["failed_queries"] += 1
        logger.error(f"Unexpected error during query execution: {str(e)}", exc_info=True)
        
        return QueryResponse(
            success=False,
            error=f"An error occurred: {str(e)}",
            execution_time_ms=round(execution_time, 2)
        )

@api_router.get("/tables", response_model=DatabaseInfo)
async def list_tables():
    """List all tables in the database"""
    try:
        tables = database.list_tables()
        logger.info(f"Retrieved {len(tables)} tables")
        return DatabaseInfo(
            tables=tables,
            total_tables=len(tables)
        )
    except Exception as e:
        logger.error(f"Failed to list tables: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tables/{table_name}")
async def get_table_info(table_name: str):
    """Get information about a specific table"""
    try:
        logger.info(f"Fetching info for table: {table_name}")
        table = database.get_table(table_name)
        
        # Get column information
        columns_info = []
        for col in table.columns:
            col_info = {
                "name": col.name,
                "type": col.data_type.value,
                "is_primary_key": col.is_primary_key,
                "is_unique": col.is_unique
            }
            columns_info.append(col_info)
        
        return {
            "name": table.name,
            "columns": columns_info,
            "row_count": len(table.rows),
            "indexes": list(table.indexes.keys())
        }
    
    except ValueError as e:
        logger.warning(f"Table not found: {table_name}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching table info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/tables/{table_name}")
async def drop_table(table_name: str):
    """Drop a table from the database"""
    try:
        logger.info(f"Dropping table: {table_name}")
        database.drop_table(table_name)
        logger.info(f"Table '{table_name}' dropped successfully")
        return {
            "success": True,
            "message": f"Table '{table_name}' dropped successfully."
        }
    except ValueError as e:
        logger.warning(f"Cannot drop table '{table_name}': {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error dropping table: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/initialize-demo")
async def initialize_demo_data():
    """Initialize the database with demo data"""
    try:
        logger.info("Initializing demo data")
        
        # Create users table
        users_sql = "CREATE TABLE users (id INT PRIMARY KEY, email STRING UNIQUE, name STRING, is_active BOOL)"
        tokens = tokenizer.tokenize(users_sql)
        command = parser.parse(tokens)
        executor.execute(command)
        
        # Insert demo users
        demo_users = [
            "INSERT INTO users VALUES (1, 'alice@example.com', 'Alice Johnson', TRUE)",
            "INSERT INTO users VALUES (2, 'bob@example.com', 'Bob Smith', TRUE)",
            "INSERT INTO users VALUES (3, 'carol@example.com', 'Carol Williams', FALSE)",
            "INSERT INTO users VALUES (4, 'david@example.com', 'David Brown', TRUE)",
            "INSERT INTO users VALUES (5, 'eve@example.com', 'Eve Davis', TRUE)"
        ]
        
        for sql in demo_users:
            tokens = tokenizer.tokenize(sql)
            command = parser.parse(tokens)
            executor.execute(command)
        
        # Create orders table
        orders_sql = "CREATE TABLE orders (order_id INT PRIMARY KEY, user_id INT, amount INT, status STRING)"
        tokens = tokenizer.tokenize(orders_sql)
        command = parser.parse(tokens)
        executor.execute(command)
        
        # Insert demo orders
        demo_orders = [
            "INSERT INTO orders VALUES (101, 1, 250, 'completed')",
            "INSERT INTO orders VALUES (102, 1, 150, 'pending')",
            "INSERT INTO orders VALUES (103, 2, 500, 'completed')",
            "INSERT INTO orders VALUES (104, 3, 75, 'cancelled')",
            "INSERT INTO orders VALUES (105, 4, 320, 'completed')",
            "INSERT INTO orders VALUES (106, 2, 180, 'pending')",
            "INSERT INTO orders VALUES (107, 5, 420, 'completed')"
        ]
        
        for sql in demo_orders:
            tokens = tokenizer.tokenize(sql)
            command = parser.parse(tokens)
            executor.execute(command)
        
        logger.info("Demo data initialized successfully")
        
        return {
            "success": True,
            "message": "Demo data initialized successfully",
            "tables_created": ["users", "orders"],
            "users_inserted": 5,
            "orders_inserted": 7
        }
    
    except Exception as e:
        logger.error(f"Failed to initialize demo data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to initialize demo data: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 80)
    logger.info("Custom RDBMS API Server Starting")
    logger.info("=" * 80)
    logger.info(f"Version: 2.0.0")
    logger.info(f"Database initialized with {len(database.tables)} tables")
    logger.info(f"Server start time: {stats['server_start_time']}")
    logger.info("=" * 80)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=" * 80)
    logger.info("Custom RDBMS API Server Shutting Down")
    logger.info(f"Total queries processed: {stats['total_queries']}")
    logger.info(f"Successful queries: {stats['successful_queries']}")
    logger.info(f"Failed queries: {stats['failed_queries']}")
    logger.info("=" * 80)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
