#! /bin/python

import fnmatch
import os
import nltk
import re

BASE_DIR		= '../dark_horizon/'
SOURCE 			= 'src'
SOURCE_EXT		= 'cpp'
HEADERS 		= 'src'
HEADERS_EXT		= 'h'

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
	print tokens
	
	t = ''
	
	for i in xrange(len(tokens)-2, -1, -1):
		if (tokens[i] != 'const'):
			t = tokens[i]
			break
	
	# Strip out ':' characters if we found the token ':string' (which comes from std::string)
	t = t.replace(':', '')
	
	return t



def parseTokens(tokens, fileMetaData, fileType):
	bindings 	= []
	b 			= None
	cache 		= []
	
	for i, t in enumerate(tokens):
		if (t == '@'):
			if tokens[i+1] == 'table':
				b 			= {}
				b['type'] 	= 'table'
				b['file']	= fileMetaData[fileType]
			elif tokens[i+1] == 'id':
				b 			= {}
				b['type'] 	= 'id'
				b['file']	= fileMetaData[fileType]
			elif tokens[i+1] == 'column':
				b 			= {}
				b['type'] 	= 'column'
				b['file']	= fileMetaData[fileType]
			elif tokens[i+1] == 'serialize':
				b 			= {}
				b['type'] 	= 'serialize'
				b['file']	= fileMetaData[fileType]
			elif tokens[i+1] == 'deserialize':
				b 			= {}
				b['type'] 	= 'deserialize'
				b['file']	= fileMetaData[fileType]
		
		if (b):
			if (t == ';'):
				b['variable'] 		= parseVariableName( cache )
				b['variableType'] 	= parseVariableType( cache )
			
				bindings.append( b )
				print b
			
				b 		= None
				cache 	= []
				
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
					
					bindings.append( b )
					print b
				
					b 		= None
					cache 	= []
					
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
					print b
				
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
					print b
				
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
		
		# Get table name
		print bindings
		table 	= ''
		for b in bindings:
			if (b['type'] == 'table'):
				table = b['table']
		
		# If we have both source and header, print into both
		if (file['source'] and file['header']):
			serializeDefinition 	= '''			// @serialize start
				virtual void serialize(SQLite::Database& db);
				// @serialize end'''
			deserializeDefinition 	= '''			// @deserialize start
				virtual void deserialize(SQLite::Database& db);
				// @deserialize end'''
			
			columns 	= []
			data 		= []
			
			for b in bindings:
				if (b['type'] == 'column'):
					columns.append( b['column'] )
					if (b['variableType'] == 'string' or b['variableType'] == 'char*'):
						data.append( "\"'\" << " + b['variable'] + " << \"'\"" )
					else:
						data.append( b['variable'] )
			
			updateData = []
			for i in range(0, len(columns)):
				t = columns[i] + '=" << ' + data[i]
				updateData.append(t)
				
			updateData	= ' << ", '.join( updateData )
			columns 	= ', '.join( columns )
			data 		= ' << \", " << '.join( data )
			
			serializeImpl 			= '''			// @serialize start
			void {name}::serialize(SQLite::Database& db)
			{{
				std::stringstream ss;
				if (id_ > 0)
				{{
					ss << "UPDATE {table} SET {updateData};
				}}
				else
				{{
					ss << "INSERT INTO {table} ({columns}) VALUES (";
					ss << {data};
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
			}}
			// @serialize end'''
			serializeImpl = serializeImpl.format(name = file['name'], table = table, columns = columns, data = data, updateData = updateData)
			print serializeImpl
			
			
			columns 	= []
			data 		= []
			index 		= 0
			for b in bindings:
				if (b['type'] == 'column'):
					columns.append( b['column'] )
					if (b['variableType'] == 'string'):
						text = '''
							const char* value{index} = query.getColumn({index});
							{variable} = std::string( value{index} );'''
						text = text.format(variable = b['variable'], index = index)
						data.append( text )
					else:
						text = '''
							{variable} = query.getColumn({index});'''
						text = text.format(variable = b['variable'], index = index)
						data.append( text )
					index = index + 1
			
			columns 	= ', '.join( columns )
			data 		= "\n".join( data )
			
			deserializeImpl 		= '''			// @deserialize start
			void {name}::deserialize(SQLite::Database& db)
			{{
				SQLite::Statement query(db, "SELECT {columns} FROM {table} WHERE id = ?");

				query.bind(1, id_);

				while (query.executeStep())
				{{
					{data}
				}}
			}}
			// @deserialize end'''
			deserializeImpl = deserializeImpl.format(name = file['name'], table = table, columns = columns, data = data)
			deserializeImpl
			print deserializeImpl
			
			
			# Insert into file(s)
			injectCodeIntoFile(file['header'], '@serialize', serializeDefinition)
			injectCodeIntoFile(file['header'], '@deserialize', deserializeDefinition)
			injectCodeIntoFile(file['source'], '@serialize', serializeImpl)
			injectCodeIntoFile(file['source'], '@deserialize', deserializeImpl)
			injectCodeIntoFile(file['header'], '@serialize', serializeDefinition)
			injectCodeIntoFile(file['header'], '@serialize', serializeDefinition)				
					



findFiles()
matchFiles()

for val in files:
	bindings = parseFile( files[val] )
	
	validateBindings( bindings )
	
	printMethods( files[val], bindings )
	
