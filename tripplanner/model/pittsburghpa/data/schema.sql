-- Next-generation byCycle schema (using SQLite syntax)
--
-- This is intended to be the blueprint for a more general-purpose SQL-based 
-- GIS schema schema [sic], possibly a replacement for shapefiles. A table 
-- starting with "layer_" is (you guessed it!) a layer. It is a lot like a 
-- combined .shp/.dbf. A significant difference is that the attributes can be 
-- normalized (in the RDMS sense) by using additional tables combined with 
-- layer attributes that start with "ix_" or "id_". An attribute that starts 
-- with "ix_" points to the sequential index of an attribute in another table.
-- An attribute that starts with "id_" points to a non-sequential unique ID of 
-- an attribute in another table. The table is specifed by naming the attribute
-- with that table name like so: ix_table or id_table.
--
-- Attribute naming conventions: 
--     * ixORid_TableName[_OtherQualifiers]
--     * FieldName[_OtherQualifiers]
-- When the attribute name starts with "ix_" or "id_", the attribute value will
-- be looked up in the table pointed to by NameOrTableName. When the name 
-- starts with "ix_" the name will be looked up by index; when it ends in "id_"
-- it will be looked up by unique id, where "ix"  and "id" are the names of 
-- columns containing, respectively, the sequential index and unique ID for 
-- each record. The Other Qualifiers part of the attribute name can be anything
-- that is useful for the user's purpose.
--
-- The geometry column will contain a binary geometry representation.
--"geometry"      BLOB

-- Pitts?? street attributes
--  "cfcc"         TEXT,
--from Mil
--
--  "id"           INTEGER PRIMARY KEY,
--  "oneway"       INTEGER,
--  "cfcc"         TEXT,	
--  "bikemode"     TEXT,
--  "lanes"        INTEGER,	
--  "adt"          INTEGER,
--  "spd"          INTEGER

--??from portland??
 -- "bikemode"     TEXT,
 -- "up_frac"      REAL,	
 -- "abs_slp"      REAL,
 -- "cpd"          INTEGER
--
 -- "code"         INTEGER


CREATE TABLE "layer_street" (
  "id"            INTEGER PRIMARY KEY,
  "node_f_id"     INTEGER,
  "node_t_id"     INTEGER,
  "addr_f"        INTEGER,
  "addr_t"        INTEGER,
  "streetname_id" INTEGER,
  "city_l_id"     INTEGER,
  "city_r_id"     INTEGER,
  "state_l_id"    TEXT,
  "state_r_id"    TEXT,
  "zip_l"         INTEGER,
  "zip_r"         INTEGER,
  "wkt_geometry"  TEXT
);


CREATE TABLE "attr_street" (
  "id"           INTEGER PRIMARY KEY,
  "oneway"       INTEGER,
  "cfcc"         TEXT	
);

CREATE TABLE "layer_node" (
  "id"           INTEGER  PRIMARY KEY,
  "wkt_geometry" TEXT   
);

CREATE TABLE "streetname" (
  "id"     INTEGER PRIMARY KEY,
  "prefix" TEXT,
  "name"   TEXT,
  "type"   TEXT,
  "suffix" TEXT,
  UNIQUE ("prefix","name","type","suffix")
);

CREATE TABLE "city" (
  "id"    INTEGER PRIMARY KEY,
  "city"  TEXT UNIQUE
);

CREATE TABLE "state" (
  "id"    TEXT PRIMARY KEY, -- Two-letter state code
  "state" TEXT UNIQUE
);

--CREATE TABLE "matrix" (
--  "id"     INTEGER PRIMARY KEY AUTOINCREMENT,
--  "name"   TEXT UNIQUE,
--  "matrix" BLOB
--);

