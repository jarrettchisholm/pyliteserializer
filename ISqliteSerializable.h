#ifndef ISQLITESERIALIZABLE_H_
#define ISQLITESERIALIZABLE_H_

#include "sqlitec++/SQLiteC++.h"

namespace pyliteserializer
{

class ISqliteSerializable {
public:
	virtual ~ISqliteSerializable()
	{
	}
	;
	
	virtual void serialize(SQLite::Database& db) = 0;
	virtual void deserialize(SQLite::Database& db) = 0;
	
	virtual void deserialize(SQLite::Database& db, const std::string& where) = 0;
};

}

#endif /* ISQLITESERIALIZABLE_H_ */
