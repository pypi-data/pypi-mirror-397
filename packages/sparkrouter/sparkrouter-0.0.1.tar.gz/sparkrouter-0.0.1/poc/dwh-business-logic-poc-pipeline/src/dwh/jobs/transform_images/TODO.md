# TransformImage TODO

* Add Functional tests for dropped records, 0 records extracted

Clean up source and sink logic - make configuration driven

Setup Elasticsearch server for image metadata indexing (terraform)

Setup SNS listener to populate elasticsearch with job metrics (python lambda + terraform)

Setup elasticsearch dashboard for job performance

Setup example listener for dropped images files and trigger transform job