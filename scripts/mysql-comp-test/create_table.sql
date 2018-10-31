USE comp_test;

CREATE TABLE t1_@@SE_COMP@@ (
	a1 INT,
	a2 DECIMAL(65,10),
	a3 CHAR(255) COLLATE 'latin1_bin',
	a4 TIMESTAMP,
	a5 TEXT CHARACTER SET 'utf8' COLLATE 'utf8_bin',
	PRIMARY KEY (a1) @@COMMENT_PARTITIONED@@
) ENGINE=@@SE@@ PARTITION BY HASH(a1) PARTITIONS 4;

CREATE TABLE t2_@@SE_COMP@@ (
	a1 DATE,
	a2 TIME,
	a3 BLOB,
	a4 varchar(100) COLLATE 'latin1_bin', -- TODO this originally should have been JSON but moved to varchar because of MYR-152
	a5 float(25,5),
	PRIMARY KEY (a1) @@COMMENT@@
) ENGINE=@@SE@@;

CREATE TABLE t3_@@SE_COMP@@ (
	a1 varchar(255) COLLATE 'binary',
	a2 BINARY(20),
	a3 VARBINARY(100),
	a4 SET('one', 'two', 'three'),
	a5 ENUM('x-small', 'small', 'medium', 'large', 'x-large'),
	PRIMARY KEY (a1) @@COMMENT@@
) ENGINE=@@SE@@;
