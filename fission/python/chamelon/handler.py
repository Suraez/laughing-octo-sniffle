import time
import six
import json
from chameleon import PageTemplate

BIGTABLE_ZPT = """
<table xmlns="http://www.w3.org/1999/xhtml"
       xmlns:tal="http://xml.zope.org/namespaces/tal">
<tr tal:repeat="row options['table']">
  <td tal:repeat="c python: row.values()">
    <span tal:define="d python: c + 1"
          tal:attributes="class python: 'column-' + str(d)"
          tal:content="python: d" />
  </td>
</tr>
</table>
"""

def main(input=None):
    try:
        data = json.loads(input.get("body", "{}"))
        num_of_rows = int(data.get('num_of_rows', 5))
        num_of_cols = int(data.get('num_of_cols', 3))
    except Exception:
        num_of_rows = 5
        num_of_cols = 3

    start = time.time()

    tmpl = PageTemplate(BIGTABLE_ZPT)
    row_data = {str(i): i for i in range(num_of_cols)}
    table = [row_data for _ in range(num_of_rows)]
    options = {'table': table}

    rendered = tmpl.render(options=options)
    latency = time.time() - start

    return {
        "statusCode": 200,
        "body": json.dumps({
            "latency": latency,
            "html": rendered
        }),
        "headers": {
            "Content-Type": "application/json"
        }
    }


if __name__ == "__main__":
    print(handler(None))