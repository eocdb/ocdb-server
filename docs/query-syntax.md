# OC-DB Query Syntax

## Query Strings

A query string can be a single term or word or a phrase, comprising multiple search terms or words.

The syntax is best explained by examples.

### Default queries

The next examples are queries that are performed on the default attribute (or on attributes) of a given data table.
Such attributes could be "title" or "description". Therefore the phrase *searches for all records that contain XXX*
in the following example actually means *searches for all records whose "title" or "description"
attribute values contain XXX*.

The query string

* `chl` searches for all records that contain the word "chl", ignoring letter case;
* `"Chl A"` searches for all records that contain the words "Chl" and "A" which must occur in this order;
* `chl kd*48?` searches for all records that either contain the word "chl" or that match the wildcard "kd*48?".

The next examples are queries that are performed on specified attributes of a given data table.

### Field queries

The query string

* `chl:[4 TO 20]` searches for all records whose values of "chl" attribute are between 4 and 20;
* ...

### Complex queries

The query string

* `chl:(4 OR 20)`
* ...


## Formal Syntax

    Term := ListTerm
    ListTerm := {OrTerm}
    OrTerm := AndTerm "OR" OrTerm
    AndTerm := UnaryTerm "AND" OrTerm
    UnaryTerm := "+" Term | "-" Term | PrimaryTerm
    PrimaryTerm := [Name ":"] TextTerm | "(" Term ")"
    TextTerm := WildCard | Text | "<Text>"

## References

* https://github.com/Esri/geoportal-server/wiki/Using-Lucene-Search-Text-Queries
* https://www.oclc.org/developer/develop/worldshare-platform/architecture/query-syntax.en.html
* http://www.opensearchserver.com/documentation/api_v2/search_parameters/README.md


