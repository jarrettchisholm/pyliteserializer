#include "SqliteDataStore.h"

namespace pyliteserializer
{

SqliteDataStore::SqliteDataStore(const std::string& file)
{
	try
	{
		db_ = std::unique_ptr<SQLite::Database>( new SQLite::Database(file.c_str(), SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE) );
	}
	catch (std::exception& e)
	{
		std::cout << "exception: " << e.what();
	}
}

SqliteDataStore::~SqliteDataStore()
{
}
	
void SqliteDataStore::load(ISqliteSerializable& object)
{
	object.deserialize( *(db_.get()) );
}

void SqliteDataStore::load(ISqliteSerializable& object, const std::string& where)
{
	object.deserialize( *(db_.get()), where );
}

void SqliteDataStore::load(std::vector<ISqliteSerializable>& objects)
{
	for ( auto& obj : objects )
	{
		obj.deserialize( *(db_.get()) );
	}
}

void SqliteDataStore::load(std::vector<ISqliteSerializable>& objects, const std::string& where)
{
	for ( auto& obj : objects )
	{
		obj.deserialize( *(db_.get()), where );
	}
}

void SqliteDataStore::save(ISqliteSerializable& object)
{
	object.serialize( *(db_.get()) );
}

void SqliteDataStore::save(std::vector<ISqliteSerializable>& objects)
{
	for ( auto& obj : objects )
	{
		obj.serialize( *(db_.get()), where );
	}
}

}
