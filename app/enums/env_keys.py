from enum import Enum

class EnvKeys(Enum):
    APP_HOST='APP_HOST'
    APP_PORT='APP_PORT'
    APP_ENVIRONMENT = "APP_ENVIRONMENT"
    # Logging settings
    APP_LOG_LEVEL='APP_LOG_LEVEL'
    APP_LOG_FILE='APP_LOG_FILE'
    APP_LOGGING_LEVEL='APP_LOGGING_LEVEL'
    APP_LOGGING_HANDLER_NAME='APP_LOGGING_HANDLER_NAME'
    APP_LOGGING_FOLDER='APP_LOGGING_FOLDER'
    APP_LOGGING_FORMATTER='APP_LOGGING_FORMATTER'
    APP_LOGGING_DATEFORMAT='APP_LOGGING_DATEFORMAT'
    APP_LOGGING_MAXBYTES='APP_LOGGING_MAXBYTES'
    APP_LOGGING_BACKUPCOUNT='APP_LOGGING_BACKUPCOUNT'
    APP_USER_AGENT='APP_USER_AGENT'
    # FOLDERS
    UPLOAD_DIR = 'UPLOAD_DIR'
    UPLOAD_ALLOWED_EXTENTIONS = 'UPLOAD_ALLOWED_EXTENTIONS'
    SQLITE_DB_PATH='SQLITE_DB_PATH'
    # LLM
    OPENAI_KEY = 'OPENAI_KEY'
    OPENAI_MODEL = 'OPENAI_MODEL'
    OPENAI_VERBOSE='OPENAI_VERBOSE'
    OPENAI_TEMPERATURE = 'OPENAI_TEMPERATURE'
    #POSTGRES
    POSTGRES_DB_HOST='POSTGRES_DB_HOST'
    POSTGRES_DB_NAME='POSTGRES_DB_NAME'
    POSTGRES_DB_USER='POSTGRES_DB_USER'
    POSTGRES_DB_PASSWORD='POSTGRES_DB_PASSWORD'
    POSTGRES_DB_PORT='POSTGRES_DB_PORT'
    POSTGRES_DB_SCHEMA='POSTGRES_DB_NAME'
    POSTGRES_SSLMODE="POSTGRES_SSLMODE"
    # Authentication
    SECRET_KEY='SECRET_KEY'
    ALGORITHM='ALGORITHM'
    ACCESS_TOKEN_EXPIRE_MINUTES='ACCESS_TOKEN_EXPIRE_MINUTES'
  