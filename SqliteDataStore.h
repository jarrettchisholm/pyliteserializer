#ifndef DATASTORE_H_
#define DATASTORE_H_

#include <string>
#include <memory>
#include <vector>

#include "ISqliteSerializable.h"

namespace pyliteserializer
{

class SqliteDataStore
{
public:
	SqliteDataStore(const std::string& file);
	virtual ~SqliteDataStore();
	
	void load(ISqliteSerializable& object);
	void load(ISqliteSerializable& object, const std::string& where);
	void load(std::vector<ISqliteSerializable>& objects);
	void load(std::vector<ISqliteSerializable>& objects, const std::string& where);
	
	void save(ISqliteSerializable& object);
	void save(std::vector<ISqliteSerializable>& objects);
	

private:
	std::unique_ptr<SQLite::Database> db_;
};

}

#endif /* DATASTORE_H_ */
