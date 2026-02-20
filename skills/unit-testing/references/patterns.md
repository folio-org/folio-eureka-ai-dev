# Unit Testing Patterns

## Parameterized Tests with Single Parameter

When testing methods that should fail for multiple input values, use `Stream<Type>` directly:

```java
@ParameterizedTest
@MethodSource("invalidInputsProvider")
void operation_negative_throwsException(String invalidInput) {
    assertThatThrownBy(() -> service.operation(invalidInput))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("Invalid input");
}

private static Stream<String> invalidInputsProvider() {
    return Stream.of(
        "invalid-1",
        "invalid-2",
        "invalid-3"
    );
}
```

Use `Stream<String>` (or the appropriate type) directly instead of `Stream<Arguments>` when testing a single parameter.

## Explicit Type Declaration for Lambdas

When var type inference fails with lambda expressions (e.g., `Supplier`), use explicit type declaration:

```java
// ✅ Explicit type declaration
Supplier<RuntimeException> supplier = () -> new IllegalStateException("error");

var result = service.operation(supplier);
```

## Testing Exact Matching Logic

Include similar values that should NOT match to verify only exact matches are selected:

```java
@Test
void findModule_positive_exactMatchWithSimilarNames() {
    var modules = List.of(
        "mod-foo-1.0.0",        // Exact match
        "mod-foo-item-1.0.0",   // Similar — must NOT match
        "mod-foobar-1.0.0"      // Similar — must NOT match
    );

    var result = service.findModuleByName("mod-foo", modules);

    assertThat(result).isEqualTo("mod-foo-1.0.0");
}
```

## Testing Composed Logic with Utility Methods

Test all error paths from utility methods (e.g., `CollectionUtils.takeOne()`):

```java
@Test
void findModule_negative_noModulesFound() {
    assertThatThrownBy(() -> service.findModuleByName("mod-foo", List.of()))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("No modules found");
}

@Test
void findModule_negative_multipleModulesFound() {
    var duplicates = List.of("mod-foo-1.0.0", "mod-foo-2.0.0");

    assertThatThrownBy(() -> service.findModuleByName("mod-foo", duplicates))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("Multiple modules found");
}
```

## Testing Services That Create Internal Copies

When a service creates defensive copies of input, stub the copy operation and use the copy in all subsequent stubs:

```java
@Test
void operation_positive_withDeepCopy() {
    var input = createInput();
    var inputCopy = createInput();  // Separate object with same content
    var output = createOutput();
    var entity = createEntity(inputCopy);

    when(mapper.deepCopy(input)).thenReturn(inputCopy);
    when(mapper.toEntity(inputCopy)).thenReturn(entity);  // Use the copy, not input
    when(repository.save(entity)).thenReturn(entity);
    when(mapper.toOutput(entity)).thenReturn(output);

    var actual = service.operation(input);

    assertThat(actual).isEqualTo(output);
}
```

Common copy methods to stub: `mapper.deepCopy()`, `BeanUtils.copyProperties()`, custom clone/copy methods, builder-based copies.

## Use Fluent API Consistently in Test Data

```java
// ✅ Preferred
var entity = new Entity()
    .id(ID)
    .name("test")
    .enabled(true);

// Or with helper methods:
var entity = createEntity().id(ID).enabled(true);
```

## Testing with Context Dependencies

```java
private void setupContextMocks() {
    when(context.getFolioModuleMetadata()).thenReturn(moduleMetadata);
    when(context.getTenantId()).thenReturn(TENANT_ID);
    when(moduleMetadata.getDBSchemaName(TENANT_ID)).thenReturn(SCHEMA_NAME);
}

@Test
void testWithContext() {
    setupContextMocks();
    var service = new MyService(dataSource, context);
    // test execution
}
```

## Testing Null Validation

```java
@Test
void operation_negative_parameterIsNull() {
    var service = new MyService(dependencies);

    assertThatThrownBy(() -> service.operation(null))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("Parameter must not be null");
}
```
