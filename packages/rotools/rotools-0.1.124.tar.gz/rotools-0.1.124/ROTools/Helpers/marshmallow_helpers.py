from ROTools.Helpers.DictObj import DictObj



def parse_marshmallow(schema, request):
    from flask import jsonify
    from marshmallow import ValidationError
    try:
        data = schema.load(request.form if request.form else request.get_json())
        return DictObj(data)
    except ValidationError as err:
        return jsonify({"error": "Invalid data", "messages": err.messages}), 400
