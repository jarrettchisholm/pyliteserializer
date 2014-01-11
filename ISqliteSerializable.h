#ifndef ISQLITESERIALIZABLE_H_
#define ISQLITESERIALIZABLE_H_

#include "sqlitec++/SQLiteC++.h"

namespace pyliteserializer
{

// Forward declaration
class SqliteDataStore;

class ISqliteSerializable {
public:
	virtual ~ISqliteSerializable()
	{
	}
	;
	
	virtual void serialize(SQLite::Database& db, SqliteDataStore& ds) = 0;
	virtual void deserialize(SQLite::Database& db, SqliteDataStore& ds) = 0;
	
	virtual void deserialize(SQLite::Database& db, SqliteDataStore& ds, const std::string& where) = 0;
	virtual void deserialize(SQLite::Statement& query, SqliteDataStore& ds) = 0;
	
	virtual void load(SqliteDataStore& ds) = 0;
	virtual void save(SqliteDataStore& ds) = 0;
};

}

#endif /* ISQLITESERIALIZABLE_H_ */
