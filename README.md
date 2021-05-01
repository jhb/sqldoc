# sqldoc

A document database in python, using a sql backend.

Handles dicts/list/scalar combinations of arbitrary depth (think json documents).

## Why, o why?

For my own experiments I need a document storage, that allows me the following:

- store documents completely schema free
- allow retrieval of said documents
- schema free indexing of the documents - e.g. I don't want to handle indexing, just index
  everything
- use database functionality on the values - e.g. still being able to concat strings etc.
- fulltext search, that actually works (am at looking at you, neo4j)
- multi document transactions
- potentially attribute level security - it would be great if I could fine tune access rights on the
  permissions of every object on every attribute
- easy to set up and run on "cheap" hosting setups
- open source

The background is that I like information management systems, and need a backend where I have lots of freedom to experiment. Especially I want to be able to build a graph on top the backend. My requirement is not to scale to infinity, but full flexibility on a small to medium level (whatever that means).

## Why not <foo>?

I considered the following alternatives:

- neo4j - has some form of schema (labels for nodes, types for edges), has quite some issues when it comes to indexing and searching, is java, e.g. no cheap setups, is only half open source. Funny problems with transactions.
- mongodb - you need some form of schema for indexing, not available on standard cheap setups, not really that open source. Not sure about the transaction support.
- zodb - is of course fantastic, but lacks in the indexing and fulltext search department. Hard to debug if you run into problems (e.g. PosKeyErrors).
- ... - others usually have one or more of the above problems:
  - good, well tested transaction support,
  - good, well tested indexing and/or fulltext support
  - not easily available on cheap setups
  
## Because I can

The main reason is that I want to play around with the idea of a generic 'safe-everything' SQL Storage. 

