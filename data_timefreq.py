# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 16:01:38 2019

Try the timefreq V2 with real data

@author: ludov
"""

import numpy as np
import matplotlib.pyplot as plt
from compute_timefreq import compute_timefreq

#The directory and file
file = '2019-03-06T17-33-00McsRecording_1100um_P3.rbf'

basedir = 'D:/Federica/RAW_BINARY_FILES/'
filename  = basedir + file 

#Data characteristics
nb_channel = 16
sampling_rate = 20000.
t_start = 0.
f_start, f_stop = 1., 200.
 
# Signal mapped from file (not all file in memory)
#-1 asks the reshape to automatically estimate segment size 
sig = np.memmap(filename, mode='r', dtype='float64').reshape(-1, nb_channel)[:,0]

duration = len(sig)/sampling_rate

sig_times =np.arange(0,duration,1./sampling_rate)


#PLot the signal
fig, axs = plt.subplots(nrows=2)
axs[0].plot(sig_times, sig)
axs[0].set_ylabel('Signal (mV)')
axs[0].set_title(file)

#Now the serious things start
#Compute the TimeFreq heat map
complex_map, map_times, freqs, tfr_sampling_rate = compute_timefreq(sig, sampling_rate,
                                                                    f_start, f_stop, delta_freq=1., nb_freq=None,
                                                                    f0=2.5,  normalisation = 0., t_start=t_start)


#Dissociate the complex map to extract the amplitude and the phase 
ampl_map = np.abs(complex_map) # the amplitude map (module)
phase_map = np.angle(complex_map) # the phase

#Extent the colormap for the borders
delta_freq = freqs[1] - freqs[0]
extent = (map_times[0], map_times[-1], freqs[0]-delta_freq/2., freqs[-1]+delta_freq/2.)


#Display the amplitude map 
im = axs[1].imshow(ampl_map.transpose(), interpolation='nearest', 
                    origin ='lower', aspect = 'auto', extent = extent, cmap='viridis')
axs[1].set_xlabel('Time (s)')
axs[1].set_ylabel('Freq (Hz)')

#Add a colorbar 
cbar = fig.colorbar(im, orientation='horizontal',label='Amplitude (AU)')


#A second plot, for the average of the morlet spectrum == rough FFT
fig, ax = plt.subplots()
morlet_spectrum = np.mean(ampl_map, axis=0)
ax.plot(freqs, morlet_spectrum)
ax.set_title('Morlet spectrum')
ax.set_ylabel('Amplitude (AU)')
ax.set_xlabel('Frequency (Hz)')
plt.show()


