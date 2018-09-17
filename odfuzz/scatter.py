import os

import plotly
import plotly.graph_objs as go
import pandas

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
    find_string = "Plotly.newPlot"
    stop_string = "then(function(eventPlot)"

    def locate_newplot_script_tag(soup):
        script_tag = soup.find_all(string=re.compile(find_string))

        if len(script_tag) == 0:
            raise ValueError("Couldn't locate the newPlot javascript in {}".format(filename))
        elif len(script_tag) > 1:
            raise ValueError("Located multiple newPlot javascript in {}".format(filename))

        if script_tag[0].find(stop_string) > -1:
            raise ValueError("Already updated javascript, it contains:", stop_string)

        return script_tag[0]

    def find_newplot_creation_line(javascript_lines):
        for index, line in enumerate(javascript_lines):
            if line.find(find_string) > -1:
                return index, line
        raise ValueError("Missing new plot creation in javascript, couldn't find:", find_string)

    def join_javascript_lines(javascript_lines):
        # join the lines with javascript line terminator ;
        return ";".join(javascript_lines)

    def register_on_events(events):
        on_events_registration = []
        for function_name in events:
            on_events_registration.append("eventPlot.on('{}', {})".format(
                function_name, function_name
            ))
        return on_events_registration

    # load the file
    with open(filename) as inf:
        txt = inf.read()
        soup = bs4.BeautifulSoup(txt, "lxml")

    new_plot_script_tag = locate_newplot_script_tag(soup)
    javascript_lines = new_plot_script_tag.string.split(";")

    line_index, line_text = find_newplot_creation_line(javascript_lines)

    on_events_registration = register_on_events(events)

    # replace whitespace characters with actual whitespace
    # using + to concat the strings as {} in format
    # causes fun times with {} as the brackets in js
    # could possibly overcome this with in ES6 arrows and such
    line_text = line_text + ".then(function(eventPlot) { " + join_javascript_lines(on_events_registration)\
                          + "  })".replace('\n', ' ').replace('\r', '')

    # now add the function bodies we've register in the on handles
    for function_name in events:
        javascript_lines.append(events[function_name])

    # update the specific line
    javascript_lines[line_index] = line_text

    # update the text of the script tag
    new_plot_script_tag.string.replace_with(join_javascript_lines(javascript_lines))

    # save the file again
    with open(filename, "w") as outf:
        outf.write(str(soup))


class ScatterPlotter:
    def __init__(self, stats_directory):
        self._stats_directory = stats_directory
        self._csv_file_path = os.path.join(self._stats_directory, DATA_RESPONSES_NAME)
        self._html_plot_path = os.path.join(self._stats_directory, DATA_RESPONSES_PLOT_NAME)

    def create_plot(self):
        data = pandas.read_csv(self._csv_file_path + '.csv', delimiter=';')

        traces = []
        for entity_set in data['EntitySet'].unique():
            trace = go.Scattergl(
                name=entity_set,
                x=data[data['EntitySet'].isin([entity_set])]['Time'],
                y=data[data['EntitySet'].isin([entity_set])]['Data'],
                text=data[data['EntitySet'].isin([entity_set])]['URL'],
                mode='markers'
            )
            traces.append(trace)
        layout = go.Layout(
            title='Response time overview',
            hovermode='closest',
            xaxis={'title': 'Time'},
            yaxis={'title': 'Data'}
        )

        figure = go.Figure(data=traces, layout=layout)
        plotly.offline.plot(figure, filename=self._html_plot_path, auto_open=False)
        add_plotly_events(self._html_plot_path)
