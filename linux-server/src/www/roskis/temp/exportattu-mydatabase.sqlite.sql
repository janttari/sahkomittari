BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "asiakkaat" (
	"ip"	TEXT,
	"nimi"	TEXT,
	"numero"	TEXT
);
CREATE TABLE IF NOT EXISTS "person" (
	"id"	int,
	"name"	varchar(30),
	"phone"	varchar(30)
);
INSERT INTO "person" VALUES (1,'Jim','123446223');
INSERT INTO "person" VALUES (2,'Tom','232124303');
INSERT INTO "person" VALUES (3,'Bill','812947283');
INSERT INTO "person" VALUES (4,'Alice','351246233');
INSERT INTO "person" VALUES (5,'Jorma','12433446223');
COMMIT;
