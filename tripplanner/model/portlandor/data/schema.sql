-- Next-generation byCycle schema (using SQLite syntax)
--
-- This is intended to be the blueprint for a more general-purpose SQL-based 
-- GIS schema schema [sic], possibly a replacement for shapefiles. A table 
-- starting with `layer_` is (you guessed it!) a layer. It is a lot like a 
-- combined .shp/.dbf. A significant difference is that the attributes can be 
-- normalized (in the RDMS sense) by using additional tables combined with 
-- layer attributes that start with `ix_` or `id_`. An attribute that starts 
-- with `ix_` points to the sequential index of an attribute in another table.
-- An attribute that starts with `id_` points to a non-sequential unique ID of 
-- an attribute in another table. The table is specifed by naming the attribute
-- with that table name like so: ix_table or id_table.
--
-- Attribute naming conventions: 
--     * ixORid_TableName[_OtherQualifiers]
--     * FieldName[_OtherQualifiers]
-- When the attribute name starts with `ix_` or `id_`, the attribute value will
-- be looked up in the table pointed to by NameOrTableName. When the name 
-- starts with `ix_` the name will be looked up by index; when it ends in `id_`
-- it will be looked up by unique id, where `ix`  and `id` are the names of 
-- columns containing, respectively, the sequential index and unique ID for 
-- each record. The Other Qualifiers part of the attribute name can be anything
-- that is useful for the user's purpose.
--
-- The geometry column will contain a binary geometry representation.

USE portlandor;

CREATE TABLE `layer_street` (
  `id`            INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `node_f_id`     INTEGER UNSIGNED NOT NULL,
  `node_t_id`     INTEGER UNSIGNED NOT NULL,
  `addr_f`        MEDIUMINT UNSIGNED NOT NULL,
  `addr_t`        MEDIUMINT UNSIGNED NOT NULL,
  `even_side`		ENUM('l', 'r') NOT NULL,
  `streetname_id` INTEGER NOT NULL,
  `city_l_id`     INTEGER NOT NULL,
  `city_r_id`     INTEGER NOT NULL,
  `state_l_id`    CHAR(2) NOT NULL,
  `state_r_id`    CHAR(2) NOT NULL,
  `zip_l`         MEDIUMINT NOT NULL,
  `zip_r`         MEDIUMINT NOT NULL,
  `wkt_geometry`  TEXT NOT NULL
);

-- Portland street attributes
CREATE TABLE `attr_street` (
  `id`       INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `localid`  FLOAT(11, 2) NOT NULl,
  `oneway`   ENUM('', 'f', 't', 'n') NOT NULL,
  `code`     SMALLINT NOT NULL,	
  `bikemode` ENUM('', 'p', 'mm', 'b', 'l', 'm', 'h', 'c', 'x') NOT NULL,
  `up_frac`  FLOAT(4, 3) NOT NULL,	
  `abs_slp`  FLOAT(4, 3) NOT NULL,
  `cpd`      INTEGER NOT NULL,
  `sscode`   INTEGER NOT NULL
);

CREATE TABLE `layer_node` (
  `id`           INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
--`geometry`     BLOB NOT NULL,
  `wkt_geometry` TEXT NOT NULL  
);

CREATE TABLE `streetname` (
  `id`     INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `prefix` CHAR(2) NOT NULL,
  `name`   VARCHAR(255) NOT NULL,
  `type`   CHAR(4) NOT NULL,
  `suffix` CHAR(2) NOT NULL
);

CREATE TABLE `city` (
  `id`    INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `city`  VARCHAR(255) NOT NULL
);

CREATE TABLE `state` (
  `id`    CHAR(2) PRIMARY KEY NOT NULL, 
  `state` VARCHAR(255) NOT NULL
);

--CREATE TABLE `matrix` (
-- `id`     INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT NOT NULL,
--  `region`   VARCHAR(255) NOT NULL,
--  `matrix` LONG BLOB NOT NULL
--);

