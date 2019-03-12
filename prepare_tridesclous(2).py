"""
Explore a data dir and make group of file to run tridesclous.
"""

import tridesclous as tdc
import numpy as np
import pandas as pd
import os
import re
import datetime


basedir = '/home/samuel/Bureau/federica/'
datadir = basedir + 'raw_files/'
tdc_workdir = basedir + 'tdc_workdirs/'




if not os.path.exists(tdc_workdir):
    os.mkdir(tdc_workdir)



def explore():
    
    columns = ['filename']
    
    filenames =  []
    for filename in os.listdir(datadir):
        #~ print(filename)
        if filename.endswith('.rbf'):
            filenames.append(filename)
    
    files = pd.DataFrame({'filename' : filenames})
    
    for ind, row in files.iterrows():
        #~ print(row['filename'])
        if len(row['filename'].split('_')) == 2:
            rec_datetime, depth= row['filename'].replace('.rbf', '').split('_')
            protocol = 'P1'
        else:
        
            rec_datetime, depth, protocol= row['filename'].replace('.rbf', '').split('_')
        
        #~ print(rec_datetime, depth, protocol)
        
        pattern = '(\d+)\-(\d+)\-(\d+)T(\d+)-(\d+)-(\d+)McsRecording'
        r = re.findall(pattern, rec_datetime)
        if len(r) == 1:
            YY , MM , DD , hh, mm , ss  =r[0]
            rec_datetime = datetime.datetime(int(YY),int(MM),int(DD),int(hh),int(mm),int(ss))
        else:
            rec_datetime = None
        #~ print(rec_datetime)
        #~ print(r)
        #~ exit()
        #~ re.findall(
        
        #~ 2019-03-06T17-33-24McsRecording
        
        #~ rec_datetime = rec_datetime.replace('')
        
        files.at[ind, 'rec_datetime'] = rec_datetime
        #~ print(protocol)
        files.at[ind, 'protocol'] = int(protocol.replace('P', ''))
        files.at[ind, 'depth'] = float(depth.replace('um', ''))
    
    files['date'] = files['rec_datetime'].apply(lambda e: e.date())
    
    
    groups = files.groupby(['date', 'depth'])
    print(groups)
    for g, rows in groups:
        group_name = '{}_{}'.format(g[0], g[1])
        #~ print(g)
        #~ print(rows)
        files.loc[rows.index, 'group_name']=group_name
    
    files = files.sort_values(['date', 'depth', 'protocol'])
    files = files.reset_index()
    
    #~ print(files)
    files.to_excel(basedir + 'file_list.xlsx')
    
    
    #~ def create_depth
    
    

def create_tridesclous_workdir():
    files = pd.read_excel(basedir + 'file_list.xlsx')
    
    group_names = np.unique(files['group_name'])
    print(group_names)
    
    for group_name in group_names:
        print('*******')
        print(group_name)
        dirname = tdc_workdir + group_name
        print(dirname)
        
        if os.path.exists(dirname):
            print('Already exists', dirname)
            continue
        
        
        
        keep = files['group_name']==group_name
        #~ print(keep)
        filenames = files.loc[keep, 'filename'].tolist()
        #~ print(filenames)
        
        #~ exit()
        
        filenames = [ os.path.join(datadir, f) for f in filenames ]
        print(filenames)
        
        #~ exit()
        
        dataio = tdc.DataIO(dirname=dirname)
        
        # feed DataIO with one file
        dataio.set_data_source(type='RawData', filenames=filenames,
                    sample_rate=20000., dtype='float64', total_channel=16,
                    bit_to_microVolt=1./1e6)

        print(dataio)

        # set the probe file
        dataio.set_probe_file(basedir + 'good_atlas_probe.prb')
    
    
    
def run_all_catalogues():

    files = pd.read_excel(basedir + 'file_list.xlsx')
    
    group_names = np.unique(files['group_name'])
    
    for group_name in group_names:
        print('*******')
        print(group_name)
        dirname = tdc_workdir + group_name
        
        dataio = tdc.DataIO(dirname=dirname)
        print(dataio)
        
        for chan_grp in dataio.channel_groups.keys():
            cc = tdc.CatalogueConstructor(dataio=dataio, chan_grp=chan_grp)
            print(cc)
            
            fullchain_kargs = {
                'duration' : 300.,
                'preprocessor' : {
                    'highpass_freq' : 400.,
                    'lowpass_freq' : 5000.,
                    'smooth_size' : 0,
                    'chunksize' : 1024,
                    'lostfront_chunksize' : 128,
                    'signalpreprocessor_engine' : 'numpy',
                },
                'peak_detector' : {
                    'peakdetector_engine' : 'numpy',
                    'peak_sign' : '-',
                    'relative_threshold' : 4.5,
                    'peak_span' : 0.0002,
                },
                'noise_snippet' : {
                    'nb_snippet' : 300,
                },
                'extract_waveforms' : {
                    'n_left' : -20,
                    'n_right' : 30,
                    'mode' : 'rand',
                    'nb_max' : 20000,
                    'align_waveform' : False,
                },
                'clean_waveforms' : {
                    'alien_value_threshold' : 25.,
                },
              }
            feat_method = 'global_pca'
            feat_kargs = {}
            clust_method = 'sawchaincut'
            clust_kargs = {}
                   
            tdc.apply_all_catalogue_steps(cc, fullchain_kargs, 
                    feat_method, feat_kargs,clust_method, clust_kargs)
            print(cc)


def export_spike_and_report():
    files = pd.read_excel(basedir + 'file_list.xlsx')
    group_names = np.unique(files['group_name'])
    for group_name in group_names:
        print('*******')
        print(group_name)
        dirname = tdc_workdir + group_name
        dataio = tdc.DataIO(dirname=dirname)
        
        try:
            dataio.export_spikes(export_path=None, # None is inside the workir
                split_by_cluster=False,  use_cell_label=True, formats='csv')        # csv' or 'mat' or 'xlsx'
            print('Export OK')
        except:
            print('Erreur in exporting spikes')

        try:
            tdc.generate_report(dataio, export_path=None, neighborhood_radius=None)  # None is inside the workir
            print('Report OK')
        except:
            print('Erreur in reporting')
    

    

if __name__ == '__main__':
    
    # Step 1 : create the list and the XLSX file
    # explore()
    
    # Step 2: create tridesclous workdir if they not exists
    # create_tridesclous_workdir()
    
    # Step 3: run the catalogue for tridesclous
    # run_all_catalogues()
    
    # Step 4 : manual check + run peeler
    
    # Step 5 : export spiketrain in csv and reporting
    export_spike_and_report()
    
    
    
    
    
    
    