DROP TABLE persist;

CREATE TABLE persist (
domein VARCHAR(35) ,
botskey VARCHAR(35) ,
content TEXT ,
ts timestamp NOT NULL DEFAULT (datetime('now','localtime')),
PRIMARY KEY (domein, botskey)
);
