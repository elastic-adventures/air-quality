from datetime import datetime
from elasticsearch import Elasticsearch

es = Elasticsearch(['127.0.0.1:9200'])

search_query = {
    "query": {
        "range": {
            "value": {
                "gte": 1
            }
        }
    },
    "aggs": {
        "days": {
            "date_histogram": {
                "field": "@timestamp",
                "interval": "day",
                "time_zone": "+08:00"
            },
            "aggs": {
                "pm25": {
                    "stats": {
                        "field": "value"
                    }
                }
            }
        }
    },
    "size": 0
}
res = es.search(index='air_quality', body=search_query)

index_name = 'air_quality_days'
index_type = 'data'
es.indices.delete(index=index_name, ignore=[400, 404])

for info in res['aggregations']['days']['buckets']:
    cur_date = datetime.strptime(info['key_as_string'], '%Y-%m-%dT%H:%M:%S.%f+08:00')
    new_doc = {
        "@timestamp": info['key_as_string'],
        'year': cur_date.year,
        'month': cur_date.month,
        'day': cur_date.day,
        "value_max": info['pm25']['max'],
        "value_avg": info['pm25']['avg'],
        "value_min": info['pm25']['min'],
    }
    es.index(index=index_name, doc_type=index_type, id=new_doc['@timestamp'], body=new_doc)
    print new_doc
