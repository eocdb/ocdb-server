# OC-DB RESTful API

## Querying measurements

Path: `api/measurements`

Parameters

* `q` or `query`: query string using a [Lucene-like syntax](https://github.com/bcdev/eocdb-server/blob/master/docs/query-syntax.md).
* `region`: bounding box of the form `<lon_min>,<lat_min>,<lon_max>,<lat_max>` 
   or geometry WKT using [WGS-84](http://spatialreference.org/ref/epsg/wgs-84/) coordinates.
* `period`: time range of the form `<start_time>,<end_time>`. 
  Uses [ISO formatted](https://en.wikipedia.org/wiki/ISO_8601) UTC times.
* `format` or `f`: result format possible values include
  - `json` - plain, UTF8-encoded text, JSON-formatted. Mime type will be `application/json`. This is the default.
  - `geojson` - plain, UTF8-encoded text, GeoJSON-formatted. Mime type will be `application/geojson`. This is the default.
  - `csv` - plain, UTF8-encoded text, CSV-formatted. Mime type will be `text/csv`. This is the default.
  - `excel` - binary Excel file. Mime type is `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.
              Download location JSON-formatted.
* `index`: 1-based index of the first record to be retrieved.
* `results`: Maximum number of records.
