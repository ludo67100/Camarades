""" 
Provided by Sam Garcia

Script to debug and/or understand the compute_timefreq module 


"""


from compute_timefreq import compute_timefreq
import numpy as np
import matplotlib.pyplot as plt

#The basics 
sampling_rate= 20000. #As in Fede's experiments
t_start = 0.

#Frequency range for analysis 
f_start = 1
f_stop = 100.

# generate a fake signal with two major frequencies
duration = 10. #In seconds 

sig_times = np.arange(0, duration, 1./sampling_rate) #Time vector for the signal

freq0, ampl0 = 10., 3. #Freq and amplitude for the first frequency

sig0 = np.sin(2*np.pi*freq0*sig_times)*ampl0 # First sinusoid based on first frequency

freq1, ampl1 = 60., 3. #Freq and amplitude for the second frequency

sig1 = np.sin(2*np.pi*freq1*sig_times)*ampl1 # Second sinusoid based on second freq

#The fake signal + noise
sig = sig0 + sig1 + np.random.randn(sig_times.size)*.4 

#PLot the signal
fig, axs = plt.subplots(nrows=2)
axs[0].plot(sig_times, sig)
axs[0].set_ylabel('Signal (AU)')
axs[0].set_title('Here is a fake signal')


#Now the serious things start
#Compute the TimeFreq heat map
complex_map, map_times, freqs, tfr_sampling_rate = compute_timefreq(sig, sampling_rate, f_start, f_stop, delta_freq=1., nb_freq=None,
                f0=2.5,  normalisation = 0., t_start=t_start)
'''
print(complex_map.shape)
print(map_times.shape)
print(map_times)
print(freqs)
print(tfr_sampling_rate)
print(complex_map.dtype)
'''

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











