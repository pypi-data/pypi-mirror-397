import json
from .storage import ConfigStorageBase
import logging
import asyncio

# Необязательный импорт dglog
try:
    import dglog

    LoggerType = logging.Logger | dglog.Logger
except ImportError:
    LoggerType = logging.Logger

# Необязательный импорт dgredis
try:
    import dgredis

    HAS_DGREDIS = True
except ImportError:
    HAS_DGREDIS = False
    dgredis = None


class RedisConfigStorage(ConfigStorageBase):
    def __init__(self, redis_client, redis_key: str, auto_reload: bool = False, ts_key: str = None,
                 logger: LoggerType | None = None, use_redis_json: bool = True,
                 json_fallback_to_string: bool = True):
        super().__init__(auto_reload=auto_reload, logger=logger)
        self.redis = redis_client
        self.key = redis_key
        self.ts_key = ts_key
        self.json_fallback_to_string = json_fallback_to_string
        self._last_ts = None
        self._redis_json_available = None  # Кешируем результат проверки сервера
        self.use_redis_json = use_redis_json

        # Определяем тип клиента
        self.is_dgredis = self._is_dgredis_client(redis_client)
        self.is_async = self._is_async_client(redis_client)

        # Для dgredis проверка JSON не нужна - он всегда поддерживает JSON
        if self.is_dgredis:
            self._redis_json_available = True
            self.logger.info("Using dgredis client with native JSON support")
        elif self.use_redis_json and not self.is_async:
            # Для стандартного redis проверяем поддержку RedisJSON на сервере
            self._test_redis_json_server_support()

    def _is_dgredis_client(self, client) -> bool:
        """Определяет, является ли клиент dgredis"""
        if not HAS_DGREDIS:
            return False
        return isinstance(client, (dgredis.RedisClient, dgredis.AsyncRedisClient)) if dgredis else False

    def _is_async_client(self, client) -> bool:
        """Определяет, является ли клиент асинхронным"""
        if self.is_dgredis and dgredis:
            return isinstance(client, dgredis.AsyncRedisClient)
        else:
            return (hasattr(client, 'aget') or
                    'aioredis' in str(type(client)) or
                    'async' in str(type(client)).lower())

    def _test_redis_json_server_support(self) -> bool:
        """Проверяет поддержку RedisJSON модуля на Redis сервере (только для стандартного redis)"""
        if self._redis_json_available is not None or self.is_dgredis:
            return self._redis_json_available

        try:
            # Простая и надежная проверка - пробуем выполнить JSON.SET
            test_key = f"{self.key}:__json_test__"
            self.redis.execute_command("JSON.SET", test_key, "$", '{"test":true}')
            self.redis.delete(test_key)

            self._redis_json_available = True
            self.logger.info("RedisJSON module confirmed on server")

        except Exception as e:
            self.logger.warning(f"RedisJSON module not available on server: {e}. Falling back to string storage")
            self._redis_json_available = False
            self.use_redis_json = False

        return self._redis_json_available

    async def _test_redis_json_server_support_async(self) -> bool:
        """Проверяет поддержку RedisJSON модуля на Redis сервере (асинхронно, только для стандартного redis)"""
        if self._redis_json_available is not None or self.is_dgredis:
            return self._redis_json_available

        try:
            # Простая и надежная проверка - пробуем выполнить JSON.SET
            test_key = f"{self.key}:__json_test__"
            await self.redis.execute_command("JSON.SET", test_key, "$", '{"test":true}')
            await self.redis.delete(test_key)

            self._redis_json_available = True
            self.logger.info("RedisJSON module confirmed on server (async)")

        except Exception as e:
            self.logger.warning(f"RedisJSON module not available on server: {e}. Falling back to string storage")
            self._redis_json_available = False
            self.use_redis_json = False

        return self._redis_json_available

    def _can_use_json(self) -> bool:
        """Проверяет, можно ли использовать JSON формат"""
        if self.is_dgredis:
            return self.use_redis_json  # dgredis всегда поддерживает JSON
        else:
            return (self.use_redis_json and
                    self._redis_json_available is not False)

    async def _can_use_json_async(self) -> bool:
        """Проверяет, можно ли использовать JSON формат (асинхронно)"""
        if self.is_dgredis:
            return self.use_redis_json

        if not self.use_redis_json:
            return False

        if self._redis_json_available is None:
            await self._test_redis_json_server_support_async()

        return self._redis_json_available

    def _handle_dgredis_value(self, val):
        """Обрабатывает значение, полученное из dgredis"""
        if val is None:
            return {}

        if isinstance(val, dict):
            return val
        elif isinstance(val, (str, bytes)):
            if isinstance(val, bytes):
                val = val.decode('utf-8')
            try:
                return json.loads(val)
            except (json.JSONDecodeError, TypeError):
                return {'raw_value': val}
        else:
            return val if isinstance(val, dict) else {'value': val}

    def _handle_standard_value(self, val):
        """Обрабатывает значение, полученное из стандартного redis"""
        if not val:
            return {}

        if isinstance(val, bytes):
            val = val.decode('utf-8')

        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return {'raw_value': val}

    def _serialize_data_for_string(self, data: dict) -> str:
        """Сериализует данные в строку для обычного хранения"""
        return json.dumps(data, ensure_ascii=False)

    def load(self) -> dict:
        """Загружает конфигурацию из Redis"""
        if self.is_async:
            return self._load_async()
        else:
            return self._load_sync()

    def _load_sync(self) -> dict:
        """Синхронная загрузка"""
        try:
            if self.is_dgredis:
                return self._load_dgredis_sync()
            else:
                return self._load_standard_redis_sync()

        except Exception as e:
            self.logger.error(f'Error loading config from Redis: {e}')
            return {}

    def _load_dgredis_sync(self) -> dict:
        """Загрузка через dgredis (синхронно)"""
        if self._can_use_json():
            try:
                # Пробуем загрузить как JSON
                val = self.redis.get_json_key(self.key)
                if val is not None:
                    self._update_timestamp_sync()
                    self.logger.info('Config loaded successfully from dgredis (JSON)')
                    return val if isinstance(val, dict) else {}
            except Exception as e:
                self.logger.warning(f"Failed to load as JSON from dgredis: {e}")
                if not self.json_fallback_to_string:
                    raise

        # Загружаем как обычное значение (dgredis.get может возвращать dict)
        val = self.redis.get(self.key)
        self._update_timestamp_sync()
        result = self._handle_dgredis_value(val)
        self.logger.info('Config loaded successfully from dgredis (fallback)')
        return result

    def _load_standard_redis_sync(self) -> dict:
        """Загрузка через стандартный redis (синхронно)"""
        # Пытаемся загрузить как RedisJSON
        if self._can_use_json():
            try:
                val = self.redis.execute_command("JSON.GET", self.key, "$")
                if val:
                    # JSON.GET возвращает JSON строку, парсим её
                    result = json.loads(val)
                    # Результат в формате массива из-за JSONPath "$"
                    if isinstance(result, list) and len(result) > 0:
                        result = result[0]

                    if isinstance(result, dict):
                        self._update_timestamp_sync()
                        self.logger.info('Config loaded successfully from RedisJSON')
                        return result
            except Exception as e:
                self.logger.warning(f"Failed to load as RedisJSON: {e}")
                if not self.json_fallback_to_string:
                    raise
                # Если RedisJSON не сработал, отключаем его для будущих запросов
                self._redis_json_available = False
                self.use_redis_json = False

        # Загружаем как обычную строку
        val = self.redis.get(self.key)
        self._update_timestamp_sync()
        result = self._handle_standard_value(val)
        self.logger.info('Config loaded successfully from Redis (string format)')
        return result

    async def _load_async(self) -> dict:
        """Асинхронная загрузка"""
        try:
            if self.is_dgredis:
                return await self._load_dgredis_async()
            else:
                return await self._load_standard_redis_async()

        except Exception as e:
            self.logger.error(f'Error loading config from Redis: {e}')
            return {}

    async def _load_dgredis_async(self) -> dict:
        """Загрузка через dgredis (асинхронно)"""
        if await self._can_use_json_async():
            try:
                # Пробуем загрузить как JSON
                val = await self.redis.get_json_key(self.key)
                if val is not None:
                    await self._update_timestamp_async()
                    self.logger.info('Config loaded successfully from dgredis (JSON, async)')
                    return val if isinstance(val, dict) else {}
            except Exception as e:
                self.logger.warning(f"Failed to load as JSON from dgredis: {e}")
                if not self.json_fallback_to_string:
                    raise

        # Загружаем как обычное значение
        val = await self.redis.get(self.key)
        await self._update_timestamp_async()
        result = self._handle_dgredis_value(val)
        self.logger.info('Config loaded successfully from dgredis (fallback, async)')
        return result

    async def _load_standard_redis_async(self) -> dict:
        """Загрузка через стандартный redis (асинхронно)"""
        # Пытаемся загрузить как RedisJSON
        if await self._can_use_json_async():
            try:
                val = await self.redis.execute_command("JSON.GET", self.key, "$")
                if val:
                    result = json.loads(val)
                    if isinstance(result, list) and len(result) > 0:
                        result = result[0]

                    if isinstance(result, dict):
                        await self._update_timestamp_async()
                        self.logger.info('Config loaded successfully from RedisJSON (async)')
                        return result
            except Exception as e:
                self.logger.warning(f"Failed to load as RedisJSON: {e}")
                if not self.json_fallback_to_string:
                    raise
                # Если RedisJSON не сработал, отключаем его для будущих запросов
                self._redis_json_available = False
                self.use_redis_json = False

        # Загружаем как обычную строку
        val = await self.redis.get(self.key)
        await self._update_timestamp_async()
        result = self._handle_standard_value(val)
        self.logger.info('Config loaded successfully from Redis (async, string format)')
        return result

    def _update_timestamp_sync(self):
        """Обновляет timestamp синхронно"""
        if self.ts_key:
            ts = self.redis.get(self.ts_key)
            if ts is not None:
                if isinstance(ts, bytes):
                    ts = ts.decode('utf-8')
                self._last_ts = ts

    async def _update_timestamp_async(self):
        """Обновляет timestamp асинхронно"""
        if self.ts_key:
            ts = await self.redis.get(self.ts_key)
            if ts is not None:
                if isinstance(ts, bytes):
                    ts = ts.decode('utf-8')
                self._last_ts = ts

    def save(self, data: dict):
        """Сохраняет конфигурацию в Redis"""
        if self.is_async:
            return self._save_async(data)
        else:
            return self._save_sync(data)

    def _save_sync(self, data: dict):
        """Синхронное сохранение"""
        try:
            if self.is_dgredis:
                self._save_dgredis_sync(data)
            else:
                self._save_standard_redis_sync(data)

            # Обновляем timestamp
            if self.ts_key:
                import time
                timestamp = str(int(time.time()))
                self.redis.set(self.ts_key, timestamp)
                self._last_ts = timestamp

        except Exception as e:
            self.logger.error(f'Error saving config to Redis: {e}')
            raise

    def _save_dgredis_sync(self, data: dict):
        """Сохранение через dgredis (синхронно)"""
        if self._can_use_json():
            try:
                self.redis.set_json_key(self.key, data)
                self.logger.info('Config saved successfully to dgredis (JSON)')
                return
            except Exception as e:
                self.logger.warning(f"Failed to save as JSON to dgredis: {e}")
                if not self.json_fallback_to_string:
                    raise

        # Сохраняем как строку
        serialized_data = self._serialize_data_for_string(data)
        self.redis.set(self.key, serialized_data)
        self.logger.info('Config saved successfully to dgredis (string format)')

    def _save_standard_redis_sync(self, data: dict):
        """Сохранение через стандартный redis (синхронно)"""
        saved_as_json = False

        # Пытаемся сохранить как RedisJSON
        if self._can_use_json():
            try:
                json_str = json.dumps(data, ensure_ascii=False)
                self.redis.execute_command("JSON.SET", self.key, "$", json_str)
                saved_as_json = True
                self.logger.info('Config saved successfully to RedisJSON')
            except Exception as e:
                self.logger.warning(f"Failed to save as RedisJSON: {e}")
                if not self.json_fallback_to_string:
                    raise
                # Отключаем RedisJSON для будущих операций
                self._redis_json_available = False
                self.use_redis_json = False

        # Сохраняем как строку, если JSON не сработал или отключен
        if not saved_as_json:
            serialized_data = self._serialize_data_for_string(data)
            self.redis.set(self.key, serialized_data)
            self.logger.info('Config saved successfully to Redis (string format)')

    async def _save_async(self, data: dict):
        """Асинхронное сохранение"""
        try:
            if self.is_dgredis:
                await self._save_dgredis_async(data)
            else:
                await self._save_standard_redis_async(data)

            # Обновляем timestamp
            if self.ts_key:
                import time
                timestamp = str(int(time.time()))
                await self.redis.set(self.ts_key, timestamp)
                self._last_ts = timestamp

        except Exception as e:
            self.logger.error(f'Error saving config to Redis: {e}')
            raise

    async def _save_dgredis_async(self, data: dict):
        """Сохранение через dgredis (асинхронно)"""
        if await self._can_use_json_async():
            try:
                await self.redis.set_json_key(self.key, data)
                self.logger.info('Config saved successfully to dgredis (JSON, async)')
                return
            except Exception as e:
                self.logger.warning(f"Failed to save as JSON to dgredis: {e}")
                if not self.json_fallback_to_string:
                    raise

        # Сохраняем как строку
        serialized_data = self._serialize_data_for_string(data)
        await self.redis.set(self.key, serialized_data)
        self.logger.info('Config saved successfully to dgredis (string format, async)')

    async def _save_standard_redis_async(self, data: dict):
        """Сохранение через стандартный redis (асинхронно)"""
        saved_as_json = False

        # Пытаемся сохранить как RedisJSON
        if await self._can_use_json_async():
            try:
                json_str = json.dumps(data, ensure_ascii=False)
                await self.redis.execute_command("JSON.SET", self.key, "$", json_str)
                saved_as_json = True
                self.logger.info('Config saved successfully to RedisJSON (async)')
            except Exception as e:
                self.logger.warning(f"Failed to save as RedisJSON: {e}")
                if not self.json_fallback_to_string:
                    raise
                # Отключаем RedisJSON для будущих операций
                self._redis_json_available = False
                self.use_redis_json = False

        # Сохраняем как строку, если JSON не сработал или отключен
        if not saved_as_json:
            serialized_data = self._serialize_data_for_string(data)
            await self.redis.set(self.key, serialized_data)
            self.logger.info('Config saved successfully to Redis (string format, async)')

    def has_changed(self) -> bool:
        """Проверяет, изменилась ли конфигурация"""
        if not self.auto_reload or not self.ts_key:
            return False

        if self.is_async:
            return self._has_changed_async()
        else:
            return self._has_changed_sync()

    def _has_changed_sync(self) -> bool:
        """Синхронная проверка изменений"""
        try:
            ts = self.redis.get(self.ts_key)
            if isinstance(ts, bytes):
                ts = ts.decode('utf-8')

            changed = ts != self._last_ts
            if changed:
                self._last_ts = ts
            return changed

        except Exception as e:
            self.logger.error(f'Error checking if config changed: {e}')
            return False

    async def _has_changed_async(self) -> bool:
        """Асинхронная проверка изменений"""
        try:
            ts = await self.redis.get(self.ts_key)
            if isinstance(ts, bytes):
                ts = ts.decode('utf-8')

            changed = ts != self._last_ts
            if changed:
                self._last_ts = ts
            return changed

        except Exception as e:
            self.logger.error(f'Error checking if config changed: {e}')
            return False

    def get_storage_info(self) -> dict:
        """Возвращает информацию о способе хранения данных"""
        storage_format = 'Unknown'

        if self.is_dgredis:
            storage_format = 'dgredis JSON' if self.use_redis_json else 'dgredis String'
        else:
            if self.use_redis_json and self._redis_json_available:
                storage_format = 'RedisJSON'
            else:
                storage_format = 'String'

        return {
            'use_redis_json': self.use_redis_json,
            'redis_json_server_available': self._redis_json_available,
            'json_fallback_enabled': self.json_fallback_to_string,
            'storage_format': storage_format,
            'is_dgredis': self.is_dgredis
        }

    def get_client_info(self) -> dict:
        """Возвращает информацию о типе Redis клиента и способе хранения"""
        return {
            'is_dgredis': self.is_dgredis,
            'is_async': self.is_async,
            'client_type': type(self.redis).__name__,
            'client_module': type(self.redis).__module__,
            'has_dgredis_module': HAS_DGREDIS,
            **self.get_storage_info()
        }

    def force_string_mode(self):
        """Принудительно переключает в режим строкового хранения"""
        self.use_redis_json = False
        if not self.is_dgredis:
            self._redis_json_available = False
        self.logger.info("Forced switch to string storage mode")

    def retry_json_mode(self):
        """Пытается повторно включить режим JSON"""
        if not self.use_redis_json:
            self.use_redis_json = True

            if self.is_dgredis:
                self.logger.info("dgredis JSON mode enabled")
            else:
                self._redis_json_available = None

                if self.is_async:
                    self.logger.info("RedisJSON mode enabled, will test on next operation")
                else:
                    success = self._test_redis_json_server_support()
                    if success:
                        self.logger.info("Successfully switched to RedisJSON mode")
                    else:
                        self.logger.warning("Failed to switch to RedisJSON mode")

    def clear_config(self):
        """Удаляет конфигурацию из Redis"""
        if self.is_async:
            return self._clear_config_async()
        else:
            return self._clear_config_sync()

    def _clear_config_sync(self):
        """Синхронное удаление конфигурации"""
        try:
            deleted = self.redis.delete(self.key)
            if self.ts_key:
                self.redis.delete(self.ts_key)
                self._last_ts = None

            self.logger.info(f'Config cleared from Redis (deleted: {deleted})')
            return deleted > 0

        except Exception as e:
            self.logger.error(f'Error clearing config from Redis: {e}')
            return False

    async def _clear_config_async(self):
        """Асинхронное удаление конфигурации"""
        try:
            deleted = await self.redis.delete(self.key)
            if self.ts_key:
                await self.redis.delete(self.ts_key)
                self._last_ts = None

            self.logger.info(f'Config cleared from Redis (deleted: {deleted}, async)')
            return deleted > 0

        except Exception as e:
            self.logger.error(f'Error clearing config from Redis: {e}')
            return False

    def exists(self) -> bool:
        """Проверяет, существует ли конфигурация в Redis"""
        if self.is_async:
            return self._exists_async()
        else:
            return self._exists_sync()

    def _exists_sync(self) -> bool:
        """Синхронная проверка существования"""
        try:
            return bool(self.redis.exists(self.key))
        except Exception as e:
            self.logger.error(f'Error checking config existence: {e}')
            return False

    async def _exists_async(self) -> bool:
        """Асинхронная проверка существования"""
        try:
            return bool(await self.redis.exists(self.key))
        except Exception as e:
            self.logger.error(f'Error checking config existence: {e}')
            return False
