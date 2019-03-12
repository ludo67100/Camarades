
import numpy as np
import pandas as pd
import neo
import os
import scipy.signal
from ephyviewer import mkQApp, MainViewer, TraceViewer, SpikeTrainViewer, TimeFreqViewer
from ephyviewer import InMemorySpikeSource, InMemoryAnalogSignalSource


basedir = 'D:/Federica/'
datadir = basedir + 'RAW_BINARY_FILES/'
tdc_workdir = basedir + 'tdc_workdirs/'


#~ name = '2019-03-06T17-12-08McsRecording_900um.rbf'
#~ name = '2019-03-06T17-37-18McsRecording_1100um_P4.rbf'
name = '2019-03-06T17-27-49McsRecording_1100um_P1.rbf'
raw_filename = datadir + name

sample_rate = 20000.

def make_spike_source():
    
    files = pd.read_excel(basedir + 'file_list.xlsx')
    row = files[files['filename'] == name].iloc[0]
    print(row)
    
    group_name = row['group_name']
    
    group = files[files['group_name'] == group_name]
    seg_index,  = np.nonzero(group['filename'] == name)
    assert seg_index.size == 1, 'several or 0 names'
    seg_index = seg_index[0]
    print(seg_index)
    
    
    all_spikes =[]
    for chan_grp in range(4):
    
        csv_name = 'spikes - segNum {} - chanGrp {} - cell#all.csv'.format(seg_index, chan_grp)
        csv_filename = os.path.join(tdc_workdir, group_name, 'export', csv_name)
        print(csv_filename)
        
        spikes = pd.read_csv(csv_filename)
        spikes.columns=['index', 'label']
        spikes = spikes[spikes['label']!=-10]
        for label in np.unique(spikes['label']):
            
            spike_times = (spikes[spikes['label'] == label]['index']/sample_rate).values
            spike_name = 'Unit {}#{}'.format(chan_grp, label)
            all_spikes.append({ 'time':spike_times, 'name':spike_name})    
            
    spike_source = InMemorySpikeSource(all_spikes=all_spikes)
    return spike_source
    


def make_sig_sources():
    # read from file
    sample_rate = 20000.
    t_start = 0.
    nb_channel = 16
    
    #### READ SIGNAL
    # case 1 : mapped from file (not all file in memory)
    # sigs = np.memmap(raw_filename, mode='r', dtype='float64').reshape(-1, nb_channel) 
    # case 2 : all sample in memory
    sigs = np.fromfile(raw_filename, dtype='float64').reshape(-1, nb_channel)
    sigs /= 1e6 # put in uV
    # case 3: neo file in memory
    #~ reader = neo.RawBinarySignalIO(filename=raw_filename, dtype='float64', 
                #~ sampling_rate=sample_rate, nb_channel=nb_channel)
    #~ seg = reader.read_segment()
    #~ anasigs = seg.analogsignals[0]
    #~ # sig = anasigs.rescale('uV').magnitude
    #~ sigs = anasigs.magnitude
    #~ t_start = anasigs.t_start.rescale('s').magnitude
    #~ sample_rate = anasigs.sampling_rate.rescale('Hz').magnitude
    
    #### FILTER SIGNAL
    N = 8 # order
    freq_low, freq_high = 4., 10.
    Wn = [ freq_low/(sample_rate/2), freq_high/(sample_rate/2)]
    #~ print(Wn)
    sos_coeff = scipy.signal.iirfilter(N, Wn, btype='band', ftype='butter', output='sos')
    #~ print(sos_coeff)
    sigs_filtered = scipy.signal.sosfiltfilt(sos_coeff, sigs, axis=0)
    
    source_sig = InMemoryAnalogSignalSource(sigs, sample_rate, t_start)
    
    source_filtered_sig = InMemoryAnalogSignalSource(sigs_filtered, sample_rate, t_start)
    
    return source_sig, source_filtered_sig
    

def make_viewer():
    
    source_sig, source_filtered_sig =make_sig_sources()
    #source_spike = make_spike_source()
    
    win = MainViewer(debug=False, show_global_xsize=True, show_auto_scale=True)
    
    view1 = TraceViewer(source=source_sig, name='trace')
    view1.params['scale_mode'] = 'same_for_all'
    view1.auto_scale()

    view2 = TraceViewer(source=source_filtered_sig, name='trace filtred')
    view2.params['scale_mode'] = 'same_for_all'
    view2.auto_scale()
    
    view3 = TimeFreqViewer(source=source_sig, name='tfr')
    view3.params['show_axis'] = False
    view3.params['timefreq', 'deltafreq'] = 1
    #~ view3.by_channel_params['ch3', 'visible'] = True
    
    
    #view4 = SpikeTrainViewer(source=source_spike)
    
    
    win.add_view(view1)
    win.add_view(view2, tabify_with='trace')
    win.add_view(view3)
    #win.add_view(view4)

    return win


if __name__ == '__main__':
    app = mkQApp()
    win = make_viewer()
    win.show()
    app.exec_()
    
    