import sys


COD_ERROR = {'invalid_value': 0001}


class FieldsValidator():

    @staticmethod
    def validate_autofield(field, value_field):
        obj = {}
        try:
            val = int(value_field)
            if val < 1 or val > sys.maxsize:
                obj['code'] = COD_ERROR['invalid_value']
                obj['message'] = "El campo " + field + " esta fuera de rango [1:" + str(sys.maxsize)+"]"
        except ValueError:
            obj['code'] = COD_ERROR['invalid_value']
            obj['message'] = "El campo " + field.name + " debe ser entero positivo"

        return obj

    @staticmethod
    def validate_bigautofield(field, value_field):
        obj = {}
        try:
            val = int(value_field)
            if val < 1 or val > 9223372036854775807:
                obj['message'] = "El campo " + field.name + " esta fuera de rango [1:9223372036854775807]"
                obj['code'] = COD_ERROR['invalid_value']
        except ValueError:
            obj['message'] = "El campo " + field.name + " debe ser entero positivo"
            obj['code'] = COD_ERROR['invalid_value']

        return obj

    @staticmethod
    def validate_integerfield(field, value_field):
        obj = {}
        try:
            val = int(value_field)
            if val < (-1 * (sys.maxsize - 1)) or val > sys.maxsize:
                obj['message'] = "El campo " + field.name + " esta fuera de rango ["+(-1 * (sys.maxsize - 1))+":"+str(sys.maxsize)+"]"
                obj['code'] = COD_ERROR['invalid_value']
        except ValueError:
            obj['message'] = "El campo " + field.name + " debe ser entero"
            obj['code'] = COD_ERROR['invalid_value']

        return obj

    @staticmethod
    def validate_positiveintegerfield(field, value_field):
        obj = {}
        try:
            val = int(value_field)
            if val < 0 or val > sys.maxsize:
                obj['message'] = "El campo " + field.name + " esta fuera de rango [0:" + str(sys.maxsize)+"]"
                obj['code'] = COD_ERROR['invalid_value']
        except ValueError:
            obj['message'] = "El campo " + field.name + " debe ser entero"
            obj['code'] = COD_ERROR['invalid_value']

        return obj

    @staticmethod
    def validate_bigintegerfield(field, value_field):
        obj = {}
        try:
            val = int(value_field)
            if val < -9223372036854775808 or val > 9223372036854775807:
                obj['message'] = "El campo " + field.name + " esta fuera de rango [-9223372036854775808:9223372036854775807]"
                obj['code'] = COD_ERROR['invalid_value']
        except ValueError:
            obj['message'] = "El campo " + field.name + " debe ser entero"
            obj['code'] = COD_ERROR['invalid_value']

        return obj

    @staticmethod
    def validate_charfield(field, value_field):
        obj = {}
        if field.max_length < len(value_field):
            obj['message'] = value_field + " supera la longitud maxima del campo " + field.name + "."
            obj['code'] = COD_ERROR['invalid_value']

        return obj

    @staticmethod
    def validate_textfield(field, value_field):
        obj = {}
        if field.max_length is not None:
            if field.max_length < len(value_field):
                obj['message'] = value_field + " supera la longitud maxima del campo " + field.name + "."
                obj['code'] = COD_ERROR['invalid_value']

        return obj

    @staticmethod
    def validate_datetimefield(field, value_field):
        obj = {}
        fechas_split = value_field.split('/')
        if len(fechas_split) != 3:
            obj['message'] = "El campo " + field.name + " debe tener el formato DD/MM/YYYY."
            obj['code'] = COD_ERROR['invalid_value']
        else:
            if not fechas_split[0].isnumeric() or not fechas_split[1].isnumeric() or not fechas_split[2].isnumeric():
                obj['message'] = "El campo " + field.name + " debe tener el formato DD/MM/YYYY."
                obj['code'] = COD_ERROR['invalid_value']

        return obj

    @staticmethod
    def validate_booleanfield(field, value_field):
        obj = {}
        if not value_field.lower() == 'true' or not value_field.lower() == 'false':
            obj['message'] = "El campo " + field.name + " debe ser True o False."
            obj['code'] = COD_ERROR['invalid_value']

        return obj

    @staticmethod
    def validation_field(field, value_field, model):

        try:
            # Busca el campo a validar dentro del modelo principal
            field_model = model._meta.get_field(field)
        except:
            # Busca recursivamente el campo a validar
            # dentro de los modelos relacionados
            field_split = field.split("__")
            for x in range(0, len(field_split) - 1):
                model = model.relation_field(field_split[x])
            field_model = model._meta.get_field(field_split[len(field_split) - 1])

        field_filter_type = field_model.get_internal_type()

        obj = {}

        if field_filter_type == 'AutoField':
            obj = FieldsValidator.validate_autofield(field_model, value_field)

        elif field_filter_type == 'BigAutoField':
            obj = FieldsValidator.validate_bigautofield(field_model, value_field)

        elif field_filter_type == 'IntegerField':
            obj = FieldsValidator.validate_integerfield(field_model, value_field)

        elif field_filter_type == 'PositiveIntegerField':
            obj = FieldsValidator.validate_positiveintegerfield(field_model, value_field)

        elif field_filter_type == 'BigIntegerField':
            obj = FieldsValidator.validate_bigintegerfield(field_model, value_field)

        elif field_filter_type == 'CharField':
            obj = FieldsValidator.validate_charfield(field_model, value_field)

        elif field_filter_type == 'TextField':
            obj = FieldsValidator.validate_textfield(field_model, value_field)

        elif field_filter_type == 'DateTimeField':
            obj = FieldsValidator.validate_datetimefield(field_model, value_field)

        elif field_filter_type == 'BooleanField':
            obj = FieldsValidator.validate_booleanfield(field_model, value_field)

        # TypeField faltantes de validacion:

        # BinaryField
        # CommaSeparatedIntegerField
        # DateField
        # DecimalField
        # DurationField
        # EmailField
        # FileField
        # FilePathField
        # FloatField
        # ImageField
        # GenericIPAddressField
        # NullBooleanField
        # PositiveSmallIntegerField
        # SlugField
        # SmallIntegerField
        # TimeField
        # URLField
        # UUIDField

        return obj

    @staticmethod
    def validation_parameter(query_data, model):

        error = []

        for field_filter in query_data:
            obj = FieldsValidator.validation_field(
                field_filter,
                query_data[field_filter],
                model)

            if len(obj):
                error.append(obj)

        return error
