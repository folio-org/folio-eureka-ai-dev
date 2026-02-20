# Entry Point Templates

Use the appropriate template(s) for the feature's entry point type. A feature may have multiple entry points.

## REST (prefer OpenAPI spec)

```markdown
## Entry point(s)
| Method | Path | Description |
|--------|------|-------------|
| GET | /resource/{id} | Returns the resource representation |
```

## Kafka Consumer

Use only when the feature is triggered by incoming messages.

```markdown
## Entry point(s)
| Type | Topic | Description |
|------|-------|-------------|
| Kafka Consumer | <topic-name or property-key> | Processes <event> messages |

### Event processing
- When processed: <on each message / batched / etc., if evidenced>
- Event types handled: <if evidenced>
- Processing behavior: <observable effects and constraints>
```

## Scheduled Job

```markdown
## Entry point(s)
| Type | Schedule | Description |
|------|----------|-------------|
| Scheduled Job | <cron/fixed-delay> | Performs <behavior> |
```

## Internal Event

Use only when an internal event is a meaningful entry point for observable behavior.

```markdown
## Entry point(s)
| Type | Event | Description |
|------|-------|-------------|
| Internal Event | <event-class or name> | Triggers <behavior> |
```
