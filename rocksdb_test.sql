USE world3;
ALTER TABLE City DROP FOREIGN KEY city_ibfk_1;
CREATE TABLE `CityRocks` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` char(35) NOT NULL DEFAULT '',
  `CountryCode` char(3) NOT NULL DEFAULT '',
  `District` char(20) NOT NULL DEFAULT '',
  `Population` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`),
  KEY `CountryCode` (`CountryCode`)
);
INSERT INTO CityRocks SELECT * FROM City;
-- ALTER TABLE City Engine=RocksDB;
OPTIMIZE TABLE CityRocks;
SHOW CREATE TABLE CityRocks;
