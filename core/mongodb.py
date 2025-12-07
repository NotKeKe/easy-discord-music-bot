from montydb import MontyClient, set_storage, MontyDatabase, MontyCollection, MontyCursor
from asyncio import to_thread
from typing import Optional, Any

from .config import DB_PATH

set_storage(
    str(DB_PATH),
    'sqlite',
    # sqlite pragma
    journal_mode="WAL",
    # sqlite connection option
    check_same_thread=False,
)

mongo_db_client = MontyClient(
    str(DB_PATH),
    synchronous=1, # 0 or 1 or 2, higher number means more safer, but lower performance(speed)
    automatic_index=True,
    busy_timeout=10000 # wait 10 seconds
)

class MongoDB_DB:
    music = mongo_db_client['music']

async def list_database_names():
    return await to_thread(mongo_db_client.list_database_names)

async def list_collection_names(db: MontyDatabase):
    return await to_thread(db.list_collection_names)

async def find_one_and_update(
        collection: MontyCollection, 
        filter: dict, 
        update: dict,
        return_document: Optional[bool] = None,
        upsert: Optional[bool] = None,
        **kwargs
    ):
    return await to_thread(
        collection.find_one_and_update,
        filter=filter,
        update=update,
        **({'return_document': return_document} if return_document else {}),
        **({'upsert': upsert} if upsert else {}),
        **kwargs
    )

async def find_one(collection: MontyCollection, filter: dict, **kwargs):
    return await to_thread(
        collection.find_one,
        filter=filter,
        **kwargs
    )

async def find(collection: MontyCollection, filter: dict, **kwargs) -> Any:
    def _find(collection: MontyCollection, filter: dict, **kwargs): 
        cursor = collection.find(filter, **kwargs)
        items = [item for item in cursor]
        return items

    return await to_thread(
        _find,
        collection,
        filter=filter,
        **kwargs
    )

async def insert_one(collection: MontyCollection, document: dict, **kwargs):
    return await to_thread(
        collection.insert_one,
        document=document,
        **kwargs
    )

async def delete_one(collection: MontyCollection, filter: dict, **kwargs):
    return await to_thread(
        collection.delete_one,
        filter=filter,
        **kwargs
    )

async def delete_many(collection: MontyCollection, filter: dict, **kwargs):
    return await to_thread(
        collection.delete_many,
        filter=filter,
        **kwargs
    )

async def update_one(collection: MontyCollection, filter: dict, update: dict, upsert: bool = False, **kwargs):
    return await to_thread(
        collection.update_one,
        filter=filter,
        update=update,
        upsert=upsert,
        **kwargs
    )

async def update_many(collection: MontyCollection, filter: dict, update: dict, **kwargs):
    return await to_thread(
        collection.update_many,
        filter=filter,
        update=update,
        **kwargs
    )

async def count_documents(collection: MontyCollection, filter: dict, **kwargs):
    return await to_thread(
        collection.count_documents,
        filter=filter,
        **kwargs
    )

async def distinct(collection: MontyCollection, key: str, filter: dict, **kwargs):
    return await to_thread(
        collection.distinct,
        key=key,
        filter=filter,
        **kwargs
    )