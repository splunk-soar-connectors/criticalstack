# import json


def all_results(provides, all_results, context):

    json_view = context['QS'].get('force_jsonview', ['False'])

    if not provides:
        provides = 'Query Value'

    if json_view[0] == 'true':
        return _get_json_data(all_results, context, provides)
    else:
        return _get_data(all_results, context, provides)


def _get_data(all_results, context, provides):
    summary_results = []
    body_color = '#303741'

    cs_type = provides
    inner_id = 0

    for summary, action_results in all_results:
        if not action_results:
            continue
        for result in action_results:
            parameter = result.get_param()
            result_summary = result.get_summary()
            data = result.get_data()
            row_id = str(inner_id)
            accordion_toggle = ''

            if(len(data) > 0 and 'sources' in data[0] and len(data[0]['sources']) > 0):
                accordion_toggle = 'accordion-toggle'

            if result_summary and parameter:

                provides_count = result_summary.get('detected_' + provides + '_count')
                hash_count = result_summary.get('detected_hash_count')
                ip_count = result_summary.get('detected_ip_count')
                domain_count = result_summary.get('detected_domain_count')

                summary_results.append((
                    data,
                    row_id,
                    accordion_toggle,
                    (
                        parameter.get(provides) or parameter.get('hash') or parameter.get('ip') or parameter.get('domain')
                    ),
                    (
                        provides_count or hash_count or ip_count or domain_count
                    ),
                    result_summary.get('lists_updated'),
                    result_summary.get('list_prefix'),
                    result_summary.get('additional_details')
                ))

            inner_id = inner_id + 1

    context['summary_results'] = summary_results
    context['cs_type'] = cs_type
    context['body_color'] = body_color

    return 'CriticalStack_Intel_template.html'


def _get_json_data(all_results, context, provides):
    # data = []
    inner_data = []
    json_html = ''
    for summary, action_results in all_results:
        if action_results:
            for result in action_results:
                inner_data.append(
                    {
                        'results':
                        {
                            'summary': result.get_summary(),
                            'parameters': result.get_param(),
                            'data': result.get_data()
                        }
                    }
                )

    print(str(inner_data))
    if len(inner_data) > 0:
        json_html = json_html + _json_treeify(inner_data, None, json_html, 0, '')

    json_html = (
                '<div class="treeview" onwidgetload="init_treeview_widget(this);" '
                'style="padding-left: 5px;">'
                '<div class="treewidget" onclick="toggle(event, this);">ActionResults'
            ) + json_html + '</div></div>'

    context['json_data'] = json_html
    return 'CriticalStack_Intel_json_template.html'


def _json_treeify(a, parent, htmlstring, index, list_name):

        if isinstance(a, list) or isinstance(a, dict):
            if isinstance(a, list):
                for idx, b in enumerate(a):
                    htmlstring = htmlstring + (
                        '<div class="treeitem treewidget">' + (
                            (
                                '<span class="keyname">' + list_name + '&nbsp;'
                                '</span>'
                            )
                            if list_name != '' else ''
                        ) + '<span class="type-indicator">[' + str(idx) + ']</span>' + '&nbsp;&nbsp;'
                    )
                    htmlstring = (_json_treeify(b, a, htmlstring, idx, '') + '</div>')

                return htmlstring

            elif isinstance(a, dict):
                if not(isinstance(parent, list) or isinstance(parent, dict)):
                    htmlstring = htmlstring + (
                        '<div class="treeitem treewidget">' + str(parent) + '&nbsp;'
                    )

                htmlstring = htmlstring + (
                    '<span class="type-indicator">{' + str(len(a)) + '}</span>'
                )

                for idx, b in enumerate(a):
                    htmlstring = _json_treeify(b, a, htmlstring, index, '')

                if(not(isinstance(parent, list) or isinstance(parent, dict)) and htmlstring):
                    return(htmlstring + '</div>')
                else:
                    return(htmlstring)
        else:
            if isinstance(parent, dict):
                if isinstance(parent[a], dict):
                    return _json_treeify(
                        parent[a],
                        a,
                        htmlstring,
                        index,
                        ''
                    )
                elif isinstance(parent[a], list):
                    return _json_treeify(
                        parent[a],
                        a,
                        htmlstring,
                        0,
                        a
                    )
                else:
                    return htmlstring + (
                        '<div class="treeitem treedata">'
                        '<span class="keyname">' + str(a) + '</span>&nbsp;'
                        '<span class="treedata" data-contains="[]">' + str(parent[a]) + '</span></div>'
                    )
            else:
                return htmlstring + (
                    '<div class="treeitem treedata">'
                    '<span class="treedata" data-contains="[]">' + str(parent[a]) + '</span></div>'
                )
