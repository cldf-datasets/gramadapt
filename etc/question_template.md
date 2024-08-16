{% if not codes_only %}{{ ctx.cldf.name }}{% endif %}
{% for code in ctx.codes %}{% if code.cldf.name != 'B' %}
- {{ code.cldf.name }}
{% endif %}{% endfor %}