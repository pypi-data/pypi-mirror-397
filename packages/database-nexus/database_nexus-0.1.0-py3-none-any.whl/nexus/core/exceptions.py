#𝖇𝖞 𝖊𝖑𝖎7𝖊𝖎𝖓 - 𝕰7

class DatabaseError(Exception):
    pass

class ValidationError(Exception):
    pass

class MigrationError(Exception):
    pass

class ConnectionError(DatabaseError):
    pass

class QueryError(DatabaseError):
    pass

class ModelError(DatabaseError):
    pass