#! /bin/python

import fnmatch
import os
import nltk
import re

BASE_DIR		= '../dark_horizon/'
DATASTORE_DIR 	= BASE_DIR + 'src/game/data_store/'
SOURCE 			= 'src'
SOURCE_EXT		= 'cpp'
HEADERS 		= 'src'
HEADERS_EXT		= 'h'

DATASTORE_NAME 	= 'SqliteDataStore'

sourceMatches 	= []
headerMatches 	= []
files 			= {}


def findFiles():
	for root, dirnames, filenames in os.walk( BASE_DIR + SOURCE ):
		for filename in fnmatch.filter(filenames, '*.' + SOURCE_EXT):
			sourceMatches.append( os.path.join(root, filename) )

	for root, dirnames, filenames in os.walk( BASE_DIR + HEADERS ):
		for filename in fnmatch.filter(filenames, '*.' + HEADERS_EXT):
			headerMatches.append( os.path.join(root, filename) )


def matchFiles():
	# Match source files
	for val in sourceMatches:
		f = {}
		
		name 	= val.split('/')
		name 	= name[-1].replace('.' + SOURCE_EXT, '')
		
		header 	= ''
		headers = [s for s in headerMatches if (name + '.' + HEADERS_EXT) in s]
		
		if len(headers) > 0:
			# If more than one match is found, try to narrow it down
			if len(headers) > 1:				
				for h in headers:
					t = h.split('/')
					t = t[-1].replace('.' + HEADERS_EXT, '')
					if (t == name):
						header = h
						break

				#if header == '':
				#	raise Exception("Too many matching headers for source file: " + val)
			else:
				header = headers[0]

		f['name'] 		= name
		f['source'] 	= val
		f['header'] 	= header
		
		files[name] = f
	
	
	# Match header files
	for val in headerMatches:
		f = {}
		
		name 	= val.split('/')
		name 	= name[-1].replace('.' + HEADERS_EXT, '')
		
		# If we have already parsed this file pair, continue
		if (files.get(name)):
			continue
		
		source 	= ''
		sources = [s for s in sourceMatches if (name + '.' + SOURCE_EXT) in s]
		
		if len(sources) > 0:
			# If more than one match is found, try to narrow it down
			if len(sources) > 1:				
				for h in sources:
					t = h.split('/')
					t = t[-1].replace('.' + SOURCE_EXT, '')
					if (t == name):
						source = h
						break

				#if source == '':
				#	raise Exception("Too many matching sources for source file: " + val)
			else:
				source = sources[0]

		f['name'] 		= name
		f['source'] 	= source
		f['header'] 	= val
		
		files[name] = f



def parseVariableName(tokens):
	return tokens[-1]
	#v = ''
	#
	#for x in reversed(tokens):
	#	if (x != ''):
	#		v += x
	#
	#return v



def parseVariableType(tokens):
	#print tokens
	
	t = ''
	
	for i in xrange(len(tokens)-2, -1, -1):
		if (tokens[i] != 'const'):
			t = tokens[i]
			break
	
	# Strip out ':' characters if we found the token ':string' (which comes from std::string)
	t = t.replace(':', '')
	
	return t



def parseTokens(tokens, fileMetaData, fileType):
	bindings 			= []
	b 					= None
	cache 				= []
	
	for i, t in enumerate(tokens):
		if (t == '@'):
			
			### Primary tags
			if tokens[i+1] == 'table':
				if (b):
					bindings.append( b )
					#print b
					b 		= {}
					cache 	= []
				else:
					b 		= {}
				b['type'] 	= 'table'
				b['file']	= fileMetaData[fileType]
				
			elif tokens[i+1] == 'column':
				if (b):
					bindings.append( b )
					#print b
					b 		= {}
					cache 	= []
				else:
					b 		= {}
				b['type'] 	= 'column'
				b['file']	= fileMetaData[fileType]
			
			elif tokens[i+1] == 'include':
				if (b):
					bindings.append( b )
					#print b
					b 		= {}
					cache 	= []
				else:
					b 		= {}
				b['type'] 	= 'include'
				b['file']	= fileMetaData[fileType]
				
			elif tokens[i+1] == 'serialize':
				if (not b):
					b 		= {}
				b['type'] 	= 'serialize'
				b['file']	= fileMetaData[fileType]
				
			elif tokens[i+1] == 'deserialize':
				if (not b):
					b 		= {}
				b['type'] 	= 'deserialize'
				b['file']	= fileMetaData[fileType]
			
			elif tokens[i+1] == 'deserialize_where':
				if (not b):
					b 		= {}
				b['type'] 	= 'deserialize_where'
				b['file']	= fileMetaData[fileType]
			
			elif tokens[i+1] == 'deserialize_from_query':
				if (not b):
					b 		= {}
				b['type'] 	= 'deserialize_from_query'
				b['file']	= fileMetaData[fileType]
				
			### Metadata tags
			elif tokens[i+1] == 'id':
				if (not b):
					b 		= {}
				b['id'] 	= True
				
			elif tokens[i+1] == 'namespace':
				if (not b):
					b 			= {}
				b['namespace'] 	= ''
		
		if (b):
			if (t == ';'):
				b['variable'] 		= parseVariableName( cache )
				b['variableType'] 	= parseVariableType( cache )
			
				bindings.append( b )
				#print b
			
				b 		= None
				cache 	= []
			
			elif (b.get('namespace') is not None):
				if (t == '@' or t == 'namespace' or t == '{'):
					# Eat
					pass
				elif (t == '}'):
					bindings.append( b )
					#print b
				
					b 		= None
					cache 	= []
				else:
					b['namespace'] += t
			
			elif (b['type'] == 'column' and not b.get('column')):
				if (t == '@' or t == 'column'):
					# Eat
					pass
				else:
					b['column'] = t
			
			elif (b['type'] == 'table' and not b.get('table')):
				if (t == '@' or t == 'table'):
					# Eat
					pass
				else:
					b['table'] 	= t
			
			elif (b['type'] == 'include' and not b.get('include')):
				if (t == '@' or t == 'include'):
					# Eat
					pass
				else:
					b['include'] = t
					
			elif (b['type'] == 'serialize' and not b.get('start') and not b.get('end')):
				if (t == '@' or t == 'serialize'):
					# Eat
					pass
				else:
					if (t == 'start'):
						b['start'] 	= True
					elif (t == 'end'):
						b['end'] 	= True
					else:
						raise Exception("Invalid @serialize annotation in file: " + b['file'])
					
					bindings.append( b )
					#print b
				
					b 		= None
					cache 	= []
				
			elif (b['type'] == 'deserialize' and not b.get('start') and not b.get('end')):
				if (t == '@' or t == 'deserialize'):
					# Eat
					pass
				else:
					if (t == 'start'):
						b['start'] 	= True
					elif (t == 'end'):
						b['end'] 	= True
					else:
						raise Exception("Invalid @deserialize annotation in file: " + b['file'])
					
					bindings.append( b )
					#print b
				
					b 		= None
					cache 	= []
			
			elif (b['type'] == 'deserialize_where' and not b.get('start') and not b.get('end')):
				if (t == '@' or t == 'deserialize_where'):
					# Eat
					pass
				else:
					if (t == 'start'):
						b['start'] 	= True
					elif (t == 'end'):
						b['end'] 	= True
					else:
						raise Exception("Invalid @deserialize_where annotation in file: " + b['file'])
					
					bindings.append( b )
					#print b
				
					b 		= None
					cache 	= []
			
			elif (b['type'] == 'deserialize_from_query' and not b.get('start') and not b.get('end')):
				if (t == '@' or t == 'deserialize_from_query'):
					# Eat
					pass
				else:
					if (t == 'start'):
						b['start'] 	= True
					elif (t == 'end'):
						b['end'] 	= True
					else:
						raise Exception("Invalid @deserialize_from_query annotation in file: " + b['file'])
					
					bindings.append( b )
					#print b
				
					b 		= None
					cache 	= []
				
			else:
				# Add to cache, which we use to get the variable name
				cache.append(t)
	
	return bindings


def parseFile(file):
	#print file
	
	bindings 	= []
	
	
	# Load header file
	tokens 		= []
	if (file['header'] != ''):
		with open(file['header'], 'rw') as f:
			# Tokenize
			for line in f.readlines():
				tokens += nltk.word_tokenize(line)
	
	# Parse tokens
	bindings += parseTokens( tokens, file, 'header' )

	
	# Load source file
	tokens 		= []
	if (file['source'] != ''):
		with open(file['source'], 'rw') as f:
			# Tokenize
			for line in f.readlines():
				tokens += nltk.word_tokenize(line)
	
	# Parse tokens
	bindings += parseTokens( tokens, file, 'source' )	
	
	return bindings



def getQueryString( bindings, variableName ):
	""" Columns a bunch of data about the bindings.  Will return properly formatted strings for
		updating, inserting, and querying the SQLite table specified in the bindings dictionary.  Will also
		return the table name and a string that lists the columns (properly formatted for use in an SQLite
		query).
		variableName is the name to use for the SQLiteC++ Statement variable in the generated methods.
	"""
	table 		= ''
	columns 	= []
	queryData 	= []
	insertData 	= []
	updateData 	= []
	index 		= 0
	
	for b in bindings:
		# Process table
		if (b['type'] == 'table'):
			table = b['table']
			
		# Process column
		elif (b['type'] == 'column'):
			columns.append( b['column'] )
			
			# Process query data
			if (b['variableType'] == 'string'):
				text = '''
const char* value{index} = {query}.getColumn({index});
{variable} = std::string( value{index} );'''
				text = text.format(variable = b['variable'], index = index, query = variableName)
				queryData.append( text )
			else:
				text = '''
{variable} = {query}.getColumn({index});'''
				text = text.format(variable = b['variable'], index = index, query = variableName)
				queryData.append( text )
			index = index + 1
			
			# Process insert data
			if (b['variableType'] == 'string' or b['variableType'] == 'char*'):
				insertData.append( "\"'\" << " + b['variable'] + " << \"'\"" )
			else:
				insertData.append( b['variable'] )
	
	# Process update data
	for i in range(0, len(columns)):
		t = columns[i] + '=" << ' + insertData[i]
		updateData.append(t)
		
	columns 	= ', '.join( columns )
	updateData	= ' << ", '.join( updateData )
	insertData 	= ' << \", " << '.join( insertData )
	queryData	= '\n'.join( queryData )
	
	return {'table': table, 'updateData':  updateData, 'columns':  columns, 'insertData':  insertData, 'queryData':  queryData}



def validateBindings( bindings ):
	# Validate bindings
	pass



def injectCodeIntoFile(fileName, tag, replaceWith):
	contents = ''
	with open(fileName, 'r') as f:
		contents = f.read()
	
	regex = '.*{tag} start(.|\s)*?{tag} end.*'.format(tag = tag)
	contents = re.sub(re.compile(regex), replaceWith, contents)
	
	with open(fileName, 'w') as f:
		f.write( contents )
	

def printMethods( file, bindings ):
	if (len(bindings) == 0):
		# print 'No bindings present for file: ' + file['name']
		pass
	else:
		print 'Writing bindings for file(s): '
		if (file['source']):
			print file['source']
		if (file['header']):
			print file['header']
		print ''
		
		#print bindings
		
		# Get query, column and table data		
		data = getQueryString( bindings, 'query' )
		table 		= data['table']
		updateData 	= data['updateData']
		insertData 	= data['insertData']
		queryData 	= data['queryData']
		columns 	= data['columns']
		
		# If we have both source and header, print into both
		if (file['source'] and file['header']):
			serializeDefinition 				= '''	// @serialize start
	virtual void serialize(SQLite::Database& db, pyliteserializer::SqliteDataStore& ds);
	// @serialize end'''
			deserializeDefinition 				= '''	// @deserialize start
	virtual void deserialize(SQLite::Database& db, pyliteserializer::SqliteDataStore& ds);
	// @deserialize end'''
			deserializeWhereDefinition 			= '''	// @deserialize_where start
	virtual void deserialize(SQLite::Database& db, pyliteserializer::SqliteDataStore& ds, const std::string& where);
	// @deserialize_where end'''
			deserializeFromQueryDefinition 		= '''	// @deserialize_from_query start
	virtual void deserialize(SQLite::Statement& query, pyliteserializer::SqliteDataStore& ds);
	// @deserialize_from_query end'''


			
			serializeImpl 			= '''// @serialize start
void {name}::serialize(SQLite::Database& db, pyliteserializer::SqliteDataStore& ds)
{{
	std::stringstream ss;
	if (id_ > 0)
	{{
		ss << "UPDATE {table} SET {updateData};
	}}
	else
	{{
		ss << "INSERT INTO {table} ({columns}) VALUES (";
		ss << {insertData};
		ss << ")";
	}}
	if (id_ > 0)
	{{
		ss << " WHERE id = " << id_;
	}}
	
	try
	{{
		db.exec( ss.str().c_str() );
	}}
	catch (std::exception& e)
	{{
		std::cout << "SQLite Exception: " << e.what() << std::endl;
		std::cout << "Query: " << ss.str() << std::endl;
	}}
	
	save(ds);
}}
// @serialize end'''
			serializeImpl = serializeImpl.format(name = file['name'], table = table, columns = columns, insertData = insertData, updateData = updateData)
			#print serializeImpl
			
			
			
			deserializeWhereImpl 		= '''// @deserialize_where start
void {name}::deserialize(SQLite::Database& db, pyliteserializer::SqliteDataStore& ds, const std::string& where)
{{
	std::stringstream ss;
	
	if (where.length() > 0)
		ss << "SELECT {columns} FROM {table} WHERE " << where;
	else
		ss << "SELECT {columns} FROM {table} WHERE id = ?";

	SQLite::Statement query(db,  ss.str().c_str());

	query.bind(1, id_);

	while (query.executeStep())
	{{
		{queryData}
	}}
	
	load(ds);
}}
// @deserialize_where end'''
			deserializeWhereImpl = deserializeWhereImpl.format(name = file['name'], table = table, columns = columns, queryData = queryData)
			deserializeWhereImpl
			#print deserializeWhereImpl
			
			
			
			deserializeFromQueryImpl 		= '''// @deserialize_from_query start
void {name}::deserialize(SQLite::Statement& query, pyliteserializer::SqliteDataStore& ds)
{{
	{queryData}
	
	load(ds);
}}
// @deserialize_from_query end'''
			deserializeFromQueryImpl = deserializeFromQueryImpl.format(name = file['name'], queryData = queryData)
			deserializeFromQueryImpl
			#print deserializeFromQueryImpl
			
			
			
			deserializeImpl 		= '''// @deserialize start
void {name}::deserialize(SQLite::Database& db, pyliteserializer::SqliteDataStore& ds)
{{
	SQLite::Statement query(db, "SELECT {columns} FROM {table} WHERE id = ?");

	query.bind(1, id_);

	while (query.executeStep())
	{{
		{queryData}
	}}
	
	load(ds);
}}
// @deserialize end'''
			deserializeImpl = deserializeImpl.format(name = file['name'], table = table, columns = columns, queryData = queryData)
			deserializeImpl
			#print deserializeImpl
			
			
			# Insert into file(s)
			injectCodeIntoFile(file['header'], '@serialize', serializeDefinition)
			injectCodeIntoFile(file['source'], '@serialize', serializeImpl)
			
			injectCodeIntoFile(file['header'], '@deserialize', deserializeDefinition)
			injectCodeIntoFile(file['source'], '@deserialize', deserializeImpl)
			
			injectCodeIntoFile(file['header'], '@deserialize_where', deserializeWhereDefinition)
			injectCodeIntoFile(file['source'], '@deserialize_where', deserializeWhereImpl)
			
			injectCodeIntoFile(file['header'], '@deserialize_from_query', deserializeFromQueryDefinition)
			injectCodeIntoFile(file['source'], '@deserialize_from_query', deserializeFromQueryImpl)
			
					



def printSqliteDataStore( classBindings ):
	headerContents 	= ''
	classContents 	= ''
	includeList 	= []
	
	# Default header classes
	definition = '''
	// Default methods
	void load(ISqliteSerializable& object);
	void load(ISqliteSerializable& object, const std::string& where);
	void load(std::vector<ISqliteSerializable>& objects);
	void load(std::vector<ISqliteSerializable>& objects, const std::string& where);
	
	void save(ISqliteSerializable& object);
	void save(std::vector<ISqliteSerializable>& objects);
'''
	
	headerContents += definition

	
	
	# Generate header string
	for b in classBindings:
		name 		= b['name']
		include 	= False
		includeFile = None
		namespace 	= ''
		
		# Find the namespace (if it was specified)
		for binding in b['bindings']:
			if (binding['type'] == 'table'):
				# Only include this class if a table was defined for it
				include = True
				if (binding.get('namespace')):
					namespace = binding['namespace'] + '::'
			if (binding['type'] == 'include'):
				includeFile = binding['include']

		if (include):
			if (includeFile):
				includeList.append( includeFile )
			
			definition = '''
	// {className} class
	void load({namespace}{className}& object);
	void load({namespace}{className}& object, const std::string& where);
	void load(std::vector<{namespace}{className}>& objects);
	void load(std::vector<{namespace}{className}>& objects, const std::string& where);
	void loadBulk(std::vector<{namespace}{className}>& objects, const std::string& where);
	
	void save({namespace}{className}& object);
	void save(std::vector<{namespace}{className}>& objects);
'''
			definition = definition.format(className = name, namespace = namespace)
			
			headerContents += definition
	
	headerStart = '''#ifndef DATASTORE_H_
#define DATASTORE_H_

#include <string>
#include <memory>
#include <vector>

#include "ISqliteSerializable.h"

'''
	
	# Insert custom includes for classes here
	for i in includeList:
		headerStart += '#include "' + i + '"\n'
	
	headerStart += '''
namespace pyliteserializer
{

class SqliteDataStore
{
public:
	SqliteDataStore(const std::string& file);
	virtual ~SqliteDataStore();
	'''
	
	headerContents = headerStart + headerContents
	
	headerContents += '''
	
private:
	std::unique_ptr<SQLite::Database> db_;
};

}

#endif /* DATASTORE_H_ */
	'''
	
	
	# Default class methods
	implementation = '''	
void SqliteDataStore::load(ISqliteSerializable& object)
{
	object.deserialize( *(db_.get()), *this );
}

void SqliteDataStore::load(ISqliteSerializable& object, const std::string& where)
{
	object.deserialize( *(db_.get()), *this, where );
}

void SqliteDataStore::load(std::vector<ISqliteSerializable>& objects)
{
	for ( auto& obj : objects )
	{
		obj.deserialize( *(db_.get()), *this );
	}
}

void SqliteDataStore::load(std::vector<ISqliteSerializable>& objects, const std::string& where)
{
	for ( auto& obj : objects )
	{
		obj.deserialize( *(db_.get()), *this, where );
	}
}

void SqliteDataStore::save(ISqliteSerializable& object)
{
	object.serialize( *(db_.get()), *this );
}

void SqliteDataStore::save(std::vector<ISqliteSerializable>& objects)
{
	for ( auto& obj : objects )
	{
		obj.serialize( *(db_.get()), *this );
	}
}
'''

	classContents += implementation
	
	# Generate class string
	for b in classBindings:
		name 		= b['name']
		include 	= False
		namespace 	= ''
		
		# Find the namespace (if it was specified)
		for binding in b['bindings']:
			if (binding['type'] == 'table'):
				# Only include this class if a table was defined for it
				include = True
				if (binding.get('namespace')):
					namespace = binding['namespace'] + '::'
				break
		
		if (include):
			# Get query, column and table data		
			data = getQueryString( b['bindings'], 'query' )
			table 		= data['table']
			updateData 	= data['updateData']
			insertData 	= data['insertData']
			queryData 	= data['queryData']
			columns 	= data['columns']
			
			implementation = '''
// {className} class					
void SqliteDataStore::load({namespace}{className}& object)
{{
	object.deserialize( *(db_.get()), *this );
}}

void SqliteDataStore::load({namespace}{className}& object, const std::string& where)
{{
	object.deserialize( *(db_.get()), *this, where );
}}

void SqliteDataStore::load(std::vector<{namespace}{className}>& objects)
{{
	for ( auto& obj : objects )
	{{
		obj.deserialize( *(db_.get()), *this );
	}}
}}

void SqliteDataStore::load(std::vector<{namespace}{className}>& objects, const std::string& where)
{{
	for ( auto& obj : objects )
	{{
		obj.deserialize( *(db_.get()), *this, where );
	}}
}}

void SqliteDataStore::loadBulk(std::vector<{namespace}{className}>& objects, const std::string& where)
{{
	std::stringstream ss;
	
	// Get number of rows that will be returned
	if (where.length() > 0)
		ss << "SELECT COUNT(*) FROM {table} WHERE " << where;
	else
		ss << "SELECT COUNT(*) FROM {table}";
	
	int numRows = db_->execAndGet( ss.str().c_str() ).getInt();
	
	objects.resize( numRows );
	
	
	
	ss.str(std::string());
	ss.clear();

	// Do actual query here
	if (where.length() > 0)
		ss << "SELECT {columns} FROM {table} WHERE " << where;
	else
		ss << "SELECT {columns} FROM {table}";	
	
	SQLite::Statement query(*(db_.get()), ss.str().c_str());

	int index = 0;
    while (query.executeStep())
    {{
		objects[index].deserialize( query, *this );
		index++;
    }}
}}

void SqliteDataStore::save({namespace}{className}& object)
{{
	object.serialize( *(db_.get()), *this );
}}

void SqliteDataStore::save(std::vector<{namespace}{className}>& objects)
{{
	for ( auto& obj : objects )
	{{
		obj.serialize( *(db_.get()), *this );
	}}
}}
			'''
			implementation = implementation.format(className = name, namespace = namespace, table = table, columns = columns)
			
			classContents += implementation
	
	classContents = '''#include <iostream>

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
	''' + classContents
	
	classContents += '''
}
	'''
	
	
	print 'Writing SqliteDataStore class'
	
	# Print class
	with open(DATASTORE_DIR + DATASTORE_NAME + '.h', 'w') as f:
		f.write( headerContents )
	with open(DATASTORE_DIR + DATASTORE_NAME + '.cpp', 'w') as f:
		f.write( classContents )



findFiles()
matchFiles()

dataStoreBindings = []

for val in files:
	bindings = parseFile( files[val] )
	
	validateBindings( bindings )
	
	printMethods( files[val], bindings )
	
	data = {}
	data['name'] 		= val
	data['file'] 		= file
	data['bindings'] 	= bindings
	
	dataStoreBindings.append( data )

printSqliteDataStore( dataStoreBindings )
	
