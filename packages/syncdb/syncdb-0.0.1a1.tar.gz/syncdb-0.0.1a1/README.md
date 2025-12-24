# SyncDB

WARNING: THIS IS A WORK IN PROGRESS NOT READY YET. Please don't use it!

SyncDB is a synchronized engine built to communicate database changes to the client in realtime.

It currently wraps around a SQLAlchemy Model system and propagate changes.

The library handles the following :

 * Serialization of database model
 * Attribute state watching


To come:

 * Watching computed properties
 * Separating from the SQLAlchemy library (but keeping a compatible system)