DROP TABLE mutex ;

CREATE TABLE mutex (
mutexk integer PRIMARY KEY NOT NULL,
mutexer integer DEFAULT 0,
ts timestamp NOT NULL DEFAULT (datetime('now','localtime'))
);
