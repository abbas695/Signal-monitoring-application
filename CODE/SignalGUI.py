import statistics
from io import BytesIO

import PySimpleGUI as sg
import matplotlib.animation as anim
import matplotlib.pyplot as plt
import neurokit2 as nk
import numpy as np
import pandas as pd
from matplotlib import mlab
from matplotlib.backends._backend_tk import Toolbar, NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Slider
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table
from svglib.svglib import svg2rlg


class Toolbar(NavigationToolbar2Tk):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2Tk.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom')]

    def init(self, *args, **kwargs):
        super(Toolbar, self).init(*args, **kwargs)


def statistics_fun(normal_signal, ax1, ax2, ax3, fig, abnormal_signal=None, abnormal_signal2=None):
    statistics_canvas = canvas.Canvas('signal statistics.pdf')
    statistics_canvas.setPageSize((900, 900))

    data_normal = [['mean', 'standard deviation', 'max value', 'min value'],
                   [str(round(statistics.mean(normal_signal), 2)), str(round(statistics.stdev(normal_signal), 2)),
                    str(round(max(normal_signal), 2)),
                    str(round(min(normal_signal), 2))]]
    table_normal = Table(data_normal, colWidths=70 * mm, rowHeights=20 * mm)
    table_normal.setStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ('FONTSIZE', (0, 0), (-1, -1), 18),

                           ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ])
    table_normal.wrapOn(statistics_canvas, 900, 1200)
    table_normal.drawOn(statistics_canvas, 9 * mm, 225 * mm)
    if (abnormal_signal is not None) and (ax1.lines and ax2.lines):
        data_abnormal = [['mean', 'standard deviation', 'max value', 'min value'],
                         [str(round(statistics.mean(abnormal_signal), 2)),
                          str(round(statistics.stdev(abnormal_signal), 2)),
                          str(round(max(abnormal_signal), 2)),
                          str(round(min(abnormal_signal), 2))]]

        table_abnormal = Table(data_abnormal, colWidths=70 * mm, rowHeights=20 * mm)

        table_abnormal.setStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                 ('FONTSIZE', (0, 0), (-1, -1), 18),

                                 ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                 ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                 ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ])

        table_abnormal.wrapOn(statistics_canvas, 900, 1200)
        table_abnormal.drawOn(statistics_canvas, 9 * mm, 165 * mm)

    if (abnormal_signal2 is not None) and (ax1.lines and ax2.lines and ax3.lines):
        data_abnormal2 = [['mean', 'standard deviation', 'max value', 'min value'],
                          [str(round(statistics.mean(abnormal_signal2), 2)),
                           str(round(statistics.stdev(abnormal_signal2), 2)),
                           str(round(max(abnormal_signal2), 2)),
                           str(round(min(abnormal_signal2), 2))]]

        table_abnormal2 = Table(data_abnormal2, colWidths=70 * mm, rowHeights=20 * mm)

        table_abnormal2.setStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                  ('FONTSIZE', (0, 0), (-1, -1), 18),
                                  ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                  ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                  ('BOX', (0, 0), (-1, -1), 0.25, colors.black)])

        table_abnormal2.wrapOn(statistics_canvas, 900, 1200)
        table_abnormal2.drawOn(statistics_canvas, 9 * mm, 105 * mm)

    styles = getSampleStyleSheet()
    style = ParagraphStyle(
        name='Normal',
        fontSize=18,
    )
    normal_signal_text = "Signal 1 statistics"
    normal_signal_text_style = Paragraph(normal_signal_text, style=style)
    normal_signal_text_style.wrapOn(statistics_canvas, 300 * mm, 300 * mm)  # size of 'textbox' for linebreaks etc.
    normal_signal_text_style.drawOn(statistics_canvas, 30 * mm, 270 * mm)  # position of text / where to draw
    if abnormal_signal is not None:
        abnormal_signal_text = "Signal 2 statistics"
        abnormal_signal_text_style = Paragraph(abnormal_signal_text, style=style)
        abnormal_signal_text_style.wrapOn(statistics_canvas, 300 * mm,
                                          300 * mm)  # size of 'textbox' for linebreaks etc.
        abnormal_signal_text_style.drawOn(statistics_canvas, 30 * mm, 210 * mm)  # position of text / where to draw
    if abnormal_signal2 is not None:
        abnormal_signal_text2 = "Signal 3 statistics"
        abnormal_signal_text_style2 = Paragraph(abnormal_signal_text2, style=style)
        abnormal_signal_text_style2.wrapOn(statistics_canvas, 300 * mm,
                                           300 * mm)  # size of 'textbox' for linebreaks etc.
        abnormal_signal_text_style2.drawOn(statistics_canvas, 30 * mm, 150 * mm)  # position of text / where to draw
    statistics_canvas.showPage()
    statistics_canvas.setPageSize((900, 500))
    imgdata = BytesIO()
    plt.savefig(imgdata, format='svg')
    imgdata.seek(0)  # rewind the data
    drawing = svg2rlg(imgdata)
    renderPDF.draw(drawing, statistics_canvas, 0, 70)
    statistics_canvas.showPage()
    statistics_canvas.save()


def draw_figure(canvas, figure, canvas_toolbar=None):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw_idle()
    if canvas_toolbar is not None:
        toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
        toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def main():
    # define the form layout
    sg.theme('Dark Brown4')

    layout = [[sg.Text('SignalViewer', size=(53, 1), justification='center', font='System 17')],
              [sg.Text('Spacebar to Pause ', font='System'),
               sg.Text('←,k to Move Backward ', font='System'),
               sg.Text('→,L to Move Forward ', font='System'),
               sg.Text('Set Combobox and Sliders Before Start ', font='System'),
               sg.Text(' 1,2 to Hide/Show '
                       'Figure ', font='System')],
              [sg.Combo(['red', 'green'], key='color', readonly=True, pad=((250, 0), 3)),
               sg.Combo(['Signal 1', 'Signal 2', 'Signal 3'], key='Spec', readonly=True),
               sg.Canvas(key='controls_cv'),
               sg.Combo(['plasma', 'inferno', 'magma', 'viridis', 'prism'], key='Color', readonly=True)],
              [sg.Canvas(size=(640, 80), key='-CANVAS-')],
              [sg.Text('Please Choose The Signal You Want', size=(112, 1), justification='center', font='System 14')],
              [sg.Slider(orientation='horizontal', key='stSlider', range=(1.0, 5.0), resolution=.1,
                         pad=((186, 0), 3), default_value=3.8),
               sg.Slider(orientation='horizontal', key='stSlider2', range=(5.0, 10.0),
                         resolution=.1, default_value=6.9),
               sg.Slider(orientation='horizontal', key='stSlider3', range=(0.0, 0.5),
                         resolution=0.001)],
              [sg.Button('ECG', pad=((265, 0), 3)), sg.Button('EMG'), sg.Button('RSP'), sg.Button('READ FILE'),
               sg.Button('Spectrogram'), sg.Button('PDF'), sg.Button('Exit')]]

    # create the form and show it without the plot
    window = sg.Window('Signal Viewer', layout, finalize=True)
    canvas_elem = window['-CANVAS-']
    canvas = canvas_elem.TKCanvas

    fig, axis = plt.subplots(nrows=4, figsize=(9, 5), constrained_layout=True,
                             gridspec_kw={'height_ratios': [3, 2, 2, 2]})
    axcolor = 'lightgoldenrodyellow'
    axpos = plt.axes([0.2, 0.004, 0.65, 0.03], facecolor=axcolor)

    spos = Slider(axpos, 'Pos', 0.1, 90.0)
    axis[3].get_shared_x_axes().join(axis[1], axis[2], axis[3])
    axis[1].spines['bottom'].set_visible(False)
    axis[2].spines['top'].set_visible(False)
    axis[2].spines['bottom'].set_visible(False)
    axis[3].spines['top'].set_visible(False)
    fig_agg = draw_figure(canvas, fig, window['controls_cv'].TKCanvas)
    plt.subplots_adjust(hspace=0)
    wavelist = []

    def spectrogram(Sig1, Sig2=None, Sig3=None):
        axis[0].clear()
        if values['Spec'] == 'Signal 1':
            spectrum1, freqs1, t1 = mlab.specgram(Sig1, NFFT=64, Fs=256, noverlap=32)
            min_val = 10 * np.log10(spectrum1.min())
            max_val = 10 * np.log10(spectrum1.max() + values['stSlider3'])
            axis[0].specgram(Sig1, NFFT=64, Fs=256, noverlap=32, cmap=values['Color'], vmin=min_val, vmax=max_val)
        elif values['Spec'] == 'Signal 2':
            if Sig2 is not None:
                spectrum1, freqs1, t1 = mlab.specgram(Sig2, NFFT=64, Fs=256, noverlap=32)
                min_val = 10 * np.log10(spectrum1.min())
                max_val = 10 * np.log10(spectrum1.max() + values['stSlider3'])
                axis[0].specgram(Sig2, NFFT=64, Fs=256, noverlap=32, cmap=values['Color'], vmin=min_val,
                                 vmax=max_val)
        elif values['Spec'] == 'Signal 3':
            if Sig3 is not None:
                spectrum1, freqs1, t1 = mlab.specgram(Sig3, NFFT=64, Fs=256, noverlap=32)
                min_val = 10 * np.log10(spectrum1.min())
                max_val = 10 * np.log10(spectrum1.max() + values['stSlider3'])
                axis[0].specgram(Sig3, NFFT=64, Fs=256, noverlap=32, cmap=values['Color'], vmin=min_val,
                                 vmax=max_val)

        axis[0].set_ylabel('Frequency (Hertz)')
        axis[0].set_xlabel('Time (Second)')

    def set_size(width, height, ax=None):
        """ w, h: width, height in inches """
        if not ax: ax = plt.gca()
        left = ax.figure.subplotpars.left
        right = ax.figure.subplotpars.right
        top = ax.figure.subplotpars.top
        bottom = ax.figure.subplotpars.bottom
        figw = float(width) / (right - left)
        figh = float(height) / (top - bottom)
        ax.figure.set_size_inches(figw, figh)

    def limitpan(ax):
        if ax.get_xlim()[0] <= 0 or ax.get_xlim()[1] >= 1500:
            ax.set_xlim(0, 10)
        if ax.get_ylim()[1] >= 3 or ax.get_ylim()[0] <= -2:
            ax.set_ylim(-2, 3)

    def readfile(file, ax):
        datawave = pd.read_csv(file)
        datawave = datawave.iloc[:, 0]
        if ax == 'Signal 1':
            if axis[2].lines and len(wavelist) != 0:
                wave_form(datawave, wavelist[len(wavelist) - 1], ax1=axis[1], ax2=axis[2])
                wavelist.append(datawave)
            else:
                wavelist.append(datawave)
                axis[2].cla()
                axis[2].grid()
                axis[3].cla()
                axis[3].grid()
                wave_form(datawave, ax1=axis[1])
        elif ax == 'Signal 2':
            if axis[1].lines and len(wavelist) != 0:
                wave_form(wavelist[len(wavelist) - 1], datawave, ax1=axis[1], ax2=axis[2])
                wavelist.append(datawave)
            else:
                wavelist.append(datawave)
                axis[1].cla()
                axis[1].grid()
                axis[3].cla()
                axis[3].grid()
                wave_form(datawave, ax2=axis[2])
        elif ax == 'Signal 3':
            if (axis[1].lines and axis[2].lines) and len(wavelist) != 0:
                wave_form(wavedata=wavelist[len(wavelist) - 2], abwavedata=wavelist[len(wavelist) - 1],
                          abwavedata2=datawave, ax1=axis[1], ax2=axis[2], ax3=axis[3])
            elif axis[1].lines and len(wavelist) != 0:
                wave_form(wavedata=wavelist[len(wavelist) - 1], abwavedata2=datawave, ax1=axis[1], ax3=axis[3])
                wavelist.append(datawave)
            elif axis[2].lines and len(wavelist) != 0:
                wave_form(datawave, wavelist[len(wavelist) - 1], ax2=axis[2], ax3=axis[3])
                wavelist.append(datawave)
            else:
                wavelist.append(datawave)
                axis[1].cla()
                axis[1].grid()
                axis[2].cla()
                axis[2].grid()
                wave_form(datawave, ax3=axis[3])
        return wavelist[len(wavelist) - 2], wavelist[len(wavelist) - 1], datawave

    def wave_form(wavedata, abwavedata=None, abwavedata2=None, ax1=None, ax2=None, ax3=None, ani=None):

        def initiate():
            if ax1 is not None:
                ax1.cla()
                ax1.set_ylabel('Signal 1')
                ax1.grid()
                ax1.set_ylim([wavedata.min(), wavedata.max()])
            if ax2 is not None:
                ax2.cla()
                ax2.set_xlabel('Samples')
                ax2.set_ylabel('Signal 2')
                if abwavedata is not None:
                    ax2.set_ylim([abwavedata.min(), abwavedata.max()])
                else:
                    ax2.set_ylim([wavedata.min(), wavedata.max()])
                ax2.grid()
            if ax3 is not None:
                ax3.cla()
                ax3.set_ylabel('Signal 3')
                if abwavedata2 is not None:
                    ax3.set_ylim([abwavedata2.min(), abwavedata2.max()])
                elif abwavedata is not None:
                    ax3.set_ylim([abwavedata.min(), abwavedata.max()])
                else:
                    ax3.set_ylim([wavedata.min(), wavedata.max()])
                ax3.grid()

        def update_time():
            t = 0
            if abwavedata is not None and wavedata is not None:
                t_axis = min(len(wavedata), len(abwavedata))
            elif abwavedata is None:
                t_axis = len(wavedata)
            while t < t_axis and t >= 0:
                t += ani.direction
                yield t

        def animate(frame):
            initiate()
            start, end = frame / 2, frame + 100
            plt.subplots_adjust(hspace=0)
            axis[0].xaxis.set_ticklabels([])
            axis[1].xaxis.set_ticklabels([])
            axis[1].yaxis.set_ticklabels([])
            axis[2].xaxis.set_ticklabels([])
            axis[2].yaxis.set_ticklabels([])
            axis[3].yaxis.set_ticklabels([])
            axis[0].yaxis.get_major_ticks()[0].label1.set_visible(False)
            if ax1 is not None:
                ax1.set_xlim(start, end)
                ax1.plot(wavedata[0:frame], color=values['color'])
            if abwavedata is not None and ax2 is not None:
                ax2.set_xlim(start, end)
                ax2.plot(abwavedata[0:frame], color=values['color'])
            elif ax2 is not None:
                ax2.set_xlim(start, end)
                ax2.plot(wavedata[0:frame], color=values['color'])
            if abwavedata2 is not None and ax3 is not None:
                ax3.set_xlim(start, end)
                ax3.plot(abwavedata2[0:frame], color=values['color'])
            elif abwavedata is not None and ax3 is not None:
                ax3.set_xlim(start, end)
                ax3.plot(abwavedata[0:frame], color=values['color'])
            elif ax3 is not None:
                ax3.set_xlim(start, end)
                ax3.plot(wavedata[0:frame], color=values['color'])
            set_size(values['stSlider'], values['stSlider2'], ax1)
            set_size(values['stSlider2'], values['stSlider'], ax2)

        def shhid(ax):
            if ax.get_visible():
                ax.set_visible(False)
            else:
                ax.set_visible(True)

        def on_press(event1):
            if event1.key.isspace():
                if ani.running:
                    ani.event_source.stop()
                    if ax1 is not None:
                        ax1.callbacks.connect('xlim_changed', limitpan)
                        ax1.callbacks.connect('ylim_changed', limitpan)
                    if ax2 is not None:
                        ax2.callbacks.connect('xlim_changed', limitpan)
                        ax2.callbacks.connect('ylim_changed', limitpan)
                    if ax3 is not None:
                        ax3.callbacks.connect('xlim_changed', limitpan)
                        ax3.callbacks.connect('ylim_changed', limitpan)
                    ani.running ^= True
                else:
                    ani.event_source.start()
                    ani.running = True
            elif event1.key == 'delete':
                ani._stop()
            elif event1.key == '1':
                shhid(axis[1])
            elif event1.key == '2':
                shhid(axis[2])
            elif event1.key == '3':
                shhid(axis[3])
            elif event1.key == 'left':
                ani.direction = -1
            elif event1.key == 'right':
                ani.direction = +1
            elif event1.key == 'l':
                ani.direction = +7
            elif event1.key == 'k':
                ani.direction = -7
            if event1.key in ['left', 'l', 'k', 'right']:
                t = ani.frame_seq.__next__()
                animate(t)

        def update(val):
            pos = spos.val
            axis[1].set_xlim(pos, pos + 10)
            fig.canvas.draw_idle()

        spos.on_changed(update)
        fig.canvas.mpl_connect('key_press_event', on_press)
        ani = anim.FuncAnimation(plt.gcf(), animate, frames=update_time(), interval=6, repeat=True)
        ani.running = True
        ani.direction = +1
        fig_agg.draw_idle()

    while True:
        event, values = window.read(timeout=10)
        if event in ('Exit', sg.WIN_CLOSED):
            exit(420)
        elif event in 'ECG':
            fig_agg.close_event(['EMG', 'RSP', 'READ FILE'])
            fig_agg.flush_events()
            wavedata = nk.ecg_simulate(duration=10, noise=0.01, heart_rate=100, sampling_rate=256)
            abwavedata = nk.ecg_simulate(duration=10, method="ecgsyn", sampling_rate=256)
            wave_form(wavedata, abwavedata, ax1=axis[1], ax2=axis[2])
            spectrogram(wavedata, abwavedata)
        elif event in 'EMG':
            fig_agg.close_event(['ECG', 'RSP', 'READ FILE'])
            fig_agg.flush_events()
            wavedata = nk.emg_simulate(duration=10, sampling_rate=256, burst_number=4)
            abwavedata = nk.emg_simulate(duration=10, burst_number=6, burst_duration=1.0, sampling_rate=256)
            wave_form(wavedata, abwavedata, ax1=axis[1], ax2=axis[2])
            spectrogram(wavedata, abwavedata)
        elif event in 'RSP':
            fig_agg.close_event(['ECG', 'EMG', 'READ FILE'])
            fig_agg.flush_events()
            wavedata = nk.rsp_simulate(duration=30, sampling_rate=256, noise=0.01)
            abwavedata = nk.rsp_simulate(duration=20, respiratory_rate=15, method="breathmetrics", sampling_rate=256)
            wave_form(wavedata, abwavedata, ax1=axis[1], ax2=axis[2])
            spectrogram(wavedata, abwavedata)
        elif event == "READ FILE":
            fig_agg.close_event(['ECG', 'EMG', 'RSP', 'Statistics', 'Save Graph as PDF'])
            filename = sg.popup_get_file('filename to open', no_window=True, file_types=(("CSV Files", "*.csv"),))
            wavedata, abwavedata, abwavedata2 = readfile(filename, values['Spec'])
        elif event == 'Spectrogram':
            spectrogram(wavedata, abwavedata, abwavedata2)
        elif event == 'PDF':
            if abwavedata is not None and abwavedata2 is not None:
                statistics_fun(wavedata, axis[1], axis[2], axis[3], fig, abnormal_signal=abwavedata,
                               abnormal_signal2=abwavedata2)
            elif abwavedata is not None:
                statistics_fun(wavedata, axis[1], axis[2], axis[3], fig, abnormal_signal=abwavedata)
            elif abwavedata2 is not None:
                statistics_fun(wavedata, axis[1], axis[2], axis[3], fig, abnormal_signal2=abwavedata2)
            else:
                statistics_fun(wavedata, axis[1], axis[2], axis[3], fig)

    window.close()


if __name__ == '__main__':
    main()
