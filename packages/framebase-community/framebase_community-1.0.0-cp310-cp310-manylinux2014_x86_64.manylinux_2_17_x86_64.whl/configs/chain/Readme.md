# global config list

metric_router_v1.json : 
    - 
metric_query_intent_v1.json: remove sorting, comparison, limit, offset

metric_query_intent_version:
    - metric_query_intent.json
    - metric_query_intent_v1.json

metric_router_version:
    - metric_router.json
    - metric_router_v1.json
table_max_length:
    - '4096'
metric_pick_mode:
    - 'single'
    - 'multiple'
metric_dimension_warning_mode:
    - 'all'
    - 'only_abnormal_metric_message'
    - 'abnormal_metric_and_dimension_message'
    - 'none'
metric_dimension_analysis_mode:
    - 'one by one'
metric_time_records_mapping_mode:
    - 'fixed'
    - 'adaptive'

