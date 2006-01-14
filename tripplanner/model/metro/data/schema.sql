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

--LOCALID: Real (9.2)
--FNODE: Real (11.0)
--TNODE: Real (11.0)

--LEFTADD1: Integer (6.0) ADDR_FL
--LEFTADD2: Integer (6.0) ADDR_TL
--RGTADD1: Integer (6.0)  ADDR_FR
--RGTADD2: Integer (6.0)  ADDR_TR

--FDPRE: String (2.0)
--FNAME: String (30.0)
--FTYPE: String (4.0)
--FDSUF: String (2.0)

--LCITY: String (4.0)
--RCITY: String (4.0)

--ZIPCOLEF: Integer (5.0)
--ZIPCORGT: Integer (5.0)

--TYPE: Integer (6.0)
--BIKEMODE: String (2.0)
--UP_FRAC: Real (6.4)
--ABS_SLP: Real (6.4)
--ONE_WAY: String (2.0)


-- Street attributes I assume all streets will have
CREATE TABLE "layer_street" (
  "ix"            INTEGER PRIMARY KEY AUTOINCREMENT,
--"geometry"      BLOB    NOT NULL,
  "wkt_geometry"  TEXT    NOT NULL,
  "id_node_f"     INTEGER NOT NULL,
  "id_node_t"     INTEGER NOT NULL,
  "addr_f"        INTEGER NOT NULL,
  "addr_t"        INTEGER NOT NULL,
  "ix_streetname" INTEGER NOT NULL,
  "ix_city_l"     INTEGER NOT NULL,
  "ix_city_r"     INTEGER NOT NULL,
  "id_state_l"    TEXT    NOT NULL,
  "id_state_r"    TEXT    NOT NULL,
  "zip_l"         INTEGER NOT NULL,
  "zip_r"         INTEGER NOT NULL
);

-- Portland street attributes
CREATE TABLE "attr_street" (
  "ix"           INTEGER PRIMARY KEY AUTOINCREMENT,
  "id"           INTEGER NOT NULL,  -- LOCALID
  "oneway"       INTEGER NOT NULL,
  "code"         INTEGER NOT NULL,	
  "up_frac"      INTEGER NOT NULL,	
  "abs_slp"      INTEGER NOT NULL,	
  "bikemode"     TEXT    NOT NULL
);

CREATE TABLE "layer_node" (
  "ix"           INTEGER PRIMARY KEY AUTOINCREMENT,
  "id"           INTEGER NOT NULL, -- TZID
--"geometry"     BLOB    NOT NULL,
  "wkt_geometry" TEXT    NOT NULL
);

CREATE TABLE "streetname" (
  "ix"     INTEGER PRIMARY KEY AUTOINCREMENT,
  "prefix" TEXT NOT NULL,
  "name"   TEXT NOT NULL,
  "type"   TEXT NOT NULL,
  "suffix" TEXT NOT NULL,
  UNIQUE ("prefix","name","type","suffix")
);

CREATE TABLE "city" (
  "ix"    INTEGER PRIMARY KEY AUTOINCREMENT,
  "city"  TEXT UNIQUE NOT NULL
);

CREATE TABLE "state" (
  "ix"    INTEGER PRIMARY KEY AUTOINCREMENT,
  "id"    TEXT UNIQUE NOT NULL, -- Two-letter state code
  "state" TEXT UNIQUE NOT NULL
);

CREATE TABLE "matrix" (
  "ix"     INTEGER PRIMARY KEY AUTOINCREMENT,
  "name"   TEXT UNIQUE NOT NULL,
  "matrix" BLOB NOT NULL
);

