# Created constants for the HTML templates.
ICON_PLACEHOLDER = '<span class="notification-icon"> </span>'

# Define a template for the notification.
NOTIFICATION_TEMPLATE = '<span class="notification-icon" data-id="{counter}">{icon}</span>'

# Define a template for the highlighted line.
CODE_LINE_TEMPLATE = """
    <div class="code-line">
        {line_number}
        <div class="notification">{notification}</div>
        <div class="highlighted-line">{highlighted_line}</div>
    </div>
"""
# Define a template for the function API.
FUNCTION_API_TEMPLATE = """
    <div id="detail-{counter}" class="detail-page">
        {details}
    </div>
"""
SEPARATOR = "<br><hr>"

# Define a dictionary of icons for different types of notifications.
ICON_TYPE = {
    "NO_ACTION": '<img class="icon" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAAAXNSR0IArs4c6QAABs5JREFUeF7tnVXIdUUUhp8fFOzAurBQDDBuVLBbsAO7GxMb7G4FG5Pf7sQOsFtQbwwwUKwLCztAQfcr+4Pj8exZa8ecOVtm3XwXe82aNe+7Zs3Mmv3tM40sSRGYlrT33DmZgMRBkAnIBCRGIHH3eQZkAhIjkLj7ccyA7YC7E4+zaffRfY9NwAnAmcBcwA9NURjRbj9gDWDN8tkLwIvANR32MSfwPXAicFaHdv9lKiYBNwK7l73dCuza0SBeB1assPUGsFJH/dwC7FLaugnYoyO7YyHgZWDVIYdFgIhoI3cBSgshUbrbvk0nJfAiYFBeAVZrafc/zWPMgG+AeUY4+guwCvB2w0HsBigSPaKZd7NHcYTOcsCrwKwjnn0LzNvQ7shmXRPwCbBIwME7gJ0aDsAT/VOm28yC24EdAz5+CizacAxRZ4DSy84Ox44DznXoDat8BizkbPc5sLBTd1DtWOAcR7vbBtYHh3q1SlczQKCe7fTkTiPCqsz85bQ/pdZkbJqhOzj7Od5JVtBcEyeHDWpLeLXT6RuAvZy6w2rjIEB9Xg/s6fRx/7Zb37YEbAnc73T2SuAgp+4otXERoL6vAA50+roV8IBTt9M1YEbg+XJnY/V/IXCUpTTiubay+wJ7N2irJtcV68Z0QFvIunIBcKSjkXZMawF/OHQ7JeAk4HRHp1obdCL2ytxlCtgGWN3byNB7CbgXUAr8roZNnYCV6y05GTjDUhr1vGkK0klUx/+ZjU7rRr4OWSJ2+SaDcbR5qwSqTm3KMxN+K8siOonXkqYE3AMoQkOiqNsA+N3hkbaXAl4L+jhENSNFrLarlsxU1J2edMxGzbBtLWPDz5sQoF2McmtI/izBf87hkKJe54LFHbpdqnxUBIf2/Z7ZsHZJwgyGA1qrtItySxMCVHW0cvMxwPkOLwS+TrgpRXUjDwlHFyn3PMesV5XWLXUJ2Bx40LB+nyM9ycQkgD81FC8JSjNbG+PfoqjWPuRloC4B1knxi2JxXr+o97xnODBJ4NchYelisX0KWDAwvlon/ToErABYq/yhRSX0MgN8TVHtoCZRdMGjFBuSQ4BLDR3tEt/0DLAOAdZ2TAvvUsXFxcdGx5qem3mcS6DzcBFkSrMhWawoOr5f3PSFFmT39ttLgK7nlFYWCHim47iO5SFR7eSqBMDW6fIAR21L5ReVYarkS0DpyryG9RKwCfCIMQqVDK4N6ChvKvUogiZZNIOVirSeVck+ZYkjNI5NgUetgXoJ0MV6qJyg2y6VEEL1EOVN5c8+iNYxrWdVojqYShqjbs2m2qiMoQv9oHgJeAZYJ2DJuqCYr7iU/xCYw3JoQp7/CCwBfB3wx7qAehZY1xqPhwCxrQjX3yrZqLiEfyLwXKVdlXj7JCqdq4ReJRsWleDHA8+VDTRDglVSDwHrlXvfqr5UiJrFQFaOyuE+iQJKgRWSX42CpM5ET4cMeAg4FTglYERvOYSql0o/X/UJ+QFf5zfSkKqreouiSk4rHgi/SvEQcLlxk2VtPzWVZaOPcrCROq3tqNKubLQiwHodxDp09Gn3MwyUtRuyDqfm6zGeGWDtgA4zjuYWgZM8MywAtVW9JDAAcyfkIUA5ftlAJ7qEUJWwSnRvPPUS7SSDPco3HRx131slupTS5VSVvGOsEa7/EdMCqoW0SvS64WuB5x+Ue+q+gS9/dXZZMuD4yuVrjFUqOkdoIW+1Blivg+gNtNDV3k/AbH1EH/gZmD3gu65S9cZeY4w9KagtdhaBbe3Hbh8Vo6jGS2QyAS1TUNsIywRkAlrFUNQsEdV4TkE28ZmAxBhlAjIBNgKJNaIGaVTjeQ2wQycTkBijTEAmwEYgsUbUII1qPK8BduhkAhJjlAnIBNgIJNaIGqRRjec1wA6dTEBijDIBmQAbgcQaUYM0qvG8BtihkwlIjFEmIBNgI5BYI2qQRjWe1wA7dDIBiTHKBGQCbAQSa0QN0i6M9/3Nt7b8tsKwVeP/ySKbCWiLQOL2rYK4VeM8A/5BoBWGrRpnAjIBibNPJiATUPwXfd6GtgiDLtaAFt3nppmAxDGQCcgEJEYgcfd9mAFtF/mJHuNEO1cGpz58t3HDQH0M0AcHJ1b6QMBFxS/aHd4QwYuLT0ce0bDtWJr1gQBFv/n5xwq0FP2aBRMrfSBA4A3+rKAXzC5/PtHbZ229vhCggdVdjHsxtl44ORBW1heqpGp9wat2lMZs0DcChIV+PEK/2LfMwJe89GWqd4uPh+sDsvrplN5IHwnoDbgeRzMBHpQi6mQCIoLrMZ0J8KAUUScTEBFcj+lMgAeliDqZgIjgekxnAjwoRdT5G9JXBXCAvE2AAAAAAElFTkSuQmCC" alt="notfication">',
    "NOT_SUPPORTED": '<img class="icon" src="data:image/png;base64,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" alt="Not supported">',
    "PARTIALLY_SUPPORTED": '<img class="icon" src="data:image/png;base64,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" alt="Partially supported">',
    "BUG_REPORT": '<img class="icon" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFwAAABcCAYAAADj79JYAAAAAXNSR0IArs4c6QAABgdJREFUeF7t3E9oHFUcB/Dvb9KIh3gQrc1OxBq1O1spXtKDgoLRneRU7WnbWhRFaBVRPFSoeLAF8Q8KohS0ggr+axsPaj0ls5iiBRWaixS7u0FLSjNJrXqxBzHJ/HTSptTtJvNm583vbeEt5LS/9/v93mdfJvNmJ0OwL1EBEq1mi8GCCy8CC27BhQWEy9kVbsGFBYTL2RVuwYUFhMvZFW7BhQWEyxld4ccGBrr/PDe7eag+/bnEvAOvr3JtT+8XGycm5iTqtaphDHz89tU98wvdnwJ4gEGVvNGrXmE7gz4BcHhV19z2wZ/PnjOBbgS8Wuq7Lor4ABH8pUnniR547mMAPrhYixE4Dm0r16b/kEYXB/+6eGPf1RQdBHB382TzQK+WCjuYaX8L2KN/s7N1U+P0tCS6KHh13ZpbIqdrhICB5SapE32s6D5FhH3L18KEEy1UypNnfpVCFwMP1hXWw8EIQBuSJqcDPfAKzwL0ZlItgI8jQsWfnDmRHJs9Qgw8bjXwCi8B9IJK21nQg5K7C4zXVepEjL3DjXCPSqyOGFHw8+huDLFLpfl20KulwvPM9LJKfmnsuCdx8Lho1XPfYuAZFZQYncDXEOAx6FaA+wnoj843/wsWf3gSRCcowm1M2KuS1wS2MfC48JhXeJdAO1VwdMeYwjYKvohedD8kwqO6QVfKZxLbOPiFY3q823xIAt00dqeA/28XmCP8qShyKsOTp3/MsUZiaiN/NJe6Coru2yA8ndilxgAieqJcm26189RYZflUxsADz/0WwD0is2wuwtjnN0LRD3qpBSPggef+BaDHCPaFosQIyo1wSLoHcfCq5x5mYJP0RFvVY2D3UD18TbIXUfCxkruNGJ9JTjCxFkWDfm32SGKcpgAx8Gqpr8jMdU1960wz77Bz8/1Cl2kzgQel3nuVZ870IkDq8cqJtQSOgaJXVDNl+Y3IBu4VxjsYUdUvZRwf8eszgykHXQy34KnlLHhqsmwDLHg2v9SjLXhqsmwDLHg2v9SjLXhqsmwDTIInnoc7w2DsbmuCFLV96rVYj53x9uriVSAaXWmssfPwpAlVS+4BZmxNimv5foYt9+KGrE1wIhws18JtbfWsMCjTeXhS/qDofg/CnUlxnQQOxg9+I7yrrZ4VBuUL7rkzAHoV+rg8xNAKBzDr18NCWz0rDMobnBV6aB1iDhx+PczNJbfEsWLguRa8aTlZ8Ba/X3aFpzwuZTlLiUt1LHhgL8+mXAoZ7y204Km9s93MacEteHqB1CNMXkuxx/DUH1em00J7SEntbY/h6cmMH1JWajnLbRGc8eac/Gob+9Y+aXXYrX2La3JJaFnet+AWXGn9dOzWPql7u8LlV/jUfw8VuCnpg+mob3yAU349XNtWzwqDMp2HJ+UPPPe7Vg8xSBq3+L65LyCO+vUwt//MyBm87yOAH1YCbg4yBk4f+/XpR9rqWWFQJvDzO82kV7vnw6bOw5PrGjsPt1v7pMWm+Y+mBbfg6QVSjzB+LaXdY3TqmXbIAAsu/EFYcAsuLCBczuAKTzPToNi3H8Q70owRi2V6z29MizwsJ9PGJy1I1XOP8QqP0EubT0c8ARPlerhRRy6VHLLgG25Yw3OrZlUak4qh7vne8vHfzojVkyq0VGes5A4RY8X/MJDqiQnDQ7VwTKpeXEd0hS9NLM1zBXPDIDzn18I3csu/TGIj4HEvJle6iZW95G8MPG5g1FvT76DrSwB3CK20nyIsbB6unzkpVO+yMkbB4272D6C7/5z7DgGP54nAwPsne8Ind07A2MPajR3DW8GOFt09DqECYL1m+BMRY0Ty+bIr9W98hV/aHANOUHK3EGMLgAczwn/FhEN+LTxEQPzk1I54dRT4pSKjpcJAF1OFgfsAxF/qrk4QOwtgioBvFohHhmszEx0h3NREx4I3Y40X3ev/cXits4C1cC7cCRDhVNSFqasimhpshL93InBzT1cM+JWAqdKjBVdR0hhjwTViqqSy4CpKGmMsuEZMlVQWXEVJY4wF14ipksqCqyhpjLHgGjFVUllwFSWNMRZcI6ZKqn8BiO5+e0RcwW8AAAAASUVORK5CYII=" alt="Bug report">',
    "EMPTY_FILE": '<img class="icon" src="data:image/png;base64,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" alt="Empty file">',
    "SUCCESS_FILE": '<img class="icon" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFwAAABcCAYAAADj79JYAAAAAXNSR0IArs4c6QAABB1JREFUeF7t2k1PE0EYB/BntgWKGFEjanwLKAHsG2I1ikatEUtLQdGAZ0/cSARKqXqwJw8IN29ePbQevWg/h+Cn8CQ2kZfumCmQFClM29199u3husP+d379Z3Z3Wgb0hyrAUNMoDAgcuQQETuDIAshx1HACRxZAjqOGEziyAHIcNZzAkQWQ46jhBI4sgBxHDSdwZAHkOGo4gSMLIMdRwwkcWQA5jhpO4MgCyHHUcAJHFkCOo4YfBJ4FJV4M5oDD1+9LK5/1+lwIvIrk5CR41rpCOeB8QhzmnE8VllY/6YFO4P8pRrNRr+/PrzwweF55iDM2XVj88VErOoFXCEamIk0d7et5AHhWDZYzSBUWV5a1oBP4jt5k1t/8u6jkGcD4YaAc4G3hw8r7RtEJHACiLzt9vo62HAB7Kodkq0xVX3xbXv0pH7t/hOvBB2cGW9s9a2LNHpMDasMW53c1+Fg2cmSjuC6WkVEMbFeDx1LhNkVR88AhiYXtWvBo1n/UV1TE08gIJrYrwRPT3cfU1pYc4yyBje068KGFSLu3tC5ukMNmYLsKfPzVteN/m7bEMhIzC9s14MlM6IRa4nkO8NhMbFeAD88ETjIvE80eMhvb8eBjcz2nNpWWHAB/ZAVsR4MnXg908K1N0eyHVsF2LHgsFT6tMFVgR62EbQh4Yi7gb3RjR44jH/HkTfDMxiYI7Afy0dr3RuQZe0foupcSTwWzwNiElt20eidQOX5k3n+WMyXPOdyXnwcfW9eGb2PDu+2J4k/mcbr3nIc3ixvkPati6wa+F3t3unjoozP957e8JbGM3LUyti7g1bHx0BPp8AWuquJ1/Y7VsTWDH45tPHpsNnhR8ZRvkIN2wNYELp5GuKJ8AeABMyY7uuC/tKWWt1hvm5Evz6w+QtNTilno8UxfJys15TjwW/KJ491L5Neiw1ds2OixVLhr56XmpnyC1sLWtKRUThYLPZkJXS6VuFhGbtgRWzdwcSKj0RPzwSscyjfIiF2xdQU3En04E+hmpfIW63U7Y+sObgT6yGx/j+pVxQ8rB+yObQi4nujxdLgXtl9q+p2AbRi4HuixuVCfopRvkGGnYBsKrgU9mQ5eLfHyDTLkJGzDwRtFB4WJL3yDTsNGAW8E3aztAvkHrH2Eplf7euLre06Xndl6b5CyK949jgZef9MPmoJ9sdGWlEo6bU23N7Yp4I033f7YpoHXj+4MbFPBa0d3Drbp4HJ0Z2FbAvxgdOdhWwZ8P7ozsS0FXolu1i+3an150TIO9cWnlgs1+7eJtVyjljGWA9cyGTv8L4Ejf0oETuDIAshx1HACRxZAjqOGEziyAHIcNZzAkQWQ46jhBI4sgBxHDSdwZAHkOGo4gSMLIMdRwwkcWQA5jhpO4MgCyHHUcAJHFkCO+wdaqFh7mYFnJgAAAABJRU5ErkJggg==" alt="Success file">',
}

# Define a single template constant for both notes and user actions.
LIST_ITEM_HTML_TEMPLATE = "<li style='margin:0 0 5px 0;'> {item} </li>"
EXAMPLES_SECTION_HTML_TEMPLATE = """
<div> 
    <h3 class="head-3">PySpark and teradatamlspk example code</h3>
</div>
{examples_content}
"""

# Define HTML constants for opening and closing code blocks.
CODE_BLOCK_OPEN_HTML = "<pre class='pre-one'><code>\n"
CODE_BLOCK_CLOSE_HTML = "</code></pre>\n"

# Define a single HTML constant for PySpark and Teradatamlspk code.
CODE_BLOCK_HTML = '<div style="color: purple; font-weight: bold;">{line}</div>\n'


# Define HTML constant for comments
COMMENT_HTML = '<div style="color: darkgreen; font-weight: bold; padding-top: 5px; padding-bottom:5px;">{line}</div>\n\n'

# Define a constant for the left files template for directory.
LEFT_FILES_TEMPLATE = '''
<li class="content" style="cursor: pointer;">
    <a href="{filedir_converted}" target="_blank" style="text-decoration: none; color: inherit;">
        {filedir_display}
    </a>
</li>
'''

LEFT_PANE_NB_CELL = '''
<div style="display: flex; align-items: flex-start; margin-bottom: 15px;">
    <div class="execution-count">
        {execution_count}
    </div>
    <div class="cell">
        {highlighted_code}
    </div>
</div>
'''

LEFT_PANE_NB_MARKDOWN = '''
<div style="display: flex; align-items: flex-start; margin-bottom: 15px;">
    <div class="markdown">
        {highlighted_code}
    </div>
</div>
'''

HEADER_HTML_API = "<h2 class='head-2'>Differences between PySpark vs teradatamlspk for API <span>{name}</span></h2>"

HEADER_HTML = "<h2 class='head-2'>Differences between PySpark vs teradatamlspk for <span>{name}</span></h2>"

# Row template for the summary by module table.
HTML_ROW_BY_MODULE_TEMPLATE = '''
<tr>
    <td>{object_name}</td>
    <td class="notification" style="text-align: center;">{notification}</td>
    <td class="partially_supported" style="text-align: center;" >{partially_supported}</td>
    <td class="not_supported" style="text-align: center;" >{not_supported}</td>
    <td style="text-align: center;" >{total}</td>
    <td>{where_found}</td>
</tr>
'''

# Row template for the summary by file table.
HTML_ROW_BY_FILE_TEMPLATE = """
<tr>
    <td>{filename_html}</td>
    <td style="text-align: center;">{error}</td>
    <td style="text-align: center;">{empty_file}</td>
    <td style="text-align: center;" class="notification">{notification}</td>
    <td style="text-align: center;" class="partially_supported">{partially_supported}</td>
    <td style="text-align: center;" class="not_supported">{not_supported}</td>
    <td style="text-align: center;">{total}</td>
</tr>
"""

# Consolidated template for the summary by file table.
CONSOLIDATED_TEMPLATE = """
<table>
    <tr>
        <th colspan="7" style="text-align: center; background-color: #cee0ed;">User actions Summary by file
    </tr>
    <tr>
        <th colspan="7" style="background-color: #F0F2F5;text-align: left; width:800px; font-weight: normal; ">
            <strong>Note:</strong> 
            <ul style="margin: 5px 0 0 20px; padding-left: 15px;">
                <li><strong>SE</strong> refers to Syntax Errors</li>
                <li><strong>UE</strong> refers to Utility Errors</li>
            </ul>
        </th>
    </tr>
    <tr >
        <th style=" padding-left: 10px;">File</th>
        <th style=" padding-right: 10px; font-weight: bold;">{bug_report}</th>
        <th style=" padding-right: 10px; font-weight: bold;">{empty_file}</th>
        <th style=" padding-right: 10px; font-weight: bold;" class="notification">{notification}</th>
        <th style=" padding-right: 10px; font-weight: bold;" class="partially_supported">{partially_supported}</th>
        <th style=" padding-right: 10px; font-weight: bold;" class="not_supported">{not_supported}</th>
        <th style=" padding-right: 10px; font-weight: bold;">Total</th>
    </tr>
    {html_rows}
</table>
"""

# Total summary template.
TOTAL_SUMMARY = """
    <table>
        <tr>
            <th colspan="2" style="text-align: center; background-color: #cee0ed;">pyspark2teradataml Conversion Summary</th>
        </tr>
        <tr>
            <th style="padding: 8px; text-align: left;">Category</th>
            <th style="padding: 8px; text-align: left;">Count</th>
        </tr>
        <tr>
            <td style="padding: 8px;">Files converted</td>
            <td style="padding: 8px;">{total_files_converted}</td>
        </tr>
        <tr>
            <td style="padding: 8px;">Files failed to convert (Syntax errors + unexpected utility errors)</td>
            <td style="padding: 8px;">{total_files_not_converted} ({total_user_errors} + {total_utility_errors})</td>
        </tr>
        <tr>
            <td style="padding: 8px;">Empty files</td>
            <td style="padding: 8px;">{total_empty_files}</td>
        </tr>
        <tr>
            <td style="padding: 8px;">Total files processed (.py files + .ipynb files)</td>
            <td style="padding: 8px;">{total_files_processed} ({py_files_processed} + {ipynb_files_processed})</td>
        </tr>
    </table>
"""

# Base span style for file display
FILEDIR_DISPLAY_BASE = '<span style="display: flex; align-items: center; padding-left: 23px; white-space: nowrap;">{}</span>'

# Error span style with a bug report icon
FILEDIR_DISPLAY_ERROR = '<span style="display: flex; align-items: center; color: red; white-space: nowrap;">{} {}</span>'

# Success span style with a checkmark icon
FILEDIR_DISPLAY_SUCCESS = '<span style="display: flex; align-items: center; color: green; white-space: nowrap;">{} {}</span>'

FILEDIR_DISPLAY_EMPTY = '<span style="display: flex; align-items: center; white-space: nowrap;">{} {}</span>'

ARRAY_UDF_CONFIG = """
<details class="gray-background">
    <summary style="font-size: 18px; font-weight: bold; cursor: pointer; color: #2C3E50;"> Handling Arrays with UDFs</summary>
    
    <p style="margin: 10px 0; color: #555;">
                To work with arrays inside UDFs in Teradata Vantage, user must process both input and output array values:
    </p>
    <ul style="margin: 10px 0 10px 0; padding-left: 0; color: #555;">
        <li><strong>Input Arrays:</strong> Array columns passed into UDFs are received as string representations with extra quotes (if array size > 1).
                                           Hence, the user must strip the extra quotes and convert the string back into an array before processing.
            <ul style="margin: 5px 0 5px;">
                <li>For example, the array (1,2,3) arrives in the UDF as "(1,2,3)".</li>
                <li>To convert the string back to an array, the user can use the following code snippet:
                    <pre style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; margin: 10px 0;">
# Trim extra quotes from the string representation of the array
if arr.startswith('"') and arr.endswith('"'):
    arr = arr[1:-1]
# Handle scientific notation if present
import re
arr = re.sub(r"E\s*([+-]?\d+)", r"E\\1", arr)
# Evaluate the string to convert it back to an array
arr = eval(arr)
arr = [None if str(item).upper() == "NONE" else item for item in arr]
                    </pre>
                </li>
            </ul>
        </li>
        <li><strong>Output Arrays:</strong> If UDFs returns an array it must send the result back as a string representation of the array.
            <ul style="margin: 5px 0 5px;">
                <li>For example, to return the array (1,2,3), the UDF should return the string "(1,2,3)".</li>
                <li> To convert the output array to a string representation, the user can use the following code snippet:
                <pre style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; margin: 10px 0;">
# Return the array as a string representation
return str(tuple(result)).replace("None", "NULL")
                    </pre>
                </li>
            </ul>
        </li>
        <li><strong>Using Custom Delimiter:</strong> Pass additional argument 'delimiter' to the udf/ register function as character apart from comma(,) or any special character present in the array elements.
            <ul style="margin: 5px 0 5px;">
                <li>For Example:
                    <pre style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; margin: 10px 0;">
# Using pipe (|) as delimiter for when input/ output column is of ArrayType.
udf(func, ArrayType(IntegerType()), delimiter="|")
                    </pre>
                </li>
            </ul>
        </li>
        <li> For arrays containing Date, Timestamp, or Interval elements, the UDF must handle both the input and output carefully, ensuring that each element is parsed and formatted in a way that aligns with Teradata Vantage's formats.</li>
    </ul>
</details>"""