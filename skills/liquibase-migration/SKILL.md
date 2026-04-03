---
name: liquibase-migration
description: >-
  Use when creating, editing, or reviewing Liquibase database migrations in FOLIO Spring Boot modules.
  Always use this skill for any db migration, schema change, changeset authoring, XML changelog creation,
  database migration script, or table/column/index/FK changes in a FOLIO module — even if the user
  just says "add a column", "create a table", or "write a migration". Enforces FOLIO folder structure
  (changelog-master → changelog-vX.Y → vX.Y/ files), changeset ID naming convention
  (JIRA@@scope-action-target), comment tags, and FOLIO-standard column types.
license: Apache-2.0
compatibility: FOLIO Spring Boot module using Maven, PostgreSQL database, Liquibase via folio-spring-base dependency.
metadata:
  author: folio-org
  version: "1.0.0"
---

# FOLIO Liquibase Migration Guidelines

## 1. Folder Structure

### Preferred Layout

The preferred structure is versioned — each release gets its own folder and aggregator file:

```
src/main/resources/db/changelog/
├── changelog-master.xml
└── changes/
    ├── changelog-v1.0.xml
    ├── v1.0/
    │   ├── create-table-foo.xml
    │   └── add-index-foo-bar.xml
    ├── changelog-v2.0.xml
    └── v2.0/
        └── alter-table-foo-add-column-baz.xml
```

**Preferred structure rules:**
- `changelog-master.xml` includes **only** version aggregators (`changes/changelog-vX.Y.xml`)
- Each `changelog-vX.Y.xml` includes **only** files from `changes/vX.Y/`
- Create a new `vX.Y/` directory and `changelog-vX.Y.xml` for each module release
- All `<include>` elements use `relativeToChangelogFile="true"`

**changelog-master.xml example:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                   https://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd">

  <include file="/changes/changelog-v1.0.xml" relativeToChangelogFile="true"/>
  <include file="/changes/changelog-v2.0.xml" relativeToChangelogFile="true"/>
</databaseChangeLog>
```

**changes/changelog-v2.0.xml example:**
```xml
<databaseChangeLog ...>
  <include file="/changes/v2.0/create-table-foo.xml" relativeToChangelogFile="true"/>
  <include file="/changes/v2.0/alter-table-foo-add-column-bar.xml" relativeToChangelogFile="true"/>
</databaseChangeLog>
```

### Working with Existing Modules

Before creating new files, check the existing changelog structure in the module. **Always follow the layout already in use** — do not reorganize or introduce a different structure mid-project.

- If the module uses `changelog-master.xml` with per-version aggregators → follow that pattern
- If the module uses a flat `changelog-master.xml` with direct `<include>` entries → continue adding entries directly there
- If the module uses different naming or nesting → match what is already there

When starting a brand new module with no existing migrations, use the preferred structure above.

---

## 2. Changeset ID Naming Convention

### Format

```
<JIRA-TICKET>@@<scope>-<action>-<target>[-<detail>]
```

### Allowed Values

| Part       | Values                                                                                     |
|------------|--------------------------------------------------------------------------------------------|
| **scope**  | `schema`, `data`, `refactor`, `fix`                                                        |
| **action** | `create`, `alter`, `drop`, `rename`, `migrate`, `backfill`, `seed`, `cleanup`, `enforce`   |
| **target** | `table-<name>`, `column-<table>-<col>`, `index-<name>`, `fk-<from>-to-<to>`, `type-<name>` |
| **detail** | *(optional)* specific intent, e.g. `add-not-null`, `add-metadata-fields`                   |

### Style Rules

- Lowercase only
- Kebab-case only (no underscores, no spaces)
- ASCII only — no `:` characters
- Use imperative verbs (not gerunds or past tense)
- **IDs are immutable after release** — never rename a released changeset ID

### ✅ Good Examples

```
MYMOD-101@@schema-create-table-item
MYMOD-102@@schema-alter-table-item-add-column-status
MYMOD-103@@schema-create-index-item-status
MYMOD-104@@schema-create-fk-item-to-location
MYMOD-105@@data-seed-item-default-status
MYMOD-106@@data-migrate-rule-to-specification-rule-metadata-fields
MYMOD-107@@schema-enforce-column-item-id-not-null
MYMOD-108@@schema-create-type-status-enum
```

### ❌ Bad Examples

```
MYMOD-101@@CreateItemTable          # PascalCase, no scope/action
MYMOD-101@@schema:create:table      # colons not allowed
MYMOD-101@@schema-creating-table    # gerund
MYMOD-101@@schema-created-table     # past tense
item-table                          # missing JIRA ticket and @@
```

---

## 3. Changeset Structure

Every changeset **must** include:
1. `<comment>` — describes what the changeset does and why

```xml
<changeSet id="MYMOD-42@@schema-create-table-item" author="john_doe">
  <comment>Create item table for inventory storage</comment>

  <createTable tableName="item">
    ...
  </createTable>
</changeSet>
```

---

## 4. FOLIO Standard Column Types

Use these types consistently across all FOLIO modules:

| Purpose                              | Type                           |
|--------------------------------------|--------------------------------|
| Primary key / foreign key (UUID)     | `uuid`                         |
| Short string                         | `varchar(36)` – `varchar(250)` |
| Long string                          | `varchar(2500)` or `text`      |
| JSON blob                            | `jsonb`                        |
| Timestamp                            | `datetime`                     |
| Boolean flag                         | `bool`                         |
| Version counter (optimistic locking) | `integer`                      |
| Single character code                | `char`                         |

### Metadata Columns

Before adding metadata columns to a new table, ask the user whether they are needed. Not all tables require audit tracking.

If the user confirms, include:

```xml
<column name="created_date" type="DATETIME">
  <constraints nullable="false"/>
</column>
<column name="updated_date" type="DATETIME">
  <constraints nullable="false"/>
</column>
<column name="created_by_user_id" type="uuid">
  <constraints nullable="false"/>
</column>
<column name="updated_by_user_id" type="uuid">
  <constraints nullable="false"/>
</column>
```

---

## 5. Common Change Patterns

### Create Table

```xml
<changeSet id="MYMOD-10@@schema-create-table-item" author="jane_doe">
  <comment>Create item table</comment>

  <createTable tableName="item">
    <column name="id" type="UUID">
      <constraints nullable="false" primaryKey="true" primaryKeyName="pk_item"/>
    </column>
    <column name="barcode" type="varchar(250)"/>
    <column name="status" type="varchar(36)">
      <constraints nullable="false"/>
    </column>
    <column name="data" type="jsonb"/>
    <column name="_version" type="integer"/>
    <column name="created_date" type="DATETIME"><constraints nullable="false"/></column>
    <column name="updated_date" type="DATETIME"><constraints nullable="false"/></column>
    <column name="created_by_user_id" type="uuid"><constraints nullable="false"/></column>
    <column name="updated_by_user_id" type="uuid"><constraints nullable="false"/></column>
  </createTable>
</changeSet>
```

### Add Foreign Key

```xml
<changeSet id="MYMOD-10@@schema-create-fk-item-to-location" author="jane_doe">
  <comment>Add FK from item to location</comment>

  <addForeignKeyConstraint
    baseTableName="item"
    baseColumnNames="location_id"
    referencedTableName="location"
    referencedColumnNames="id"
    constraintName="fk_item_location_id"/>
</changeSet>
```

### Create Index

```xml
<changeSet id="MYMOD-11@@schema-create-index-item-status" author="jane_doe">
  <comment>Create B-tree index on item.status for lookup performance</comment>

  <createIndex tableName="item" indexName="idx_item_status">
    <column name="status"/>
  </createIndex>
</changeSet>
```

### Add Column

```xml
<changeSet id="MYMOD-15@@schema-alter-table-item-add-column-effective-location-id" author="jane_doe">
  <comment>Add effective_location_id column to item table</comment>

  <addColumn tableName="item">
    <column name="effective_location_id" type="UUID"/>
  </addColumn>
</changeSet>
```

### Data Migration / Seed

```xml
<changeSet id="MYMOD-20@@data-seed-item-default-status" author="jane_doe">
  <comment>Set default status 'Available' for items with null status</comment>

  <sql>
    UPDATE item
    SET status = 'Available'
    WHERE status IS NULL;
  </sql>
</changeSet>
```

---

## 6. Anti-Patterns to Avoid

❌ **Missing comment** — no context for reviewers or future developers
```xml
<!-- BAD -->
<changeSet id="MYMOD-2@@schema-alter-table-item-add-column-bar" author="foo">
  <addColumn tableName="item">...</addColumn>
</changeSet>
```

❌ **Renaming a released changeset ID** — breaks Liquibase checksum validation in all deployed environments

❌ **Multiple unrelated changes in one changeset** — makes rollback and debugging harder; one logical change per changeset

❌ **Using `runOnChange="true"`** on schema changesets — only acceptable for stored procedures/views, never for DDL
