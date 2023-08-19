# -*- coding: utf-8 -*-
"""
My custom colouring helper functions for day to day!
Created on Thu Jan 12 11:49:54 2023

@author: hamishj

Contributions 'borrowed' from:
 - wackywendell/mutedplots: https://github.com/wackywendell/mutedplots/blob/master/mutedcolors.py
"""
from hamhelper.errors import assert_error
from hamhelper.plotting import despine
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as mcm
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
import numpy as np

# continuous
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

# discrete
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

# create disct for all colours
all_col = {k: v for d in (colmaps, colsets) for k, v in d.items()}

def colours():
    """Prints list of all my custom colormaps."""
    output = ""
    for key in all_col.keys():
        output += key + ', '
    print(output)

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

def register_cmaps(cmap_dict: dict = None):
    """
    Defines a set of new colormaps for matplotlib, and registers them.
    
    Borrowed from wackywendell on Github:
    https://github.com/wackywendell/mutedplots/blob/master/mutedcolors.py

    arguments:
        cmap_dict (dict): {name:color list} pairs defining colormaps. Default 'None'
                          loads all of my maps.
    returns:
        set of cmap keys registered.
    """
    if cmap_dict is None:
        # load all colors
        cmap_dict = all_col
    
    for name, colorlist in cmaps.items():
        cmap = mcolors.LinearSegmentedColormap.from_list(name, colorlist)
        mcm.register_cmap(name, cmap)

        rname = name + '_r'
        cmap = mcolors.LinearSegmentedColormap.from_list(rname, list(reversed(colorlist)))
        mcm.register_cmap(rname, cmap)

    return set(cmaps.keys())

class HamColor:
    def __init__(self, name, hexlist = None):
        self.name = name
        self.init_len = None
        self.cmap = None
        self.cycler = None

        if isinstance(hexlist, list):                    # Hex list input
            self.init_len = len(hexlist)
            self.cmap = get_continuous_cmap(hexlist)
            self.cycler = mpl.cycler(color = hexlist)
        elif hexlist == None:                            # key name input
            try:
                hexlist = all_col[name]
            except KeyError as errormessage:
                print("Key Error: Please supply a list of hexidecimal values, a matplotlib colormap, or from the following.")
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
        """Test function to generate a serries of common plots in one figure.

        Args:
            N (int, optional): _description_. Defaults to initialize length.
            mapBool (bool, optional): Set to true if Basemap is installed, adds a map to the plot. Defaults to False.
            savePath (str, optional): Path to save figure. Defaults to None meaning do not save.
        """
        if N is None:
            N = self.init_len
            N_bar = N
        assert_error(N > 0, ValueError("Argument 'N' must be a positive intiger or 'None' type."))  # noqa: F631
        N_bar = N

        # x, y for lineplot
        t = 10
        f = 0.5
        spacing = 1
        
        ax_map = None  # leave empty if we dont want to plot
        if mapBool:
            # if basemap is installed creates larger figure
            fig = plt.figure(tight_layout=True,figsize = (11,4))
            gs = gridspec.GridSpec(2, 3, height_ratios = [1,5], width_ratios = [3,5,3])
            pp = 1
        else:
            # if basemap is not installed creates smaller figure
            fig = plt.figure(tight_layout=True,figsize = (8,4))
            gs = gridspec.GridSpec(2, 2, height_ratios = [1,5], width_ratios = [5,3])
            pp = 0
        # generate axis for each plot using gridspec
        ax_bar =  fig.add_subplot(gs[0, pp])
        ax_plot = fig.add_subplot(gs[1, pp])
        ax_mkr =  fig.add_subplot(gs[0, pp + 1])
        ax_sct =  fig.add_subplot(gs[1, pp + 1])
        
        # make background off white
        fig.patch.set_facecolor('whitesmoke')
        
        # PLOT BAR %-------------------------------------------------------------------%
        ax_bar.imshow( [list(np.arange(0, 1 , 1/N_bar))]*5, interpolation='nearest', origin='lower',
                          cmap = self.cmap, aspect = 'auto')
        ax_bar.set_title(self.name, size = 17, pad = 8 )
        
        # PLOT LINES & COLORS %--------------------------------------------------------%
        c = [self.cmap(_)[:-1] for _ in np.linspace(0, 1, N)]
        x = np.linspace(0, t, 100)
        widths = [2, 3, 4, 5, 6, 7, 8, 9]  # increasing thickness
        markers = ['.','o','s','^','*','D','$f$','p','o']  # markers to show
        flstl = ['full']*(len(markers)-1) + ['none']  # repeat markers for each color
        widths.reverse()
        for i in range(N):
            # For each color in the cmap we want to plot
            for _, thicc in enumerate(widths):  # do increasing thickness
                xtmp = x[0+_*2:_*2+3]
                ax_plot.plot(xtmp, np.sin(xtmp/f) + i*spacing, color = c[i], lw = thicc)
            
            # show different linestyles
            ax_plot.plot(x[len(widths)*2:61], np.sin(x[len(widths)*2:61]/f) + i*spacing, color = c[i], ls = 'solid')
            ax_plot.plot(x[60:71], np.sin(x[60:71]/f) + i*spacing , color = c[i], ls = 'solid')
            ax_plot.plot(x[70:81], np.sin(x[70:81]/f) + i*spacing , color = c[i], ls = 'dashed')
            ax_plot.plot(x[80:93], np.sin(x[80:93]/f) + i*spacing , color = c[i], ls = 'dashdot')
            ax_plot.plot(x[92:100], np.sin(x[92:100]/f) + i*spacing , color = c[i], ls = 'dotted')
            
            # do scatter plot
            x_sct = np.random.random(size = 5)
            y_sct = np.random.random(size = 5)
            ax_sct.scatter(x_sct, y_sct, color = c[i])
        
        # PLOT MARKERS %---------------------------------------------------------------%
        for _, mkr in enumerate(markers):
            if N >= 8:
                # to messy if many colors, so stick to first and last few
                ax_mkr.plot(_,-0.15, marker = mkr, color = c[0], fillstyle = flstl[_])
                ax_mkr.plot(_,-0.05, marker = mkr, color = c[3], fillstyle = flstl[_])
                ax_mkr.plot(_, 0.05, marker = mkr, color = c[-4], fillstyle = flstl[_])
                ax_mkr.plot(_, 0.15, marker = mkr, color = c[-1], fillstyle = flstl[_])
            elif N >= 4:
                # 4-8 colors, plot four with less spacing
                ax_mkr.plot(_,-0.15, marker = mkr, color = c[0], fillstyle = flstl[_])
                ax_mkr.plot(_,-0.05, marker = mkr, color = c[1], fillstyle = flstl[_])
                ax_mkr.plot(_, 0.05, marker = mkr, color = c[-2], fillstyle = flstl[_])
                ax_mkr.plot(_, 0.15, marker = mkr, color = c[-1], fillstyle = flstl[_])
            elif N == 3:
                # only plot three
                ax_mkr.plot(_,-0.15, marker = mkr, color = c[0], fillstyle = flstl[_])
                ax_mkr.plot(_, 0, marker = mkr, color = c[1], fillstyle = flstl[_])
                ax_mkr.plot(_, 0.15, marker = mkr, color = c[-1], fillstyle = flstl[_])
            elif N == 2:
                # plot two
                ax_mkr.plot(_,-0.1, marker = mkr, color = c[0], fillstyle = flstl[_])
                ax_mkr.plot(_, 0.1, marker = mkr, color = c[-1], fillstyle = flstl[_])
            else:
                # plot one
                ax_mkr.plot(_,0, marker = mkr, color = c[0], fillstyle = flstl[_])
        
        if mapBool:
            # PLOT MAP %---------------------------------------------------------------%
            ax_map =  fig.add_subplot(gs[:, 0])
            m = self.example_map(ax_map, N)
            ax_map.axis('off')
        
        # format axis to make it pretty!
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
        
        if savePath is None:
            plt.show()
        else:
            import os
            pathLoc = os.path.dirname(os.path.realpath(__file__)) + savePath + '\\hamMap_'+self.name+'.png'
            plt.savefig(pathLoc,dpi = 300)
            plt.show()
    
    def truncate(self, start = 0, stop = 1, n = 256, update = True, *args):
        """Create a new colormap from a reduced range of an existing map.

        Args:
            start (int, optional): Starting fraction from 0 to 1. Defaults to 0.
            stop (int, optional): Ending fraction from 0 to 1. Defaults to 1.
            n (int, optional): Sample resolution, reduce to creat linear discrete map. Defaults to 256.
            update (bool, optional): Update existing object to this new one, otherwise returns a new
                                     HamMap object. Defaults to True.

        Returns:
            HamMap: Custom colormap object.
        """
        new_name = 'truncate({n},{a:.2f},{b:.2f})'.format(n=self.cmap, a=start, b=stop)
        new_cmap = mcolors.LinearSegmentedColormap.from_list(new_name, self.cmap(np.linspace(start, stop, n)))
        if update is None:
            return new_cmap
        elif update:
            self.name = self.name + f"_truncate-{start}-{stop}"
            self.cmap = new_cmap
        else:
            return HamColor(self.name + f"_truncate-{start}-{stop}", new_cmap)
            
        return new_cmap
    
    def get_discrete(self, N: int = None, start: float = 0., stop: float = 1., makehex: bool = False):
        """Wrapper of self.truncate() method to create a discrete map.

        Args:
            N (int, optional): Number of colors. Defaults to initialized length.
            start (float, optional): Starting fraction of map [0, 1]. Defaults to 0.
            stop (int, optional): Starting fraction of map [0, 1]. Defaults to 1.
            makehex (bool, optional): If true returns a hex list instead of a colormap. Defaults to False.

        Returns:
            list: List of fractional [r, g, b, a] values.
            or
            list: List of hex values.
        """
        if N is None:
            N = self.init_len
        tmp_cmap = self.truncate(start, stop, update = None)
        output = tmp_cmap(np.linspace(0,1,N))
        if makehex:
            output = [mcolors.to_hex(_) for _ in output]
        return output
    
    def example_map(self, ax, N: int = None, shape_file = '\lpr_000b16a_e'):
        """Generate example map from a map of canada on a given matplotlib axis colored in N colors.

        Args:
            ax (plt.Axes): Axes to plot map on.
            N (int, optional): Number of colors, defaults to initialized length.
            shape_file (str, optional): Shape file name in '\map_files' subfolder to define map. Defaults to '\lpr_000b16a_e'.

        Returns:
            Basemap: Basemap opject describing the map plotted.
        """
        # mapping imports
        from mpl_toolkits.basemap import Basemap
        from matplotlib.patches import Polygon
        from matplotlib.collections import PatchCollection
        import os

        if N is None:
            N = self.init_len
        colors = self.get_discrete(N)
        
        try:
            shape_file = os.path.dirname(os.path.realpath(__file__)) + '\map_files' + shape_file
        except Exception as e:
            print('Error, basemap likely not found...')
            print(e)
        
        # generate basemap
        m = Basemap(projection = 'merc',llcrnrlon=-144,llcrnrlat=41,urcrnrlon=-51,urcrnrlat=83.7)
        m.readshapefile(shape_file,name = 'lpr_000b16a_e', default_encoding='iso-8859-15',
                        drawbounds=True)
        
        # color provinces as patches
        patches   = []
        np.random.shuffle(colors)
        for sn in range(13):  # 13 provinces
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
# print(colo.get_discrete())

def makeAllTests(cont = colmaps, disc = colsets, fileOutPath = '\\colour_demos', mapBool = 0):
    for key in cont:
        colo = HamColor(key,cont[key])
        colo.test(N = -8, mapBool = mapBool, savePath = fileOutPath)
    for key in disc:
        colo = HamColor(key,disc[key])
        colo.test(N = colo.init_len, mapBool = mapBool, savePath = fileOutPath)