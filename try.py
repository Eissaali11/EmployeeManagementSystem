{% block title %}
    {% if force_mode == 'return' %}
        نموذج استلام مركبة - {{ vehicle.plate_number }}
    {% else %}
        نموذج تسليم مركبة - {{ vehicle.plate_number }}
    {% endif %}
{% endblock %}

...

