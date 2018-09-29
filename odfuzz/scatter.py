import os
import sys

import plotly
import plotly.graph_objs as go
import pandas
import pandas.errors

import bs4
import re

from odfuzz.constants import DATA_RESPONSES_NAME, DATA_RESPONSES_PLOT_NAME

events = {
    'plotly_click': """
        function plotly_click(data) {
            var tmpElem = document.createElement('textArea');
            tmpElem.value = (data['points'][0]['text']);

            tmpElem.setAttribute('readonly', '');
            tmpElem.style = {position: 'absolute', left: '-9999px'};
            document.body.appendChild(tmpElem);

            tmpElem.select();
            document.execCommand('copy');
            
            document.body.removeChild(tmpElem);
            alert('URL copied into clipboard');
        }
    """
}


def add_plotly_events(filename):
    find_string = 'Plotly.newPlot'
    stop_string = 'then(function(eventPlot)'

    def locate_newplot_script_tag(soup):
        script_tag = soup.find_all(string=re.compile(find_string))

        if len(script_tag) == 0:
            raise ValueError('Cannot locate the newPlot javascript in {}'.format(filename))
        elif len(script_tag) > 1:
            raise ValueError('Located multiple newPlot javascript in {}'.format(filename))

        if script_tag[0].find(stop_string) > -1:
            raise ValueError('The file contains already updated javascript: {}'.format(stop_string))

        return script_tag[0]

    def join_javascript_lines(javascript_lines):
        return ';'.join(javascript_lines)

    def split_lines_by_newplot_tag(javascript_source):
        return javascript_source.string.split('Plotly.newPlot')

    def register_on_events(events):
        on_events_registration = []
        for function_name in events:
            on_events_registration.append('eventPlot.on(\'{}\', {})'.format(function_name, function_name))
        return on_events_registration

    with open(filename) as html_file:
        txt = html_file.read()
        soup = bs4.BeautifulSoup(txt, 'lxml')

    new_plot_script_tag = locate_newplot_script_tag(soup)
    javascript_lines = split_lines_by_newplot_tag(new_plot_script_tag)

    line_index, line_text = 1, javascript_lines[1]
    on_events_registration = register_on_events(events)

    # replace whitespace characters with actual whitespace using + to concatenate the strings
    line_text = line_text + '.then(function(eventPlot) { ' + join_javascript_lines(on_events_registration)\
                          + '  })'.replace('\n', ' ').replace('\r', '')

    # add the function bodies we've register in the on handles
    functions = []
    for function_name in events:
        functions.append(events[function_name])

    # update the line with created functions
    javascript_lines[line_index] = line_text + ';'.join(functions)

    # update the text of the script tag
    new_plot_script_tag.string.replace_with('Plotly.newPlot'.join(javascript_lines))

    # save the file again
    with open(filename, 'w') as html_file:
        html_file.write(str(soup))


class ScatterPlotter:
    def __init__(self, stats_directory):
        self._stats_directory = stats_directory
        self._csv_file_path = os.path.join(self._stats_directory, DATA_RESPONSES_NAME)
        self._html_plot_path = os.path.join(self._stats_directory, DATA_RESPONSES_PLOT_NAME)

    def create_plot(self):
        try:
            data = pandas.read_csv(self._csv_file_path + '.csv', delimiter=';')
        except pandas.errors.EmptyDataError:
            sys.stderr.write('Cannot read empty CSV file\n')
        except pandas.errors.ParserError as pandas_error:
            sys.stderr.write('An error occurred while reading CSV: {}\n'.format(pandas_error))
        else:
            self.plot_graph(data)

    def plot_graph(self, data):
        traces = []
        for entity_set in data['EntitySet'].unique():
            trace = go.Scattergl(
                name=entity_set,
                x=data[data['EntitySet'].isin([entity_set])]['Time'],
                y=data[data['EntitySet'].isin([entity_set])]['Data'],
                text=data[data['EntitySet'].isin([entity_set])]['URL'],
                hovertext=data[data['EntitySet'].isin([entity_set])]['Brief'],
                hoverinfo='x+y+text',
                mode='markers'
            )
            traces.append(trace)

        layout = go.Layout(
            title='Response time overview',
            hovermode='closest',
            xaxis={'title': 'Time (Seconds)'},
            yaxis={'title': 'Data (Bytes)'}
        )

        figure = go.Figure(data=traces, layout=layout)
        plotly.offline.plot(figure, filename=self._html_plot_path, auto_open=False)
        add_plotly_events(self._html_plot_path)
