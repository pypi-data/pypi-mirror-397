# AllianceAuth Mumble Authenticator

## Macros used

| Macro | Description | Value |
| ----- | ----------- | ----- |
 | `{$AA_MUMBLE_AUTHENTICATOR_CHECK_INTERVAL}` | Data check interval | `5m` |
 | `{$AA_MUMBLE_AUTHENTICATOR_DB_POOL_SIZE_ALARM}` | Threshold for database pool size alarm, % | `90` |
 | `{$AA_MUMBLE_AUTHENTICATOR_HISTORY}` | Data history retention period | `31d` |
 | `{$AA_MUMBLE_AUTHENTICATOR_HISTORY_RAW}` | Raw data retention period | `1h` |
 | `{$AA_MUMBLE_AUTHENTICATOR_METRICS_URL}` | URL for metrics collection (required) | `` |
 | `{$AA_MUMBLE_AUTHENTICATOR_PASSWORD}` | HTTP basic auth password (required) | `` |
 | `{$AA_MUMBLE_AUTHENTICATOR_PROCESS_FDS_ALARM}` | Threshold for file descriptor alarm, % | `80` |
 | `{$AA_MUMBLE_AUTHENTICATOR_RATE_ALARM}` | Time window for rate calculation | `600` |
 | `{$AA_MUMBLE_AUTHENTICATOR_RESTART_ALARM}` | Program restart alert window | `600` |
 | `{$AA_MUMBLE_AUTHENTICATOR_USER}` | HTTP basic auth username (required) | `` |

## Triggers

| Name | Expression | Severity |
| ---- | ---------- | -------- |
 | Failed to move inactive user to AFK channel | `rate(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.afk_users_moved_failure_total,{$AA_MUMBLE_AUTHENTICATOR_RATE_ALARM})>0` | average |
 | Stale cache used for avatars | `rate(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.avatar_cache_stale_total,{$AA_MUMBLE_AUTHENTICATOR_RATE_ALARM})>0` | average |
 | Stale cache used for SELECT queries | `rate(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.db_cache_select_stale_total,{$AA_MUMBLE_AUTHENTICATOR_RATE_ALARM})>0` | average |
 | Database connection failure | `rate(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.db_connection_failure_total,{$AA_MUMBLE_AUTHENTICATOR_RATE_ALARM})>0` | average |
 | Connection pool: errors when reusing an existing connection | `rate(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.db_pool_connection_error_total,{$AA_MUMBLE_AUTHENTICATOR_RATE_ALARM})>0` | average |
 | Connection pool about to be exhausted | `last(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.db_pool_util)>={$AA_MUMBLE_AUTHENTICATOR_DB_POOL_SIZE_ALARM}` | warning |
 | Database query failure | `rate(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.db_query_failure_total,{$AA_MUMBLE_AUTHENTICATOR_RATE_ALARM})>0` | average |
 | ICE server health check disabled | `last(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.ice_healthcheck)="disabled"` | info |
 | ICE server is in an unknown status | `last(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.ice_healthcheck)="unknown"` | n/a |
 | ICE server is unhealthy | `last(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.ice_healthcheck)="unhealthy"` | average |
 | Too many file descriptors are being used | `last(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.process_fds_util)>={$AA_MUMBLE_AUTHENTICATOR_PROCESS_FDS_ALARM}` | warning |

## Data Items

| Name | Type | Key |
| ---- | ---- | --- |
 | Number of failed moves of users to AFK channel | dependent | `aa_mumble_authenticator.afk_users_moved_failure_total` |
 | Number of successful moves of users to AFK channel | dependent | `aa_mumble_authenticator.afk_users_moved_success_total` |
 | Time spent processing AFK users (avg) | calculated | `aa_mumble_authenticator.afk_users_process_latency_avg` |
 | Time spent processing AFK users (measurement number) | dependent | `aa_mumble_authenticator.afk_users_process_latency_count` |
 | Time spent processing AFK users (sum) | dependent | `aa_mumble_authenticator.afk_users_process_latency_sum` |
 | Number of cache hits for avatar | dependent | `aa_mumble_authenticator.avatar_cache_hit_total` |
 | Number of cache misses for avatar | dependent | `aa_mumble_authenticator.avatar_cache_miss_total` |
 | Number of times stale cache was used for avatar | dependent | `aa_mumble_authenticator.avatar_cache_stale_total` |
 | Time spent downloading avatar (avg) | calculated | `aa_mumble_authenticator.avatar_download_time_avg` |
 | Time spent downloading avatar (measurement number) | dependent | `aa_mumble_authenticator.avatar_download_time_count` |
 | Time spent downloading avatar (sum) | dependent | `aa_mumble_authenticator.avatar_download_time_sum` |
 | Number of cache hits for SELECT queries | dependent | `aa_mumble_authenticator.db_cache_select_hit_total` |
 | Number of cache misses for SELECT queries | dependent | `aa_mumble_authenticator.db_cache_select_miss_total` |
 | Number of times stale cache was used for SELECT queries | dependent | `aa_mumble_authenticator.db_cache_select_stale_total` |
 | Number of failed connections to the database | dependent | `aa_mumble_authenticator.db_connection_failure_total` |
 | Number of successful connections to the database | dependent | `aa_mumble_authenticator.db_connection_success_total` |
 | Number of connection errors when reusing an existing connection | dependent | `aa_mumble_authenticator.db_pool_connection_error_total` |
 | Number of new connections created | dependent | `aa_mumble_authenticator.db_pool_connection_new_total` |
 | Number of successful reuses of existing connections from the pool | dependent | `aa_mumble_authenticator.db_pool_connection_reuse_total` |
 | Maximum size of the connection pool | dependent | `aa_mumble_authenticator.db_pool_max_size` |
 | Current size of the connection pool | dependent | `aa_mumble_authenticator.db_pool_size` |
 | Connection pool utilisation | calculated | `aa_mumble_authenticator.db_pool_util` |
 | Number of failed queries | dependent | `aa_mumble_authenticator.db_query_failure_total` |
 | Latency of queries (avg) | calculated | `aa_mumble_authenticator.db_query_latency_avg` |
 | Latency of queries (measurement number) | dependent | `aa_mumble_authenticator.db_query_latency_count` |
 | Latency of queries (sum) | dependent | `aa_mumble_authenticator.db_query_latency_sum` |
 | Number of successful queries | dependent | `aa_mumble_authenticator.db_query_success_total` |
 | Healthcheck for ICE server | dependent | `aa_mumble_authenticator.ice_healthcheck` |
 | Total user and system CPU time spent | dependent | `aa_mumble_authenticator.process_cpu_seconds_total` |
 | File descriptors utilisation | calculated | `aa_mumble_authenticator.process_fds_util` |
 | Maximum number of open file descriptors | dependent | `aa_mumble_authenticator.process_max_fds` |
 | Number of open file descriptors | dependent | `aa_mumble_authenticator.process_open_fds` |
 | Resident memory size | dependent | `aa_mumble_authenticator.process_resident_memory_bytes` |
 | Start time of the process since unix epoch | dependent | `aa_mumble_authenticator.process_start_time_seconds` |
 | Virtual memory size | dependent | `aa_mumble_authenticator.process_virtual_memory_bytes` |
 | Time taken to authenticate users (avg) | calculated | `aa_mumble_authenticator.user_authentication_latency_avg` |
 | Time taken to authenticate users (measurement number) | dependent | `aa_mumble_authenticator.user_authentication_latency_count` |
 | Time taken to authenticate users (sum) | dependent | `aa_mumble_authenticator.user_authentication_latency_sum` |
 | AA Mumble Authenticator Metrics | http_agent | `aa_mumble_authenticator_metrics` |

## LLD rule User Discovery

#### Trigger prototypes for User Discovery

| Name | Expression | Severity |
| ---- | ---------- | -------- |
 | User {#AA_MUMBLE_AUTHENTICATOR_USER}: authentication failures | `last(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.user.status[{#AA_MUMBLE_AUTHENTICATOR_USER}])="failure"` | warning |
 | User {#AA_MUMBLE_AUTHENTICATOR_USER}: authentication failures where the data could (temporarily) | `last(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.user.status[{#AA_MUMBLE_AUTHENTICATOR_USER}])="temporarily"` | warning |
 | User {#AA_MUMBLE_AUTHENTICATOR_USER}: unknown user (fallthrough) | `last(/AllianceAuth Mumble Authenticator/aa_mumble_authenticator.user.status[{#AA_MUMBLE_AUTHENTICATOR_USER}])="fallthrough"` | warning |

### Item prototypes for User Discovery

| Name | Type | Key |
| ---- | ---- | --- |
 | User status {#AA_MUMBLE_AUTHENTICATOR_USER} | dependent | `aa_mumble_authenticator.user.status[{#AA_MUMBLE_AUTHENTICATOR_USER}]` |
