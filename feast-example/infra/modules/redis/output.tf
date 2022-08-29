output "redis_id" {
  value = azurerm_redis_cache.redis.id
}

output "redis_name" {
  value = azurerm_redis_cache.redis.name
}

output "redis_conn_string" {
  value = azurerm_redis_cache.redis.primary_connection_string
}
