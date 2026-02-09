from decimal import Decimal

from jinja2 import Template
from weasyprint import HTML

DOC_TEMPLATE = Template(
    """
<!doctype html><html><head><meta charset="utf-8">
<style>
body{font-family:Arial,sans-serif;font-size:12px;margin:30px}
h1{font-size:18px;margin:0 0 4px 0}
table{width:100%;border-collapse:collapse;margin-top:12px}
th,td{border:1px solid #ddd;padding:6px}
th{background:#f5f5f5;text-align:left}
.right{text-align:right}
.small{color:#666;font-size:11px}
.total-row{font-weight:bold;font-size:14px}
</style></head><body>

<h1>{{ title }} {{ number }}</h1>
<div class="small">Date: {{ date }}</div>
<div style="margin-top:6px">Partner: <strong>{{ partner_name }}</strong></div>

<table>
<thead><tr>
<th>#</th>
<th>Description</th><th class="right">Qty</th><th>Unit</th>
<th class="right">Unit Price</th><th class="right">Line Total</th>
</tr></thead>
<tbody>
{% for ln in lines %}
<tr>
<td>{{ loop.index }}</td>
<td>{{ ln.description }}</td>
<td class="right">{{ "%.3f"|format(ln.qty) }}</td>
<td>{{ ln.unit }}</td>
<td class="right">{{ "%.4f"|format(ln.unit_price) }} {{ currency }}</td>
<td class="right">{{ "%.4f"|format(ln.line_total) }} {{ currency }}</td>
</tr>
{% endfor %}
</tbody></table>

<p class="total-row right">Total: {{ "%.4f"|format(total) }} {{ currency }}</p>

{% if notes %}
<p><b>Notes:</b> {{ notes }}</p>
{% endif %}

</body></html>
"""
)


def render_doc_pdf(
    title: str,
    number: str,
    date,
    partner_name: str,
    currency: str,
    notes: str | None,
    raw_lines,
) -> bytes:
    lines = []
    total = Decimal("0")
    for ln in raw_lines:
        qty = Decimal(str(ln.qty))
        up = Decimal(str(ln.unit_price))
        lt = qty * up
        total += lt
        lines.append(
            {
                "description": ln.description,
                "qty": float(qty),
                "unit": ln.unit,
                "unit_price": float(up),
                "line_total": float(lt),
            }
        )

    html = DOC_TEMPLATE.render(
        title=title,
        number=number,
        date=date,
        partner_name=partner_name,
        currency=currency,
        notes=notes,
        lines=lines,
        total=float(total),
    )
    return HTML(string=html).write_pdf()
