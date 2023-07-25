# -*- coding: utf-8 -*-
"""
My custom helped functions for day to day!
Created on Thu Jan 12 11:49:54 2023

@author: hamishj
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors 
import matplotlib.gridspec as gridspec
import numpy as np


colmaps = {
        'ptol_sunset':      ['#364B9A', '#4A7BB7', '#6EA6CD', '#98CAE1', '#C2E4EF','#EAECCC', '#FEDA8B',
                             '#FDB366', '#F67E4B', '#DD3D2D','#A50026'],
        'ptol_nightfall':   ['#125A56', '#00767B', '#238F9D', '#42A7C6', '#60BCE9','#9DCCEF', '#C6DBED',
                              '#DEE6E7', '#ECEADA', '#F0E6B2', '#F9D576', '#FFB954', '#FD9A44', '#F57634',
                              '#E94C1F','#D11807', '#A01813'],
        'ptol_iridescent':  ['#FEFBE9', '#FCF7D5', '#F5F3C1', '#EAF0B5', '#DDECBF','#D0E7CA', '#C2E3D2',
                             '#B5DDD8', '#A8D8DC', '#9BD2E1','#8DCBE4', '#81C4E7', '#7BBCE7', '#7EB2E4',
                             '#88A5DD','#9398D2', '#9B8AC4', '#9D7DB2', '#9A709E', '#906388','#805770',
                             '#684957', '#46353A'],
        'morlnd_ext_bb':    ['#000000', '#0018a8', '#6300e4', '#dc143c', '#ff7538', '#e6e635', '#ffffff'],
        }

colsets = {
        'ptol_bright':          ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE','#AA3377', '#BBBBBB',
                                 '#000000'],
        'ptol_vibrant':         ['#EE7733', '#0077BB', '#33BBEE', '#EE3377', '#CC3311', '#009988', '#BBBBBB',
                                 '#000000'],
        'ptol_light':           ['#77AADD', '#EE8866', '#EEDD88', '#FFAABB', '#99DDFF','#44BB99', '#BBCC33', 
                                 '#AAAA00', '#DDDDDD', '#000000'],
        'ptol_muted':           ['#CC6677', '#332288', '#DDCC77', '#117733', '#88CCEE','#882255', '#44AA99',
                                 '#999933', '#AA4499', '#DDDDDD','#000000'],
        'ptol_high-contrast':   ['#004488', '#DDAA33', '#BB5566', '#000000'],
        'ham_simple':           ['#ff0000', '#000000', '#808080'],
        'pone_colorful':        ['#3399ff','#31aeb4','#d3eb36','#fed32c','#f4337d','#cc3095'],
        'sfu_tones':            ['#CC0633','#A6192E','#e0e0df','#54585A','#000000']
    
        }

all_col = {k:v for d in (colmaps,colsets) for k,v in d.items()}

def colours():
    output = ""
    for key in all_col.keys():
        output += key + ', '
    print(output)


# Other Helpers ##############################################################################################

# Plot Helpers ###############################################################################################
def despine(axis = None, trim = False, drop = 0, noLine = False,
            bottom = True, left = True, top = False, right = False):
    if axis == None:
        axis = plt.gca()
    # Hide the specified spines
    if not right:  axis.spines.right.set_visible(False)
    if not top:    axis.spines.top.set_visible(False)
    if not bottom: axis.spines.bottom.set_visible(False);
    if not left:   axis.spines.left.set_visible(False);
    
    # Stollen from seaborn git
    # https://github.com/mwaskom/seaborn/blob/master/seaborn/utils.py
    # line 375, accessed April 6, 2023
    if trim:
            # clip off the parts of the spines that extend past major ticks
            xticks = np.asarray(axis.get_xticks())
            if xticks.size:
                firsttick = np.compress(xticks >= min(axis.get_xlim()),
                                        xticks)[0]
                lasttick = np.compress(xticks <= max(axis.get_xlim()),
                                       xticks)[-1]
                axis.spines['bottom'].set_bounds(firsttick, lasttick)
                axis.spines['top'].set_bounds(firsttick, lasttick)
                newticks = xticks.compress(xticks <= lasttick)
                newticks = newticks.compress(newticks >= firsttick)
                axis.set_xticks(newticks)

            yticks = np.asarray(axis.get_yticks())
            if yticks.size:
                firsttick = np.compress(yticks >= min(axis.get_ylim()),
                                        yticks)[0]
                lasttick = np.compress(yticks <= max(axis.get_ylim()),
                                       yticks)[-1]
                axis.spines['left'].set_bounds(firsttick, lasttick)
                axis.spines['right'].set_bounds(firsttick, lasttick)
                newticks = yticks.compress(yticks <= lasttick)
                newticks = newticks.compress(newticks >= firsttick)
                axis.set_yticks(newticks)
    
    if drop:
        axis.spines.left.set_position(('outward', drop))
        axis.spines.bottom.set_position(('outward', drop))
        
    if noLine:
        for pos in ['bottom', 'left']:
                axis.spines[pos].set_visible(False)
   
def errorbands(x, y, yerr, capsize = 0, ax = None, color = None, *args, **kwargs):
    if ax == None:
        ax = plt.gca()
   
    low  = y - yerr
    high = y + yerr
    poly = ax.fill_between(x, low, high, *args, facecolor = color, **kwargs)
    if capsize:
        ax.errorbar(x,y, yerr = yerr, capsize = capsize, color = color,
                    elinewidth = 0, fmt = '.')
        
    return poly
   
# Colormaps ##################################################################################################
def hex_to_rgb(value):
    '''
    Converts hex to rgb colours
    value: string of 6 characters representing a hex colour.
    Returns: list length 3 of RGB values'''
    value = value.strip("#") # removes hash symbol if present
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_dec(value):
    '''
    Converts rgb to decimal colours (i.e. divides each value by 256)
    value: list (length 3) of RGB values
    Returns: list (length 3) of decimal values'''
    return [v/256 for v in value]

def rgb_lst_to_hex(lst):
    col_hex = [mcolors.to_hex(_) for _ in lst]
    return col_hex

def get_continuous_cmap(hex_list, float_list=None, plot = False):
    ''' creates and returns a color map that can be used in heat map figures.
        If float_list is not provided, colour map graduates linearly between each color in hex_list.
        If float_list is provided, each color in hex_list is mapped to the respective location in float_list. 
        https://towardsdatascience.com/beautiful-custom-colormaps-with-matplotlib-5bab3d1f0e72
        
        Parameters
        ----------
        hex_list: list of hex code strings
        float_list: list of floats between 0 and 1, same length as hex_list. Must start with 0 and end with 1.
        
        Returns
        ----------
        colour map'''
    rgb_list = [rgb_to_dec(hex_to_rgb(i)) for i in hex_list]
    if float_list:
        pass
    else:
        float_list = list(np.linspace(0,1,len(rgb_list)))
        
    cdict = dict()
    for num, col in enumerate(['red', 'green', 'blue']):
        col_list = [[float_list[i], rgb_list[i][num], rgb_list[i][num]] for i in range(len(float_list))]
        cdict[col] = col_list
    cmp = mcolors.LinearSegmentedColormap('my_cmp', segmentdata=cdict, N=256)
    if plot:
        plt.figure( figsize = (6,1))
        plt.imshow( [list(np.arange(0, len( hex_list ) , 0.1))]*8 , interpolation='nearest', origin='lower'
                   , cmap= cmp )
        bounds = plt.gca().get_xlim()
        plt.xticks(bounds,[hex_list[0],hex_list[-1]])
        plt.yticks([])
    return cmp

def display_my_maps(continuous = colmaps, discrete = colsets):
        n = len(continuous)
        m = len(discrete)
        j = np.max([m,n])
        
        fig, axs = plt.subplots(j,2,figsize = (6,j*2/3))
        fig.subplots_adjust(hspace = 0.9)
        fig.patch.set_facecolor('whitesmoke')
        
        for i, hexlist in enumerate(list(continuous.values())):
            ax = axs[i,0]
            ax.imshow( [list(np.arange(0, 10 , 0.1))], interpolation='nearest', origin='lower',
                      cmap = get_continuous_cmap(hexlist), aspect = 'auto')
            ax.set(title = list(continuous.keys())[i])
        
        
        for i, hexlist in enumerate(list(discrete.values())):
            ax = axs[i,1]
            ax.imshow( [list(np.arange(0, 10, 10/len(hexlist)))], interpolation='nearest', origin='lower',
                      cmap = get_continuous_cmap(hexlist), aspect = 'auto')
            ax.set(title = list(discrete.keys())[i])
            
        for ax in axs.ravel():
                ax.axis('off')
        plt.show()

class HamColor:
    def __init__(self, name, hexlist = None):
        self.name = name
        if isinstance(hexlist, list):
            self.init_len = len(hexlist)
            self.cmap = get_continuous_cmap(hexlist)
            self.cycler = mpl.cycler(color = hexlist)
        elif hexlist == None:
            try:
                hexlist = all_col[name]
            except:
                print("Name Error: Please supply a list of hexidecimal values, a matplotlib colormap, or from the following.")
                colours()
                hexlist = ['#FFFFFF']
            self.init_len = len(hexlist)
            self.cmap = get_continuous_cmap(hexlist)
            self.cycler = mpl.cycler(color = hexlist)
        else:
            self.init_len = 8
            self.cmap = hexlist
            self.cycler = mpl.cycler(color = self.get_discrete(8, makehex = True))
    
    def test(self, N = None, mapBool = False, savePath = None):
        if N == None or N == 0:
            N = self.init_len
            N_bar = N
        elif N < 0:
            N_bar = 255
            N -= N
        N_bar = N
        t = 10
        f = 0.5
        spacing = 1
        
        ax_map = None
        if mapBool:
            fig = plt.figure(tight_layout=True,figsize = (11,4))
            gs = gridspec.GridSpec(2, 3, height_ratios = [1,5], width_ratios = [3,5,3])
            pp = 1
        else:
            fig = plt.figure(tight_layout=True,figsize = (8,4))
            gs = gridspec.GridSpec(2, 2, height_ratios = [1,5], width_ratios = [5,3])
            pp = 0
        ax_bar =  fig.add_subplot(gs[0, pp])
        ax_plot = fig.add_subplot(gs[1, pp])
        ax_mkr =  fig.add_subplot(gs[0, pp + 1])
        ax_sct =  fig.add_subplot(gs[1, pp + 1])
        
        fig.patch.set_facecolor('whitesmoke')
        
        # PLOT BAR
        ax_bar.imshow( [list(np.arange(0, 1 , 1/N_bar))]*5, interpolation='nearest', origin='lower',
                          cmap = self.cmap, aspect = 'auto')
        ax_bar.set_title(self.name, size = 17, pad = 8 )
        
        # PLOT LINES & COLORS
        c = [self.cmap(_)[:-1] for _ in np.linspace(0, 1, N)]
        x = np.linspace(0, t, 100)
        widths = [2,3,4,5,6,7,8,9]
        markers = ['.','o','s','^','*','D','$f$','p','o']
        flstl = ['full']*(len(markers)-1) + ['none']
        widths.reverse()
        for i in range(N):
            for _, thicc in enumerate(widths):
                xtmp = x[0+_*2:_*2+3]
                ax_plot.plot(xtmp, np.sin(xtmp/f) + i*spacing, color = c[i], lw = thicc)
                
            ax_plot.plot(x[len(widths)*2:61], np.sin(x[len(widths)*2:61]/f) + i*spacing, color = c[i], ls = 'solid')
            ax_plot.plot(x[60:71], np.sin(x[60:71]/f) + i*spacing , color = c[i], ls = 'solid')
            ax_plot.plot(x[70:81], np.sin(x[70:81]/f) + i*spacing , color = c[i], ls = 'dashed')
            ax_plot.plot(x[80:93], np.sin(x[80:93]/f) + i*spacing , color = c[i], ls = 'dashdot')
            ax_plot.plot(x[92:100], np.sin(x[92:100]/f) + i*spacing , color = c[i], ls = 'dotted')
            
            x_sct = np.random.random(size = 5)
            y_sct = np.random.random(size = 5)
            ax_sct.scatter(x_sct, y_sct, color = c[i])
        
        # PLOT MARKERS
        for _, mkr in enumerate(markers):
            if N >= 8:
                ax_mkr.plot(_,-0.15, marker = mkr, color = c[0], fillstyle = flstl[_])
                ax_mkr.plot(_,-0.05, marker = mkr, color = c[3], fillstyle = flstl[_])
                ax_mkr.plot(_, 0.05, marker = mkr, color = c[-4], fillstyle = flstl[_])
                ax_mkr.plot(_, 0.15, marker = mkr, color = c[-1], fillstyle = flstl[_])
            elif N >= 4:
                ax_mkr.plot(_,-0.15, marker = mkr, color = c[0], fillstyle = flstl[_])
                ax_mkr.plot(_,-0.05, marker = mkr, color = c[1], fillstyle = flstl[_])
                ax_mkr.plot(_, 0.05, marker = mkr, color = c[-2], fillstyle = flstl[_])
                ax_mkr.plot(_, 0.15, marker = mkr, color = c[-1], fillstyle = flstl[_])
            elif N == 3:
                ax_mkr.plot(_,-0.15, marker = mkr, color = c[0], fillstyle = flstl[_])
                ax_mkr.plot(_, 0, marker = mkr, color = c[1], fillstyle = flstl[_])
                ax_mkr.plot(_, 0.15, marker = mkr, color = c[-1], fillstyle = flstl[_])
            elif N == 2:
                ax_mkr.plot(_,-0.1, marker = mkr, color = c[0], fillstyle = flstl[_])
                ax_mkr.plot(_, 0.1, marker = mkr, color = c[-1], fillstyle = flstl[_])
            else:
                ax_mkr.plot(_,0, marker = mkr, color = c[0], fillstyle = flstl[_])
        
        if mapBool:
            # PLOT MAP
            ax_map =  fig.add_subplot(gs[:, 0])
            m = self.example_map(ax_map, N)
            ax_map.axis('off')
            
        ax_mkr.set(ylim = (-0.2,0.2))
        ax_bar.axis('off')
        ax_mkr.axis('off')
        ax_sct.set(xticks = [], yticks = [])
        ax_sct.patch.set_alpha(0)
        ax_sct.spines['top'].set_visible(False)
        ax_sct.spines['right'].set_visible(False)
        ax_plot.set(frame_on=False)
        ax_plot.yaxis.labelpad = -10
        ax_plot.set(ylabel = "N = {}".format(N), xticks = [], yticks = [])
        
        if savePath == None:
            plt.show()
        else:
            import os
            pathLoc = os.path.dirname(os.path.realpath(__file__)) + savePath + '\\hamMap_'+self.name+'.png'
            plt.savefig(pathLoc,dpi = 300)
            plt.show()
    
    def trunc(self, start = 0, stop = 0, n = 256, update = True, *args):
        new_name = 'trunc({n},{a:.2f},{b:.2f})'.format(n=self.cmap, a=start, b=stop)
        new_cmap = mcolors.LinearSegmentedColormap.from_list(new_name,self.cmap(np.linspace(start, stop, n)))
        if update == None:
            return new_cmap
        elif update:
            self.name = self.name + f"_trunc-{start}-{stop}"
            self.cmap = new_cmap
        else:
            return HamColor(self.name + f"_trunc-{start}-{stop}",new_cmap)
            
            
        return new_cmap
    
    def get_discrete(self, N = None, start = 0, stop = 1, makehex = False):
        if N == None:
            N = self.init_len
        tmpmap = self.trunc(start, stop, update = None)
        output = tmpmap(np.linspace(0,1,N))
        if makehex:
            output = [mcolors.to_hex(_) for _ in output]
        return output
    
    def example_map(self, ax, N, shape_file = '\lpr_000b16a_e'):
        from mpl_toolkits.basemap import Basemap
        from matplotlib.patches import Polygon
        from matplotlib.collections import PatchCollection
        import os
        
        colors = self.get_discrete(N)
        
        shape_file = os.path.dirname(os.path.realpath(__file__)) + '\map' + shape_file
        
        m = Basemap(projection = 'merc',llcrnrlon=-144,llcrnrlat=41,urcrnrlon=-51,urcrnrlat=83.7)
        m.readshapefile(shape_file,name = 'lpr_000b16a_e', default_encoding='iso-8859-15',
                        drawbounds=True)
        
        patches   = []
        np.random.shuffle(colors)
        for sn in range(13):
            pn = []
            for info, shape in zip(m.lpr_000b16a_e_info, m.lpr_000b16a_e):
                if info['SHAPENUM'] == sn + 1:
                    pn.append(Polygon(np.array(shape), True))
            patches.append(pn)
            ax.add_collection(PatchCollection(pn,facecolor=colors[sn%len(colors)],
                                              edgecolor='k', linewidths=0.1, zorder=2))
        return m
        
# colo = HamColor('ham_simple')
# colo.test(mapBool = 0)

def makeAllTests(cont = colmaps, disc = colsets, fileOutPath = '\\colors', mapBool = 0):
    for key in cont:
        colo = HamColor(key,cont[key])
        colo.test(N = -8, mapBool = mapBool, savePath = fileOutPath)
    for key in disc:
        colo = HamColor(key,disc[key])
        colo.test(N = colo.init_len, mapBool = mapBool, savePath = fileOutPath)

# makeAllTests()
        