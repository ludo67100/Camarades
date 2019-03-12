from compute_timefreq import compute_timefreq
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal


sampling_rate= 20000.
t_start = 0.

f_start = 1.
f_stop = 100.

# generate signal
duration = 10.
sig_times = np.arange(0, duration, 1./sampling_rate)

f1, f2 = 20., 25.
speed = .5
sig_ampl = scipy.signal.sawtooth(sig_times, width=.5) + 1
#~ ampl = 1




f =  (np.sin(np.pi*2*speed*sig_times)+1)/2 *  (f2-f1) + f1
sig_phase = np.cumsum(f/sampling_rate)*2*np.pi
sig = np.cos(sig_phase) *  sig_ampl

#~ noise = np.random.randn(sig.size)
#~ sig = sig + noise

spike_indexes = np.random.randint(low=0, high=sig.size-1, size=200)
spike_times = spike_indexes / sampling_rate + t_start

#~ print(spike_indexes)
#~ exit()
#~ fig, ax = plt.subplots()
#~ ax.eventplot(spike_indexes)


fig, ax = plt.subplots()
ax.plot(sig_times, sig)
#~ ax.eventplot(spike_times)

#~ plt.show()

fig, ax = plt.subplots()

complex_map, map_times, freqs, tfr_sampling_rate = compute_timefreq(sig, sampling_rate, f_start, f_stop, delta_freq=1., nb_freq=None,
                f0=2.5,  normalisation = 0., t_start=t_start)


ampl_map = np.abs(complex_map) # the amplitude map (module)
phase_map = np.angle(complex_map) # the phase

delta_freq = freqs[1] - freqs[0]
extent = (map_times[0], map_times[-1], freqs[0]-delta_freq/2., freqs[-1]+delta_freq/2.)

im = ax.imshow(ampl_map.transpose(), interpolation='nearest', 
                    origin ='lower', aspect = 'auto', extent = extent, cmap='viridis')
im.set_clim(0, .5)
fig.colorbar(im)

ind_max = np.argmax(ampl_map, axis=1)
print(ind_max)
#~ phase_with_morlet = 
freq_max = freqs[ind_max]
ax.plot(map_times, freq_max, color='m', lw=3)

fig, ax =  plt.subplots()
im = ax.imshow(phase_map.transpose(), interpolation='nearest', 
                    origin ='lower', aspect = 'auto', extent = extent, cmap='viridis')
im.set_clim(-np.pi, np.pi)
fig.colorbar(im)
ax.plot(map_times, freq_max, color='m', lw=3)



estimated_phase_morlet = phase_map[np.arange(map_times.size), ind_max]
estimated_ampl_morlet = ampl_map[np.arange(map_times.size), ind_max]

# hilbert way
analytic_signal = scipy.signal.hilbert(sig)
amplitude_envelope = np.abs(analytic_signal)
instantaneous_phase = np.unwrap(np.angle(analytic_signal))
instantaneous_frequency = (np.diff(instantaneous_phase) / (2.0*np.pi) * sampling_rate)



fig, axs = plt.subplots(nrows=2)
axs[0].plot(sig_times, sig_ampl, color='g')
axs[0].plot(map_times, estimated_ampl_morlet, color='r')
axs[0].plot(sig_times, amplitude_envelope, color='c')

axs[1].plot(sig_times, sig_phase%(2*np.pi), color='g')
axs[1].plot(map_times,estimated_phase_morlet, color='r')
axs[1].plot(sig_times,instantaneous_phase%(2*np.pi), color='c')


##### spike phase
spike_indexes_400 = (spike_times*tfr_sampling_rate).astype('int64')

spikes_phase_morlet = estimated_phase_morlet[spike_indexes_400]
spikes_phase_hilbert = instantaneous_phase[spike_indexes]

spikes_phase_morlet = (spikes_phase_morlet+2*np.pi) % (2*np.pi)
spikes_phase_hilbert = (spikes_phase_hilbert+2*np.pi) % (np.pi*2)

bins=np.arange(-np.pi, 3*np.pi, np.pi/10)
hist_phase_morlet, bins = np.histogram(spikes_phase_morlet, bins=bins)
hist_phase_hilbert, bins = np.histogram(spikes_phase_hilbert, bins=bins)


fig, ax = plt.subplots()
ax.plot(bins[:-1], hist_phase_morlet, color='r')
ax.plot(bins[:-1], hist_phase_hilbert, color='c')








plt.show()