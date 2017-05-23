import re

from fieldsvalidator import FieldsValidator


class URLParser(object):

    def get_query(self, request, *args, **kwargs):
        parameters = self.check_url(request, self.model)

        error = FieldsValidator.validation_parameter(
            parameters["filter"]["query_data"],
            self.model)

        if error:
            self.message_error = error
            return False
        else:
            collection = self.resolve_query(parameters, self.model)
            self.parameter_method_json = parameters["fields"]["fields_exist"]
            if self.parameter_method_json:
                self.method_json = "as_json_fields"
            return collection

    def resolve_query(self, parameters, model):
        queryset = model.objects.filter(**parameters["filter"]["query_data"])
        queryset = queryset.order_by(*parameters["sort"]["query_data"])
        return queryset

    def check_fields(self, fields, model_fields):
        obj_fields = {"fields_exist": None,
                      "fields_not_exist": None,
                      "query_data": None
                      }
        fields_exist = []
        fields_not_exist = []
        query_data = []
        for field in fields:
            if field in model_fields.keys():
                fields_exist.append(field)
                query_data.append(model_fields[field])
            else:
                fields_not_exist.append(field)
        if len(fields_exist) > 0:
            obj_fields["fields_exist"] = fields_exist
        if len(fields_not_exist) > 0:
            obj_fields["fields_not_exist"] = fields_not_exist
        if len(query_data) > 0:
            obj_fields["query_data"] = query_data
        return obj_fields

    def check_sort(self, fields, model_fields):
        obj_sort = {"sorts_exist": [], "sorts_not_exist": [], "query_data": []}
        for sort in fields:
            if sort[:1] == "-":
                if sort[1:] in model_fields.keys():
                    obj_sort["sorts_exist"].append(sort)
                    obj_sort["query_data"].append("-" + model_fields[sort[1:]])
                else:
                    obj_sort["sorts_not_exist"].append(sort)
            else:
                if sort in model_fields.keys():
                    obj_sort["sorts_exist"].append(sort)
                    obj_sort["query_data"].append(model_fields[sort])
                else:
                    obj_sort["sorts_not_exist"].append(sort)
        return obj_sort

    def check_filter(self, filters, model_fields):
        obj_filter = {
            "filters_exist": [], "filters_not_exist": [], "query_data": {}
        }
        operadores = {
            '>=': '__gte',
            '<=': '__lte',
            '<': '__lt',
            '>': '__gt',
            '=*': '__icontains'
        }
        query_data = {}
        for fil in filters:
            reg = re.search('([a-zA-Z-_\.]+)(=\*|>=|<=|=|<|>)(.+)', fil)
            field, oper, value = reg.groups()
            if field in model_fields.keys():
                obj_filter["filters_exist"].append(field)
                field = model_fields[field]
                if oper == '=':
                    query_data[field] = value
                else:
                    query_data[field + operadores[oper]] = value
            else:
                obj_filter["filters_not_exist"].append(field)
        obj_filter["query_data"] = query_data
        return obj_filter

    def check_url(self, request, model):
        # model_fields = [f.name for f in model._meta.fields]
        model_fields = model.fields()
        parameters = {
            "fields": {
                "fields_exist": None,
                "fields_not_exist": None,
                "query_data": None
            },
            "filter": {
                "filters_exist": [], "filters_not_exist": [], "query_data": {}
            },
            "sort": {"sorts_exist": [],
                     "sorts_not_exists": [],
                     "query_data": []}
        }
        # FIELDS
        if request.GET.get('fields', None):
            fields = request.GET.get('fields').split(',')
            parameters["fields"] = self.check_fields(fields, model_fields)
        # SORTS
        if request.GET.get('sort', None):
            sorts = request.GET.get('sort').split(',')
            parameters["sort"] = self.check_sort(sorts, model_fields)
        # FILTERS
        if request.GET.get('filter', None):
            filters = request.GET.get('filter').split(',')
            parameters["filter"] = self.check_filter(filters, model_fields)
        # print parameters
        return parameters
