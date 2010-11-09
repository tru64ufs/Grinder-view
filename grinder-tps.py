#!/usr/bin/python2.6

#Thread(0) Run(1) Test(2) Start time (ms since Epoch,3), Test time(4) Errors(5) HTTP response code(5) HTTP response length(6) HTTP response errors(7) Time to resolve host(8) Time to establish connection(9) Time to first byte(10)

import sys
import numpy as np
from scipy import stats
import matplotlib as mpl
mpl.use('pdf')

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import datetime

#from matplotlib.backends.backend_pdf import pdfpages
#pp = pdfpages('grinder-multi.pdf')

if len(sys.argv) < 2:
    print 'log file(s) needed'
    sys.exit('Correct argument needed')

logfiles = sys.argv[1:]
fhandles= dict()
for f in logfiles:
   fhandles[f] = open(f, 'r')

tps = dict()
err = dict()
time = []
res = []    # total response time
ttfb = []   # time to first byte (server time + rtt)

for fh in fhandles.itervalues():
    print 'Processing', fh
    for l in fh:
        
        terms = l.strip().split(',')
        if len(terms) != 12:
            continue

        if not terms[0].isdigit():
            continue

        if terms[1].strip() == '-1':
            continue

        t = datetime.datetime.fromtimestamp(int(terms[3][:-3]))

        # response time plot
        time.append(t)
        res.append(int(terms[4]))
        ttfb.append(int(terms[11]))

        # Throughput
        if terms[6].strip() == '200':
            if t in tps:
                tps[t] += 1
            else:
                tps[t] = 1
        else:
            if t in err:
                err[t] += 1
            else:
                err[t] = 1
        
for fh in fhandles.itervalues():
   fh.close()


fig=plt.figure()
plt.title('Grinder', fontsize=10)
fig.subplots_adjust(left=0.1, right=0.9, top=0.91, wspace=0.2, hspace=0.76)

print 'Plotting TPS chart'
avgtps = np.mean(tps.values())
plt.subplot(411)
plt.plot_date(mpl.dates.date2num(tps.keys()), tps.values(),
        marker="0", fillstyle='full', c='blue', alpha=0.2, aa=True, markeredgewidth=0, markeredgecolor='none', markersize=3)
#        marker="0", fillstyle='full', c='none', alpha=0.3, aa=True, markeredgewidth=1, markeredgecolor='blue', markersize=1.5)
plt.grid(True)
plt.title('Throughput (Avg. thoughput: %d TPS)' % avgtps, fontsize=8)
plt.ylabel('TPS', fontsize=7)

ax = plt.gca()
#ax.text(tps.keys()[20], 1, 'Avg. thoughput: %d TPS' % np.mean(tps.values()), fontsize=6)
ax.grid(color='grey', alpha=0.3, linestyle='-', linewidth=0.1)
for tick in ax.xaxis.get_major_ticks():
    tick.label1.set_fontsize(6)
for tick in ax.yaxis.get_major_ticks():
    tick.label1.set_fontsize(6)
for line in ax.get_xticklines() + ax.get_yticklines():
    line.set_markersize(2)
ax.xaxis.set_major_locator(MaxNLocator(10))
ax.spines['left'].set_linewidth(0.4)
ax.spines['bottom'].set_linewidth(0.4)
ax.spines['right'].set_linewidth(0.4)
ax.spines['top'].set_linewidth(0.4)
#ax.spines['left'].set_position('center')
#ax.spines['right'].set_color('none')
#ax.spines['bottom'].set_position('center')
#ax.spines['top'].set_color('none')
#ax.spines['left'].set_smart_bounds(True)
#ax.spines['bottom'].set_smart_bounds(True)
#ax.xaxis.set_ticks_position('bottom')
#ax.yaxis.set_ticks_position('left')

print 'Plotting response time chart'
avgresp=np.mean(res)
vuser=int(round(avgtps * avgresp * 0.001))
plt.subplot(412)
plt.plot_date(mpl.dates.date2num(time), res, label='Response time',
        alpha=0.05, markeredgewidth=0, markeredgecolor='none', color='red', markevery=20, antialiased=True, markersize=2)

#plt.plot_date(mpl.dates.date2num(time), ttfb, label='Time to first byte',
#        alpha=0.1, markeredgewidth=0, markeredgecolor='none', color='lightgreen', markevery=20, antialiased=True, markersize=2)
plt.title("Response time (Little's law verification: %d vusers)" % vuser, fontsize=8)
plt.ylabel('msec (log)', fontsize=7)

ax = plt.gca()
ax.set_yscale('log')
ax.grid(color='grey', alpha=0.3, linestyle='-', linewidth=0.1)
for tick in ax.xaxis.get_major_ticks():
    tick.label1.set_fontsize(6)
for tick in ax.yaxis.get_major_ticks():
    tick.label1.set_fontsize(6)
for line in ax.get_xticklines() + ax.get_yticklines():
    line.set_markersize(2)
ax.xaxis.set_major_locator(MaxNLocator(10))
ax.spines['left'].set_linewidth(0.4)
ax.spines['bottom'].set_linewidth(0.4)
ax.spines['right'].set_linewidth(0.4)
ax.spines['top'].set_linewidth(0.4)


print 'Plotting response time distribution chart'
plt.subplot(413)
avgttfb = np.mean(ttfb)
labtext1 = "avg response time: %d msec" % avgresp
labtext2 = "avg TTFB: %d msec" % avgttfb

plt.hist( res , len(res)/3,
        histtype='stepfilled', edgecolor="red", alpha=0.3, fill=True, color='red', normed=1, aa=True)
plt.hist( ttfb , len(ttfb)/3, 
        histtype='stepfilled', edgecolor="green", alpha=0.2, fill=True, color='green', normed=1, aa=True)

plt.axvline(x=avgresp, linewidth=1, color='red', alpha=0.5, label=labtext1)
plt.axvline(x=avgttfb, linewidth=1, color='green', alpha=0.5, label=labtext2)

plt.title('Response time distribution', fontsize=8)
plt.ylabel('percentage', fontsize=7)
plt.xlabel('response time in msec (log scale)', fontsize=5)
plt.grid(True)

ax = plt.gca()
ax.grid(color='grey', alpha=0.3, linestyle='-', linewidth=0.1, which='both')
#ax.set_xscale('log')
#ax.text(np.amax(res), 0.1, "Avg. response time: %d msec" % np.mean(res), fontsize=6)
for tick in ax.xaxis.get_major_ticks():
    tick.label1.set_fontsize(6)
for tick in ax.yaxis.get_major_ticks():
    tick.label1.set_fontsize(6)
for line in ax.get_xticklines() + ax.get_yticklines():
    line.set_markersize(2)
#for sp in ax.spines:
#    sp.set_linewidth(0.3)

ax.spines['bottom'].set_linewidth(0.3)
ax.spines['right'].set_linewidth(0.3)
ax.spines['top'].set_linewidth(0.3)
ax.spines['left'].set_linewidth(0.3)

leg = ax.legend(loc='upper right')
for t in leg.get_texts():
    t.set_fontsize(6)    # the legend text fontsize
leg.get_frame().set_linewidth(0.05)
leg.get_frame().set_alpha(0.85)


print 'Plotting response time cumulative distribution chart'
plt.subplot(414)
plt.hist(res, len(res)/3,
        histtype='stepfilled', alpha=0.3, color='pink',normed=1, cumulative=True, aa=True, edgecolor='brown')
#plt.axhline(y=0.90, linewidth=0.6, color='purple', alpha=0.6, label="90 percentile")
per90 = stats.scoreatpercentile(res,90)
per95 = stats.scoreatpercentile(res,95)
per90str = '90%%: %d msec' % per90
per95str = '95%%: %d msec' % per95

plt.axvline(x=per90, linewidth=1, color='red', alpha=0.6, label=per90str)
plt.axvline(x=per95, linewidth=1, color='navy', alpha=0.6, label=per95str)
plt.title('Response time CD histogram', fontsize=8)
plt.ylabel('percentage', fontsize=7)
plt.xlabel('response time in msec', fontsize=5)
plt.grid(True)

ax = plt.gca()
ax.grid(color='grey', alpha=0.3, linestyle='-', linewidth=0.1)
#ax.text(stats.scoreatpercentile(res,96), 0.1, "90 percentile: %d msec" % stats.scoreatpercentile(res,90),  fontsize=6)
for tick in ax.xaxis.get_major_ticks():
    tick.label1.set_fontsize(6)
for tick in ax.yaxis.get_major_ticks():
    tick.label1.set_fontsize(6)
ax.xaxis.set_major_locator(MaxNLocator(20))
ax.yaxis.set_major_locator(MaxNLocator(10))
ax.set_ylim(ymin=0, ymax=1)
ax.spines['left'].set_linewidth(0.4)
ax.spines['bottom'].set_linewidth(0.4)
ax.spines['right'].set_linewidth(0.4)
ax.spines['top'].set_linewidth(0.4)
#ax.yaxis.set_ticks_position('left')

for line in ax.get_xticklines() + ax.get_yticklines():
    line.set_markersize(2)

leg = ax.legend(loc='upper right')
for t in leg.get_texts():
    t.set_fontsize(6)    # the legend text fontsize
leg.get_frame().set_linewidth(0.05)
leg.get_frame().set_alpha(0.85)
#plt.axis(xmin=0, xmax=300)

plt.suptitle("Grinder run analysis", fontsize=10)

print "Rendering and saving to 'grinder-result.pdf'"
plt.savefig('grinder-result.pdf', transparent=True)
#plt.show()

