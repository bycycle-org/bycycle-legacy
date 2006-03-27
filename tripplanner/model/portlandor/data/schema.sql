-- Next-generation byCycle schema (using SQLite syntax)
--
-- This is intended to be the blueprint for a more general-purpose SQL-based 
-- GIS schema schema [sic], possibly a replacement for shapefiles. A table 
-- starting with "layer_" is (you guessed it!) a layer. It is a lot like a 
-- combined .shp/.dbf. A significant difference is that the attributes can be 
-- normalized (in the RDMS sense) by using additional tables combined with 
-- layer attributes that end with "_id" (i.e., foreign keys).
--
-- Attribute naming conventions: 
--     * TableName[_OtherQualifiers]_id
--     * FieldName[_OtherQualifiers]
-- When the attribute name ends with "_id", the attribute value will
-- be looked up in the table pointed to by TableName. The Other Qualifiers part
-- of the attribute name can be anything that is useful for the user's purpose.
--
-- The geometry column will contain a binary geometry representation.

USE portlandor;

CREATE TABLE `layer_street` (
  `id`            INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `geom`          GEOMETRY NOT NULL,
  -- Attributes all regions should have
  `node_f_id`     INTEGER UNSIGNED NOT NULL,
  `node_t_id`     INTEGER UNSIGNED NOT NULL,
  `addr_f`        MEDIUMINT UNSIGNED NOT NULL,
  `addr_t`        MEDIUMINT UNSIGNED NOT NULL,
  `even_side`     ENUM('l', 'r') NOT NULL,
  `streetname_id` INTEGER NOT NULL,
  `city_l_id`     INTEGER NOT NULL,
  `city_r_id`     INTEGER NOT NULL,
  `state_l_id`    CHAR(2) NOT NULL,
  `state_r_id`    CHAR(2) NOT NULL,
  `zip_l`         MEDIUMINT(5) NOT NULL,
  `zip_r`         MEDIUMINT(5) NOT NULL,
  -- Region-specific attributes
  `localid`       FLOAT(11, 2) NOT NULl,
  `one_way`       ENUM('', 'f', 't', 'n') NOT NULL,
  `code`          SMALLINT NOT NULL,	
  `bikemode`      ENUM('', 'p', 'mm', 'b', 'l', 'm', 'h', 'c', 'x') NOT NULL,
  `up_frac`       FLOAT(4, 3) NOT NULL,	
  `abs_slp`       FLOAT(4, 3) NOT NULL,
  `cpd`           INTEGER NOT NULL,
  `sscode`        INTEGER NOT NULL,
  SPATIAL INDEX (`geom`),
  INDEX (`addr_f`),
  INDEX (`addr_t`),
  INDEX (`node_f_id`),
  INDEX (`node_t_id`),
  INDEX (`streetname_id`)
);

CREATE TABLE `layer_node` (
  `id`   INTEGER PRIMARY KEY NOT NULL,
  `geom` GEOMETRY NOT NULL,
  SPATIAL INDEX (`geom`)
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
