USE comp_test;

CREATE TABLE t1_@@SE_COMP@@ (
	a1 INT,
	a2 DECIMAL(65,10),
	a3 CHAR(255) COLLATE 'latin1_bin',
	a4 TIMESTAMP,
	a5 TEXT CHARACTER SET 'utf8' COLLATE 'utf8_bin',
	PRIMARY KEY (a1) @@COMMENT@@
) ENGINE=@@SE@@ @@ROW_FORMAT_OPT@@ PARTITION BY HASH(a1) PARTITIONS 4;

CREATE TABLE t2_@@SE_COMP@@ (
	b1 DATE,
	b2 TIME,
	b3 BLOB,
	b4 varchar(100) COLLATE 'latin1_bin', -- TODO this originally should have been JSON but moved to varchar because of MYR-152
	b5 float(25,5),
	PRIMARY KEY (b1) @@COMMENT@@
) ENGINE=@@SE@@ @@ROW_FORMAT_OPT@@;

CREATE TABLE t3_@@SE_COMP@@ (
	c1 varchar(255) COLLATE 'binary',
	c2 BINARY(20),
	c3 VARBINARY(100),
	c4 SET('one', 'two', 'three'),
	c5 ENUM('x-small', 'small', 'medium', 'large', 'x-large'),
	PRIMARY KEY (c1) @@COMMENT@@
) ENGINE=@@SE@@ @@ROW_FORMAT_OPT@@;
