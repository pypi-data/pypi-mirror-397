"""
Wedata PostgreSQL Online Store Implementation

Key differences from default PostgreSQL online store:
1. Uses feature view schema as table structure (wide table instead of EAV model)
2. No entity key serialization - stores raw key values
3. Each feature view has its own table with all feature columns
"""

import contextlib
import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, Generator, List, Optional, Sequence, Tuple

from feast import Entity, FeatureView, ValueType
from feast.infra.online_stores.helpers import _to_naive_utc
from feast.infra.online_stores.online_store import OnlineStore
from feast.infra.utils.postgres.connection_utils import _get_conn, _get_conn_async, _get_connection_pool, _get_connection_pool_async
from feast.infra.utils.postgres.postgres_config import ConnectionType, PostgreSQLConfig
from feast.protos.feast.types.EntityKey_pb2 import EntityKey as EntityKeyProto
from feast.protos.feast.types.Value_pb2 import Value as ValueProto
from feast.repo_config import RepoConfig
from psycopg import AsyncConnection, sql
from psycopg.connection import Connection
from psycopg_pool import AsyncConnectionPool, ConnectionPool

logger = logging.getLogger(__name__)


class WedataPostgreSQLOnlineStoreConfig(PostgreSQLConfig):
    """Configuration for Wedata PostgreSQL online store"""

    type: str  # "wedata_feast.postgres_online_store.WedataPostgreSQLOnlineStore"


class WedataPostgreSQLOnlineStore(OnlineStore):
    """
    Wedata PostgreSQL Online Store that:
    1. Creates wide tables based on feature view schema
    2. Stores entity keys without serialization
    """

    _conn: Optional[Connection] = None
    _conn_pool: Optional[ConnectionPool] = None
    _conn_async: Optional[AsyncConnection] = None
    _conn_pool_async: Optional[AsyncConnectionPool] = None

    @contextlib.contextmanager
    def _get_conn(self, config: RepoConfig, autocommit: bool = False) -> Generator[Connection, Any, Any]:
        """Get a database connection"""

        if config.online_store.conn_type == ConnectionType.pool:
            if not self._conn_pool:
                self._conn_pool = _get_connection_pool(config.online_store)
                self._conn_pool.open()
            connection = self._conn_pool.getconn()
            connection.set_autocommit(autocommit)
            yield connection
            self._conn_pool.putconn(connection)
        else:
            if not self._conn:
                self._conn = _get_conn(config.online_store)
            self._conn.set_autocommit(autocommit)
            yield self._conn

    @contextlib.asynccontextmanager
    async def _get_conn_async(self, config: RepoConfig, autocommit: bool = False) -> AsyncGenerator[AsyncConnection, Any]:
        """Get an async database connection"""
        if config.online_store.conn_type == ConnectionType.pool:
            if not self._conn_pool_async:
                self._conn_pool_async = await _get_connection_pool_async(config.online_store)
                await self._conn_pool_async.open()
            connection = await self._conn_pool_async.getconn()
            await connection.set_autocommit(autocommit)
            yield connection
            await self._conn_pool_async.putconn(connection)
        else:
            if not self._conn_async:
                self._conn_async = await _get_conn_async(config.online_store)
            await self._conn_async.set_autocommit(autocommit)
            yield self._conn_async

    def _get_entity_key_columns(self, table: FeatureView) -> List[Tuple[str, str]]:
        """
        Get entity key column definitions
        Returns: List of (column_name, postgres_type) tuples
        """
        columns = []
        for entity in table.entity_columns:
            col_name = entity.name
            pg_type = self._feast_type_to_postgres_type(entity.dtype.to_value_type())
            columns.append((col_name, pg_type))
        return columns

    def _feast_type_to_postgres_type(self, value_type: ValueType) -> str:
        """Convert Feast ValueType to PostgreSQL type"""
        type_mapping = {
            ValueType.BOOL: "BOOLEAN",
            ValueType.BYTES: "BYTEA",
            ValueType.STRING: "TEXT",
            ValueType.INT32: "INTEGER",
            ValueType.INT64: "BIGINT",
            ValueType.FLOAT: "REAL",
            ValueType.DOUBLE: "DOUBLE PRECISION",
            ValueType.UNIX_TIMESTAMP: "TIMESTAMPTZ",
            ValueType.BOOL_LIST: "BOOLEAN[]",
            ValueType.BYTES_LIST: "BYTEA[]",
            ValueType.STRING_LIST: "TEXT[]",
            ValueType.INT32_LIST: "INTEGER[]",
            ValueType.INT64_LIST: "BIGINT[]",
            ValueType.FLOAT_LIST: "REAL[]",
            ValueType.DOUBLE_LIST: "DOUBLE PRECISION[]",
            ValueType.UNIX_TIMESTAMP_LIST: "TIMESTAMPTZ[]",
        }
        return type_mapping.get(value_type, "TEXT")

    def _proto_value_to_sql_value(self, val: ValueProto) -> Any:
        """Convert protobuf Value to SQL value"""
        val_type = val.WhichOneof("val")

        if val_type == "bool_val":
            return val.bool_val
        elif val_type == "bytes_val":
            return val.bytes_val
        elif val_type == "string_val":
            return val.string_val
        elif val_type == "int32_val":
            return val.int32_val
        elif val_type == "int64_val":
            return val.int64_val
        elif val_type == "float_val":
            return val.float_val
        elif val_type == "double_val":
            return val.double_val
        elif val_type == "unix_timestamp_val":
            return datetime.fromtimestamp(val.unix_timestamp_val.seconds)
        elif val_type == "bool_list_val":
            return list(val.bool_list_val.val)
        elif val_type == "bytes_list_val":
            return list(val.bytes_list_val.val)
        elif val_type == "string_list_val":
            return list(val.string_list_val.val)
        elif val_type == "int32_list_val":
            return list(val.int32_list_val.val)
        elif val_type == "int64_list_val":
            return list(val.int64_list_val.val)
        elif val_type == "float_list_val":
            return list(val.float_list_val.val)
        elif val_type == "double_list_val":
            return list(val.double_list_val.val)
        else:
            return None

    def _sql_value_to_proto_value(self, sql_val: Any, value_type: ValueType) -> ValueProto:
        """Convert SQL value to protobuf Value"""
        val = ValueProto()

        if sql_val is None:
            return val

        if value_type == ValueType.BOOL:
            val.bool_val = sql_val
        elif value_type == ValueType.BYTES:
            val.bytes_val = bytes(sql_val) if not isinstance(sql_val, bytes) else sql_val
        elif value_type == ValueType.STRING:
            val.string_val = sql_val
        elif value_type == ValueType.INT32:
            val.int32_val = sql_val
        elif value_type == ValueType.INT64:
            val.int64_val = sql_val
        elif value_type == ValueType.FLOAT:
            val.float_val = sql_val
        elif value_type == ValueType.DOUBLE:
            val.double_val = sql_val
        elif value_type == ValueType.UNIX_TIMESTAMP:
            val.unix_timestamp_val.seconds = int(sql_val.timestamp())
        elif value_type == ValueType.BOOL_LIST:
            val.bool_list_val.val.extend(sql_val)
        elif value_type == ValueType.BYTES_LIST:
            val.bytes_list_val.val.extend(sql_val)
        elif value_type == ValueType.STRING_LIST:
            val.string_list_val.val.extend(sql_val)
        elif value_type == ValueType.INT32_LIST:
            val.int32_list_val.val.extend(sql_val)
        elif value_type == ValueType.INT64_LIST:
            val.int64_list_val.val.extend(sql_val)
        elif value_type == ValueType.FLOAT_LIST:
            val.float_list_val.val.extend(sql_val)
        elif value_type == ValueType.DOUBLE_LIST:
            val.double_list_val.val.extend(sql_val)

        return val

    def _extract_entity_keys(self, entity_key_proto: EntityKeyProto) -> Dict[str, Any]:
        """
        Extract entity keys from EntityKeyProto without serialization
        Returns: Dictionary of {entity_name: value}
        """
        entity_dict = {}
        for idx, key in enumerate(entity_key_proto.join_keys):
            val = self._proto_value_to_sql_value(entity_key_proto.entity_values[idx])
            entity_dict[key] = val
        return entity_dict

    def online_write_batch(
        self,
        config: RepoConfig,
        table: FeatureView,
        data: List[Tuple[EntityKeyProto, Dict[str, ValueProto], datetime, Optional[datetime]]],
        progress: Optional[Callable[[int], Any]],
    ) -> None:
        """Write a batch of feature data to the online store"""
        if not data:
            return

        table_name = _table_id(config.project, table)

        # Get entity columns and feature columns
        entity_cols = self._get_entity_key_columns(table)
        entity_col_names = [col[0] for col in entity_cols]

        # Build feature column names
        feature_col_names = [f.name for f in table.features]

        # Prepare all column names for insert
        all_columns = entity_col_names + feature_col_names + [table.source.timestamp_field, table.source.created_timestamp_column]

        # Prepare insert values
        insert_values = []
        for entity_key_proto, feature_values, timestamp, created_ts in data:
            # Extract entity key values (no serialization)
            entity_dict = self._extract_entity_keys(entity_key_proto)

            # Convert timestamps
            timestamp = _to_naive_utc(timestamp)
            if created_ts is not None:
                created_ts = _to_naive_utc(created_ts)

            # Build row values
            row_values = []

            # Add entity key values
            for col_name in entity_col_names:
                row_values.append(entity_dict.get(col_name))

            # Add feature values
            for feature_name in feature_col_names:
                proto_val = feature_values.get(feature_name)
                if proto_val:
                    sql_val = self._proto_value_to_sql_value(proto_val)
                    row_values.append(sql_val)
                else:
                    row_values.append(None)

            # Add timestamps
            row_values.append(timestamp)
            row_values.append(created_ts)

            insert_values.append(tuple(row_values))

        # Build INSERT query with ON CONFLICT
        columns_sql = sql.SQL(", ").join([sql.Identifier(col) for col in all_columns])
        placeholders = sql.SQL(", ").join([sql.Placeholder()] * len(all_columns))

        # Build UPDATE clause for conflict resolution
        update_assignments = []
        for col in feature_col_names + [table.source.timestamp_field, table.source.created_timestamp_column]:
            update_assignments.append(sql.SQL("{} = EXCLUDED.{}").format(sql.Identifier(col), sql.Identifier(col)))
        update_clause = sql.SQL(", ").join(update_assignments)

        # Build complete query
        query = sql.SQL(
            """
            INSERT INTO {} ({})
            VALUES ({})
            ON CONFLICT ({}) DO UPDATE SET {}
            """
        ).format(
            sql.Identifier(table_name),
            columns_sql,
            placeholders,
            sql.SQL(", ").join([sql.Identifier(col) for col in entity_col_names]),
            update_clause,
        )

        # Execute batch insert
        with self._get_conn(config) as conn, conn.cursor() as cur:
            cur.executemany(query, insert_values)
            conn.commit()

        if progress:
            progress(len(data))

    def online_read(
        self,
        config: RepoConfig,
        table: FeatureView,
        entity_keys: List[EntityKeyProto],
        requested_features: Optional[List[str]] = None,
    ) -> List[Tuple[Optional[datetime], Optional[Dict[str, ValueProto]]]]:
        """Read feature data from the online store"""
        if not entity_keys:
            return []

        table_name = _table_id(config.project, table)

        # Get entity column names
        entity_cols = self._get_entity_key_columns(table)
        entity_col_names = [col[0] for col in entity_cols]

        # Determine which features to fetch
        if requested_features:
            feature_names = requested_features
        else:
            feature_names = [f.name for f in table.features]

        # Build feature type mapping
        feature_type_map = {f.name: f.dtype.to_value_type() for f in table.features}

        # Prepare entity key conditions
        entity_key_dicts = []
        for entity_key_proto in entity_keys:
            entity_dict = self._extract_entity_keys(entity_key_proto)
            entity_key_dicts.append(entity_dict)

        # Build WHERE clause for multiple entity keys
        where_conditions = []
        query_params = []

        for entity_dict in entity_key_dicts:
            entity_conditions = []
            for col_name in entity_col_names:
                entity_conditions.append(sql.SQL("{} = %s").format(sql.Identifier(col_name)))
                query_params.append(entity_dict[col_name])

            where_conditions.append(sql.SQL("({})").format(sql.SQL(" AND ").join(entity_conditions)))

        where_clause = sql.SQL(" OR ").join(where_conditions)

        # Build SELECT columns
        select_columns = (
            [sql.Identifier(col) for col in entity_col_names]
            + [sql.Identifier(f) for f in feature_names]
            + [sql.Identifier(table.source.timestamp_field)]
        )

        # Build and execute query
        query = sql.SQL(
            """
            SELECT {}
            FROM {}
            WHERE {}
            """
        ).format(sql.SQL(", ").join(select_columns), sql.Identifier(table_name), where_clause)

        with self._get_conn(config, autocommit=True) as conn, conn.cursor() as cur:
            cur.execute(query, query_params)
            rows = cur.fetchall()

        # Process results and match with input entity keys
        result: List[Tuple[Optional[datetime], Optional[Dict[str, ValueProto]]]] = []

        # Create a lookup dict for fast matching
        rows_by_entity = {}
        for row in rows:
            # Extract entity key from row
            entity_key_tuple = tuple(row[: len(entity_col_names)])
            rows_by_entity[entity_key_tuple] = row

        # Match each input entity key with results
        for entity_dict in entity_key_dicts:
            entity_key_tuple = tuple(entity_dict[col] for col in entity_col_names)

            if entity_key_tuple in rows_by_entity:
                row = rows_by_entity[entity_key_tuple]

                # Extract features (skip entity columns)
                feature_values = {}
                for i, feature_name in enumerate(feature_names):
                    sql_val = row[len(entity_col_names) + i]
                    if sql_val is not None:
                        value_type = feature_type_map[feature_name]
                        proto_val = self._sql_value_to_proto_value(sql_val, value_type)
                        feature_values[feature_name] = proto_val

                # Extract timestamp (last column)
                event_ts = row[-1]

                result.append((event_ts, feature_values))
            else:
                result.append((None, None))

        return result

    async def online_read_async(
        self,
        config: RepoConfig,
        table: FeatureView,
        entity_keys: List[EntityKeyProto],
        requested_features: Optional[List[str]] = None,
    ) -> List[Tuple[Optional[datetime], Optional[Dict[str, ValueProto]]]]:
        """Async version of online_read"""
        if not entity_keys:
            return []

        table_name = _table_id(config.project, table)

        # Get entity column names
        entity_cols = self._get_entity_key_columns(table)
        entity_col_names = [col[0] for col in entity_cols]

        # Determine which features to fetch
        if requested_features:
            feature_names = requested_features
        else:
            feature_names = [f.name for f in table.features]

        # Build feature type mapping
        feature_type_map = {f.name: f.dtype.to_value_type() for f in table.features}

        # Prepare entity key conditions
        entity_key_dicts = []
        for entity_key_proto in entity_keys:
            entity_dict = self._extract_entity_keys(entity_key_proto)
            entity_key_dicts.append(entity_dict)

        # Build WHERE clause for multiple entity keys
        where_conditions = []
        query_params = []

        for entity_dict in entity_key_dicts:
            entity_conditions = []
            for col_name in entity_col_names:
                entity_conditions.append(sql.SQL("{} = %s").format(sql.Identifier(col_name)))
                query_params.append(entity_dict[col_name])

            where_conditions.append(sql.SQL("({})").format(sql.SQL(" AND ").join(entity_conditions)))

        where_clause = sql.SQL(" OR ").join(where_conditions)

        # Build SELECT columns
        select_columns = (
            [sql.Identifier(col) for col in entity_col_names]
            + [sql.Identifier(f) for f in feature_names]
            + [sql.Identifier(table.source.timestamp_field)]
        )

        # Build and execute query
        query = sql.SQL(
            """
            SELECT {}
            FROM {}
            WHERE {}
            """
        ).format(sql.SQL(", ").join(select_columns), sql.Identifier(table_name), where_clause)

        async with self._get_conn_async(config, autocommit=True) as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, query_params)
                rows = await cur.fetchall()

        # Process results and match with input entity keys
        result: List[Tuple[Optional[datetime], Optional[Dict[str, ValueProto]]]] = []

        # Create a lookup dict for fast matching
        rows_by_entity = {}
        for row in rows:
            # Extract entity key from row
            entity_key_tuple = tuple(row[: len(entity_col_names)])
            rows_by_entity[entity_key_tuple] = row

        # Match each input entity key with results
        for entity_dict in entity_key_dicts:
            entity_key_tuple = tuple(entity_dict[col] for col in entity_col_names)

            if entity_key_tuple in rows_by_entity:
                row = rows_by_entity[entity_key_tuple]

                # Extract features (skip entity columns)
                feature_values = {}
                for i, feature_name in enumerate(feature_names):
                    sql_val = row[len(entity_col_names) + i]
                    if sql_val is not None:
                        value_type = feature_type_map[feature_name]
                        proto_val = self._sql_value_to_proto_value(sql_val, value_type)
                        feature_values[feature_name] = proto_val

                # Extract timestamp (last column)
                event_ts = row[-1]

                result.append((event_ts, feature_values))
            else:
                result.append((None, None))

        return result

    def update(
        self,
        config: RepoConfig,
        tables_to_delete: Sequence[FeatureView],
        tables_to_keep: Sequence[FeatureView],
        entities_to_delete: Sequence[Entity],
        entities_to_keep: Sequence[Entity],
        partial: bool,
    ):
        """Update the online store schema"""
        project = config.project
        schema_name = config.online_store.db_schema or config.online_store.user

        with self._get_conn(config) as conn, conn.cursor() as cur:
            # Create schema if not exists
            cur.execute(
                """
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name = %s
                """,
                (schema_name,),
            )
            schema_exists = cur.fetchone()
            if not schema_exists:
                cur.execute(
                    sql.SQL("CREATE SCHEMA IF NOT EXISTS {} AUTHORIZATION {}").format(
                        sql.Identifier(schema_name),
                        sql.Identifier(config.online_store.user),
                    ),
                )

            # Drop tables that are no longer needed
            for table in tables_to_delete:
                table_name = _table_id(project, table)
                cur.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table_name)))
                logger.info(f"Dropped table {table_name}")

            # Create or update tables
            for table in tables_to_keep:
                table_name = _table_id(project, table)

                # Build entity columns
                entity_cols = self._get_entity_key_columns(table)

                # Build feature columns
                feature_cols = []
                for feature in table.features:
                    pg_type = self._feast_type_to_postgres_type(feature.dtype.to_value_type())
                    feature_cols.append((feature.name, pg_type))

                # Build CREATE TABLE statement
                column_defs = []

                # Add entity columns
                for col_name, col_type in entity_cols:
                    column_defs.append(sql.SQL("{} {} NOT NULL").format(sql.Identifier(col_name), sql.SQL(col_type)))

                # Add feature columns
                for col_name, col_type in feature_cols:
                    column_defs.append(sql.SQL("{} {}").format(sql.Identifier(col_name), sql.SQL(col_type)))

                # Add timestamp columns
                column_defs.append(sql.SQL("{} TIMESTAMPTZ").format(sql.Identifier(table.source.timestamp_field)))
                column_defs.append(sql.SQL("{} TIMESTAMPTZ").format(sql.Identifier(table.source.created_timestamp_column)))

                # Add primary key constraint
                entity_col_names = [col[0] for col in entity_cols]
                primary_key = sql.SQL("PRIMARY KEY ({})").format(sql.SQL(", ").join([sql.Identifier(col) for col in entity_col_names]))
                column_defs.append(primary_key)

                # Execute CREATE TABLE
                create_table_query = sql.SQL(
                    """
                    CREATE TABLE IF NOT EXISTS {} (
                        {}
                    )
                    """
                ).format(sql.Identifier(table_name), sql.SQL(",\n").join(column_defs))

                cur.execute(create_table_query)
                logger.info(f"Created/verified table {table_name}")

                # Add comments for feature columns with descriptions
                for feature in table.features:
                    if feature.description:
                        comment_query = sql.SQL("COMMENT ON COLUMN {}.{} IS {}").format(
                            sql.Identifier(table_name), sql.Identifier(feature.name), sql.Literal(feature.description)
                        )
                        cur.execute(comment_query)
                        logger.debug(f"Added comment for column {table_name}.{feature.name}")

                # Add comments for entity columns with descriptions
                for entity in table.entity_columns:
                    if entity.description:
                        comment_query = sql.SQL("COMMENT ON COLUMN {}.{} IS {}").format(
                            sql.Identifier(table_name), sql.Identifier(entity.name), sql.Literal(entity.description)
                        )
                        cur.execute(comment_query)
                        logger.debug(f"Added comment for column {table_name}.{entity.name}")

                # Create index on timestamp for efficient queries
                cur.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {} ({} DESC)").format(
                        sql.Identifier(f"{table_name}_{table.source.timestamp_field}_idx"),
                        sql.Identifier(table_name),
                        sql.Identifier(table.source.timestamp_field),
                    )
                )

            conn.commit()

    def teardown(
        self,
        config: RepoConfig,
        tables: Sequence[FeatureView],
        entities: Sequence[Entity],
    ):
        """Teardown the online store"""
        project = config.project
        try:
            with self._get_conn(config) as conn, conn.cursor() as cur:
                for table in tables:
                    table_name = _table_id(project, table)
                    cur.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table_name)))
                    logger.info(f"Dropped table {table_name}")
                conn.commit()
        except Exception:
            logging.exception("Teardown failed")
            raise


def _table_id(project: str, table: FeatureView) -> str:
    """Generate table name from project and feature view"""
    return f"{project}_{table.name}"
