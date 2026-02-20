# Unit Test Examples

## Example 1: Complete Test Class

```java
@UnitTest
@ExtendWith(MockitoExtension.class)
class TimerTableCheckServiceTest {

    private static final String TIMER_TABLE_NAME = "timer";
    private static final String[] TABLE_TYPE = {"TABLE"};
    private static final String SCHEMA_NAME = TENANT_ID + "_mod_scheduler";

    @Mock
    private DataSource dataSource;
    @Mock
    private Connection connection;
    @Mock
    private DatabaseMetaData databaseMetaData;
    @Mock
    private ResultSet resultSet;
    @Mock
    private FolioExecutionContext context;
    @Mock
    private FolioModuleMetadata moduleMetadata;

    @AfterEach
    void tearDown() {
        verifyNoMoreInteractions(dataSource, connection, databaseMetaData, resultSet);
    }

    @Test
    void tableExists_positive_tableIsPresent() throws SQLException {
        setupContextMocks();
        var service = new TimerTableCheckService(dataSource, context);

        when(dataSource.getConnection()).thenReturn(connection);
        when(connection.getMetaData()).thenReturn(databaseMetaData);
        when(databaseMetaData.getTables(isNull(), eq(SCHEMA_NAME), eq(TIMER_TABLE_NAME), eq(TABLE_TYPE)))
            .thenReturn(resultSet);
        when(resultSet.next()).thenReturn(true);

        boolean result = service.tableExists();

        assertThat(result).isTrue();
        verify(connection).close();
        verify(resultSet).close();
    }

    @Test
    void tableExists_negative_sqlExceptionWhenGettingConnection() throws SQLException {
        var service = new TimerTableCheckService(dataSource, context);
        var expectedException = new SQLException("Failed to get connection");

        when(dataSource.getConnection()).thenThrow(expectedException);

        assertThatThrownBy(() -> service.tableExists())
            .isInstanceOf(DataRetrievalFailureException.class)
            .hasMessageContaining("Failed to check if table " + TIMER_TABLE_NAME + " exists")
            .hasCause(expectedException);
    }

    private void setupContextMocks() {
        when(context.getFolioModuleMetadata()).thenReturn(moduleMetadata);
        when(context.getTenantId()).thenReturn(TENANT_ID);
        when(moduleMetadata.getDBSchemaName(TENANT_ID)).thenReturn(SCHEMA_NAME);
    }
}
```

## Example 2: Testing with Different Configurations

```java
@Test
void operation_withUpperCase_success() throws SQLException {
    setupContextMocks();
    var service = new MyService(dataSource, context, TableNameCase.UPPER);

    when(dataSource.getConnection()).thenReturn(connection);
    when(connection.getMetaData()).thenReturn(databaseMetaData);
    when(databaseMetaData.getTables(isNull(), eq(SCHEMA_NAME), eq("TIMER"), eq(TABLE_TYPE)))
        .thenReturn(resultSet);
    when(resultSet.next()).thenReturn(true);

    boolean result = service.tableExists();

    assertThat(result).isTrue();
    verify(connection).close();
    verify(resultSet).close();
}

@Test
void operation_withLowerCase_success() throws SQLException {
    setupContextMocks();
    var service = new MyService(dataSource, context, TableNameCase.LOWER);

    when(dataSource.getConnection()).thenReturn(connection);
    when(connection.getMetaData()).thenReturn(databaseMetaData);
    when(databaseMetaData.getTables(isNull(), eq(SCHEMA_NAME), eq("timer"), eq(TABLE_TYPE)))
        .thenReturn(resultSet);
    when(resultSet.next()).thenReturn(true);

    boolean result = service.tableExists();

    assertThat(result).isTrue();
    verify(connection).close();
    verify(resultSet).close();
}
```
