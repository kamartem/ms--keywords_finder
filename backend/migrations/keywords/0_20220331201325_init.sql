-- upgrade --
CREATE TABLE IF NOT EXISTS "tasks" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "keywords" JSONB NOT NULL,
    "created_date" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "resource" (
    "created_at" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "domain" VARCHAR(255) NOT NULL,
    "done" BOOL NOT NULL  DEFAULT False,
    "done_http" BOOL NOT NULL  DEFAULT False,
    "done_https" BOOL NOT NULL  DEFAULT False,
    "error_http" TEXT,
    "error_https" TEXT,
    "order" BIGINT,
    "task_id" INT NOT NULL REFERENCES "tasks" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "resourceitem" (
    "created_at" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ   DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "url" VARCHAR(255) NOT NULL,
    "done" BOOL NOT NULL  DEFAULT False,
    "error" TEXT,
    "keywords_found" JSONB NOT NULL,
    "resource_id" INT NOT NULL REFERENCES "resource" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
