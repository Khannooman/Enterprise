from datetime import datetime
import json
import os
import logging
import traceback
from typing import Optional, Dict, Any, Union, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from app.utils.utility_manager import UtilityManager

class PostgreSQLManager(UtilityManager):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self, 
        host: Optional[str] = None, 
        database: Optional[str] = None, 
        user: Optional[str] = None, 
        password: Optional[str] = None, 
        port: Optional[str] = None,
        schema: Optional[str] = None,
        ssl_mode: Optional[str] = None
    ):
        # Prevent re-initialization
        if hasattr(self, 'initialized') and self.initialized:
            return

        # Use environment variables as fallback
        self.host = host or os.getenv('POSTGRES_DB_HOST')
        self.database = database or os.getenv('POSTGRES_DB_NAME')
        self.user = user or os.getenv('POSTGRES_DB_USER')
        self.password = password or os.getenv('POSTGRES_DB_PASSWORD')
        print(self.password)
        self.port = port or int(os.getenv('POSTGRES_DB_PORT', '5432'))
        self.schema = schema or os.getenv('POSTGRES_DB_SCHEMA')
        self.ssl_mode = ssl_mode or os.getenv('POSTGRES_SSLMODE', 'prefer')
        try:
            # Construct connection URL
            connection_url = URL.create(
                'postgresql+psycopg2',
                username=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
                query={'sslmode': self.ssl_mode}
            )
            self.connection_url = connection_url
            # Log connection details (masking sensitive info)
            logging.info(f"Connecting to PostgreSQL at {self.host}:{self.port}/{self.database}")

            # Create engine
            self.engine = create_engine(connection_url, pool_pre_ping=True)
            
            # Create scoped session
            session_factory = sessionmaker(bind=self.engine)
            self._session = scoped_session(session_factory)

            # Verify connection
            with self.engine.connect() as connection:
                logging.info("Database connection established successfully")

            self.initialized = True

        except Exception as e:
            logging.error(f"Failed to initialize database connection: {e}")
            logging.debug(traceback.format_exc())
            raise

    def get_session(self):
        """Get a database session."""
        return self._session()

    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None, 
        fetch_one: bool = False,
        return_json: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], Any]:
        """
        Execute a SQL query with optional parameters.
        
        Args:
            query: SQL query string
            params: Optional dictionary of query parameters
            fetch_one: If True, fetch single row, otherwise fetch all rows
            return_json: If True, return results as JSON objects
            
        Returns:
            Query results in requested format, or error dictionary if query fails
        """
        try:
            session = self.get_session()
            
            # Ensure all parameters are strings where needed
            if params:
                params = {
                    k: str(v) if isinstance(v, (int, float)) or (
                        isinstance(v, str) and len(v) == 36
                    ) else v 
                    for k, v in params.items()
                }

            logging.debug(f"Executing query: {query}")
            logging.debug(f"Query parameters: {params}")

            # Use text() for safe parameter binding
            result = session.execute(text(query), params or {})

            if query.strip().lower().startswith("select") or "returning" in query.lower():
                # Fetch results for SELECT or RETURNING queries
                if return_json:
                    # Get column names from result
                    columns = result.keys()
                    
                    if fetch_one:
                        row = result.fetchone()
                        data = dict(zip(columns, row)) if row else None
                    else:
                        # Create list of dictionaries for all rows
                        data = [dict(zip(columns, row)) for row in result.fetchall()]
                else:
                    # Original behavior
                    data = result.fetchone() if fetch_one else result.fetchall()
            else:
                data = None  # No result needed for non-SELECT queries

            session.commit()  # Commit the transaction
            return data  # Return fetched data
            
        except SQLAlchemyError as e:
            session.rollback()
            logging.error(f"Database query error: {e}")
            logging.debug(traceback.format_exc())
            return {"error": str(e)}
        
        finally:
            session.close()  # Close session instead of rollback
            
    def create_tables(self):
        """Create required tables if they do not exist."""
        queries = [
                """ 
                CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(50) PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                phone_number VARCHAR(20),
                company_name VARCHAR(100) NOT NULL,
                addressline1 VARCHAR(100) NOT NULL,
                addressline2 VARCHAR(100),
                landmark VARCHAR(100),
                city VARCHAR(50) NOT NULL,
                state VARCHAR(50) NOT NULL,     
                pincode VARCHAR(10) NOT NULL,
                country VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
                """,
                """
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    customer_name VARCHAR(100) NOT NULL,
                    phone_number VARCHAR(20),
                    contact_info VARCHAR(100),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE);
                """,
                """
                CREATE TABLE IF NOT EXISTS products (
                    product_id VARCHAR(50),
                    user_id VARCHAR(50),
                    product VARCHAR(100) NOT NULL,
                    weight VARCHAR(50),
                    batch_number VARCHAR(50),
                    expiry_date DATE,
                    quantity INTEGER NOT NULL CHECK (quantity >= 0),
                    mrp DECIMAL(10, 2) NOT NULL,
                    distributer_loading DECIMAL(10, 2),
                    selling_price DECIMAL(10, 2) NOT NULL,
                    PRIMARY KEY (product_id, user_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
                """,
                """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id VARCHAR(50),
                    product_id VARCHAR(50),
                    user_id VARCHAR(50),
                    customer_id VARCHAR(50),
                    created_by VARCHAR(50),
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    rate DECIMAL(10, 2) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (order_id, user_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id, user_id) REFERENCES products(product_id, user_id) ON DELETE CASCADE,
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
                    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
                );
                """
            ]
        try:
            for query in queries:
                self.execute_query(query=query)
            logging.info("Tables created successfully (if not exist).")
        except Exception as e:
            logging.error(str(e))
        

         