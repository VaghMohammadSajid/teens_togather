def filter_utils(filter_dict,queryset,obj):
    for key,value in filter_dict.items():
            
            new_dict = {
                value:obj.request.query_params.get(key, None)
            }
            
            if obj.request.query_params.get(key, None):
                queryset  = queryset.filter(**new_dict)

    return queryset