"""
My custom plotting helper functions for day to day!
Created on Sat Aug 20 2023

@author: hamishj

Contributions 'borrowed' from:
 -
"""
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import numpy as np


# %----------------------------------------------------------------%
def despine(axis=None, trim: bool = False, drop: float = 0., noLine: bool = False, bottom: bool = True,
            left: bool = True, top: bool = False, right: bool = False):
    if type(axis) is type(None):
        axis = plt.gca()
    # Hide the specified spines
    axis.spines.right.set_visible(right)
    axis.spines.top.set_visible(top)
    axis.spines.bottom.set_visible(bottom)
    axis.spines.left.set_visible(left)

    # Stollen from seaborn git
    # https://github.com/mwaskom/seaborn/blob/master/seaborn/utils.py
    # line 375, accessed April 6, 2023
    if trim:
        # clip off the parts of the spines that extend past major ticks
        xticks = np.asarray(axis.get_xticks())
        if xticks.size:
            first_tick = np.compress(xticks >= min(axis.get_xlim()),
                                     xticks)[0]
            last_tick = np.compress(xticks <= max(axis.get_xlim()),
                                    xticks)[-1]
            axis.spines['bottom'].set_bounds(first_tick, last_tick)
            axis.spines['top'].set_bounds(first_tick, last_tick)
            new_ticks = xticks.compress(xticks <= last_tick)
            new_ticks = new_ticks.compress(new_ticks >= first_tick)
            axis.set_xticks(new_ticks)

        yticks = np.asarray(axis.get_yticks())
        if yticks.size:
            first_tick = np.compress(yticks >= min(axis.get_ylim()),
                                     yticks)[0]
            last_tick = np.compress(yticks <= max(axis.get_ylim()),
                                    yticks)[-1]
            axis.spines['left'].set_bounds(first_tick, last_tick)
            axis.spines['right'].set_bounds(first_tick, last_tick)
            new_ticks = yticks.compress(yticks <= last_tick)
            new_ticks = new_ticks.compress(new_ticks >= first_tick)
            axis.set_yticks(new_ticks)

    if drop:
        axis.spines.left.set_position(('outward', drop))
        axis.spines.bottom.set_position(('outward', drop))

    if noLine:
        for pos in ['bottom', 'left']:
            axis.spines[pos].set_visible(False)
    return None


def errorbands(x: np.ndarray, y: np.ndarray, yerr: np.ndarray, capsize: float = 0, ax=None, color=None, *args,
               **kwargs):
    """
    Wrapper of matplotlib fill_between which instead creates continuous colour bands that can be filled.

    TODO: Add interpolation types
    """
    if type(ax) is type(None):
        ax = plt.gca()
    low = y - yerr
    high = y + yerr
    poly = ax.fill_between(x, low, high, *args, facecolor=color, **kwargs)
    if capsize:
        ax.errorbar(x, y, yerr=yerr, capsize=capsize, color=color,
                    elinewidth=0, fmt='.')
    return poly


# !TODO: Move to a seperate helper file as a database of functions I use
def quad_fit(x, a, h, k=0):
    return a*(x-h)**2 + k

def gauss_fit(x, a, mu, sigma):
    return a*np.exp(-(x-mu)**2 / (x*sigma**2))

fit_methods = ['quadratic', 'gaussian']
fit_functions = {'quadratic': quad_fit,
                 'gaussian': gauss_fit,}

#  !TODO: Document and clean up
def make_great_triangle_of_confustion(df, names, value_column='log(SqErr)', markMin: bool = True,
                                      drawContours: bool = False, marginalHist: bool = True,
                                      contour_colour: str = 'magenta', squishy: bool = True, marginFits: list = None,
                                      cmap='viridis'):
    # Define spacing and scale
    inchPerAx = 3.4
    marginalRelativeHeight = 0.420  # make marginal plots half as tall as the squares
    nDim = len(names)
    cbarPadding = np.array([0.4, 0.1])

    # Define formatting parameters
    label_offset = -0.27
    label_fontsize = 16
    axis_padding = 0.05
    maxTicks = 8
    tickLabelRotation = 45
    grid_color = 'lightgrey'
    grid_style = '-'
    grid_width = 1
    grid_alpha = 0.6
    global_marker_colour = 'yellow'
    marker_colour = 'red'

    figWidth = nDim * (inchPerAx + 2*axis_padding)
    # add room for the marginal plot if needed
    if marginalHist:
        # add room for marginal histograms
        heights = np.concatenate([[inchPerAx*marginalRelativeHeight],
                                  inchPerAx*np.ones(shape=(nDim)) + 2*axis_padding,
                                  inchPerAx*cbarPadding])
        marginal_height = inchPerAx*marginalRelativeHeight
    else:
        heights = np.concatenate([inchPerAx*np.ones(shape=(nDim)) + 2*axis_padding, inchPerAx*cbarPadding])
        marginal_height = 0

    # Define figure to hold all components
    fig = plt.figure(figsize=(figWidth, marginal_height + figWidth + cbarPadding[0]*inchPerAx))
    fig.tight_layout()

    # Define global range for value displayed in GTC canvas
    z_values = df[value_column].to_numpy()
    max_z = np.nanmax(z_values)
    min_z = np.nanmin(z_values)

    # formatting parameters
    label_dict = {}

    # marginal hist fit list
    marginal_fit_results = None
    if type(marginFits) is type(None):
        pass
    elif len(marginFits) == 1:
        # duplicate the fit dict to fill nDims over all
        marginFits *= nDim
        marginal_fit_results = []
    elif len(marginFits) != nDim:
        # ensure length spans all dimensions
        raise ValueError(f"Ensure the length of 'marginFits' is either one (fit all the same) or matches the GTC dimensions ({nDim})")
    else:
        marginal_fit_results = []

    # create an N+1 x N grid to add a colourbar to the bottom row with an extra column of spacng for text
    if marginal_height:
        grid = gs.GridSpec(nDim + 3, nDim, fig, hspace=axis_padding, wspace=axis_padding, height_ratios=heights)
        y_offset_marginal = 1
    else:
        grid = gs.GridSpec(nDim + 2, nDim, fig, hspace=axis_padding, wspace=axis_padding, height_ratios=heights)
        y_offset_marginal = 0
    for i_x, param_x in enumerate(names):
        for i_y, param_y in enumerate(reversed(names[i_x:])):
            idx_x = nDim - i_y - 1 + y_offset_marginal
            idx_y = i_x
            ax = fig.add_subplot(grid[idx_x, idx_y])
            if idx_x == nDim - 1 + y_offset_marginal:
                ax.set_xlabel(param_x, fontsize=label_fontsize)#, labelpad=label_padding)
                if idx_y % 2 == 0:
                    ax.xaxis.set_label_coords(0.5, label_offset + 0.05)
                else:
                    ax.xaxis.set_label_coords(0.5, label_offset - 0.05)
            else:
                pass  # hide ticklabels
            if idx_y == 0:
                ax.set_ylabel(param_y, fontsize=label_fontsize)#, labelpad=label_padding)
                if idx_x % 2 == 0:
                    ax.yaxis.set_label_coords(label_offset + 0.05, 0.5)
                else:
                    ax.yaxis.set_label_coords(label_offset - 0.05, 0.5)
            else:
                pass  # hide ticklabels
            
            x_values = df[param_x].to_numpy()
            y_values = df[param_y].to_numpy()#[::-1]
            x_set = np.unique(x_values)
            y_set = np.unique(y_values)
            xx, yy = np.meshgrid(x_set, y_set)

            zz = np.full_like(xx, np.nan, dtype=float)
            zz_min = np.full_like(xx, np.nan, dtype=float)
            zz_max = np.full_like(xx, np.nan, dtype=float)
            zz_std = np.full_like(xx, np.nan, dtype=float)
            for i, x in enumerate(x_set):
                for j, y in enumerate(y_set):
                    partition = np.where(np.logical_and(np.where(x_values == x, 1, 0), np.where(y_values == y, 1, 0)), 1, 0)
                    # print()
                    z_values_ij = z_values[np.where(partition)]
                    mean_value = np.nanmean(z_values_ij)
                    if not np.isnan(mean_value):
                        zz[j, i] = mean_value
                        if marginalHist:
                            zz_min[j, i] = np.nanmin(z_values_ij)
                            zz_max[j, i] = np.nanmax(z_values_ij)
                            zz_std[j, i] = np.nanstd(z_values_ij)
            ax.invert_yaxis()
            # Decide how we want to scale the colourmap distributions
            if squishy:
                plt.pcolormesh(xx, yy, zz, vmin=min_z, vmax=max_z, zorder = 2, shading='nearest', cmap=cmap)
                xtick_locations = x_set
                ytick_locations = y_set
            else:
                plt.imshow(zz, vmin=min_z, vmax=max_z, aspect='auto', zorder = 2, interpolation='nearest', cmap=cmap)
                xtick_locations = np.array(list(range(len(x_set))))
                ytick_locations = np.array(list(range(len(y_set))))
            
            # Decide if we want to mark the minimum values
            if markMin:
                arg_min_sq = np.unravel_index(np.nanargmin(zz), zz.shape)
                arg_min_sq_global = np.unravel_index(np.nanargmin(z_values), z_values.shape)
                x_dim, y_dim = zz.shape

                y_min, x_min = arg_min_sq # divmod(arg_min_sq, x_dim)
                # y_min_g, x_min_g = arg_min_sq_global # divmod(arg_min_sq, x_dim)
                ax.scatter(xtick_locations[x_min], ytick_locations[y_min], marker='x', color=marker_colour, zorder=4, label = 'Local Min', linewidth=2,
                           s=90)

                if squishy:
                    xmin, ymin = x_values[arg_min_sq_global], y_values[arg_min_sq_global]
                    ax.scatter(xmin, ymin, marker='o', facecolors='none', color=global_marker_colour, zorder=3,
                               label = 'Global Min', s=100, linewidth=3)
                else:
                    # Global value needs to be handled differently if we rescale axis! caution!
                    print('Caution: For non-linear data scales, plotting global minima is disabled!')
                
            # Decide if we want to draw countour levels
            if drawContours:
                n_contours = int((np.nanmax(zz)-np.nanmin(zz))//np.nanstd(zz.ravel()) + 2)
                contours = ax.contour(xtick_locations, ytick_locations, zz, levels=n_contours, colors = contour_colour, linestyles='solid', label='Contour')

            # Draw the marginal histograms if desired
            if marginalHist:
                if idx_x -1 == idx_y:  # if on diagonal
                    mean_array = np.nanmean(zz, axis=0)
                    min_array = np.nanmean(zz_min, axis=0)
                    max_array = np.nanmean(zz_max, axis=0)
                    std_array = np.nanmean(zz_std, axis=0)
                    if idx_x-1 == 0:
                        # top most histogram
                        sub_grid = grid[idx_x - y_offset_marginal, idx_y].subgridspec(1, 2)
                    else:
                        num_y_zones = np.min([int(10/(10*marginalRelativeHeight)), 30])
                        sub_grid = grid[idx_x - y_offset_marginal, idx_y].subgridspec(num_y_zones, 2)
                    ax_m = fig.add_subplot(sub_grid[-1:,:])
                    ax_m.set(xticklabels=[], ylabel = value_column)
                    ax_m.scatter(xtick_locations, mean_array, marker='o', color='k')
                    ax_m.scatter(xtick_locations, min_array, marker='_', color='darkgray')
                    ax_m.scatter(xtick_locations, max_array, marker='_', color='darkgray')
                    ax_m.set_xlim(ax.get_xlim())
                    
                    if type(marginFits) is type(None):
                        # No request to fit margins, move on
                        pass
                    else:
                        margin_fit_dict = marginFits[idx_y]
                        if type(margin_fit_dict) is dict:
                            fitMethod = margin_fit_dict.get('method')
                            bounds = margin_fit_dict.get('bounds')
                            p0 = margin_fit_dict.get('p0')
                            
                            # load the fit method and p0s
                            f = fit_functions[fitMethod]
                            # If no p0 is provided, have to guess from function provided
                            if type(p0) is type(None):
                                N_param = len(signature(f).parameters) - 1
                                p0 = np.zeros(shape = (N_param)) + 1

                            # select the data to be fit, obtain bounds
                            x_data = x_set
                            y_data = mean_array
                            if type(bounds) is not type(None):
                                filter = np.argwhere(np.logical_and(bounds[0]<= x_data, x_data <= bounds[1])).ravel()
                            else:
                                filter = np.full(x_data.shape, True)

                            # run least squared fit
                            pOpt, pCov = curve_fit(f, x_data[filter], y_data[filter], p0 = p0, maxfev=1500)
                            error_vector = np.sqrt(np.diag(pCov))
                            best_fit_string = []
                            var_list = getfullargspec(f)[0]
                            for i, (arg, opt, err) in enumerate(zip(var_list, pOpt, error_vector)):
                                best_fit_string.append(f'{arg} = {opt:.2g} +/- {err:.2g}\n')
                            # print(best_fit_string)

                            if squishy:
                                x_model = np.linspace(np.min(x_data), np.max(x_data), 120, endpoint=True)
                                y_model = f(x_model, *pOpt)

                                # Save the yscale to reset after adding points
                                ylimits = ax_m.get_ylim()
                                ax_m.plot(x_model, y_model, ls='-', color='red', label = f'{fitMethod} fit', zorder = 1)
                                ax_m.set_ylim(ylimits)
                                
                                handles, labels = ax_m.get_legend_handles_labels()
                                for l, h in zip(labels, handles):
                                    label_dict[l] = h
                            else:
                                print('Caution: For non-linear data scales, plotting histogram fits is disabled')
                            marginal_fit_results.append([f, pOpt, pCov])
                        elif type(margin_fit_dict) != type(None):
                            # We have passed a nonexistant fit method
                            print(f"Provided invalid type of margin fitting dictionary, please provide None or a dictornary.")
                        else:
                            pass  # User provided none for this one so pass
                    ax_m.yaxis.set_label_position('right')
                    ax_m.yaxis.tick_right()
                    hp.despine(left=False, top=False, bottom=True, right=True)
                        
                else:
                    pass

            # Format ticks to never get too messy and
            # remove tick labels on inside dimension
            if len(x_set) <= maxTicks:
                ax.set_xticks(xtick_locations, x_set, rotation=tickLabelRotation) 
            else:
                # make smaller subset to plot
                chosen_idx = np.round(np.linspace(0, len(xtick_locations) - 1, len(xtick_locations)//2)).astype(int)
                chosen_ticks = x_set[chosen_idx]
                ax.set_xticks(xtick_locations[chosen_idx], chosen_ticks, rotation=tickLabelRotation)
            if idx_x != nDim - 1 + y_offset_marginal:
                ax.set(xticklabels=[])
    
            if len(y_set) <= maxTicks:
                ax.set_yticks(ytick_locations, y_set, rotation=tickLabelRotation) 
            else:
                # make smaller subset to plot
                chosen_idx = np.round(np.linspace(0, len(ytick_locations) - 1, len(ytick_locations)//2)).astype(int)
                chosen_ticks = y_set[chosen_idx]
                ax.set_yticks(ytick_locations[chosen_idx], chosen_ticks, rotation=tickLabelRotation)
            if idx_y != 0:
                ax.set(yticklabels=[])
    
            # add grindlines behind imshow
            ax.grid(which='major', color=grid_color, linestyle=grid_style, linewidth=grid_width, zorder = 1, alpha=grid_alpha)
            
            # Add any labels to legend if existing
            handles, labels = ax.get_legend_handles_labels()
            for l, h in zip(labels, handles):
                label_dict[l] = h
    
    cbarax = fig.add_subplot(grid[-1, :])
    plt.colorbar(label="log10(Squared Error)", orientation="horizontal", cax=cbarax)

    # Generate the legend
    # If we have only one parameter -> move legend to right to not overlap by one division
    ax_top_right = fig.add_subplot(grid[0, -1])
    if nDim > 1:
        ax_top_right.legend(label_dict.values(), label_dict.keys(), framealpha=0, loc='upper right', fontsize=16)
    else:
        # Manualy move bbox of legend to the right
        ax_top_right.legend(label_dict.values(), label_dict.keys(), framealpha=0, loc='upper right', fontsize=16,
                            bbox_to_anchor=[1.8,0])

    ax_top_right.axis('off')
    
    return fig, marginal_fit_results