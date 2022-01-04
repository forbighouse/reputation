import mapclassify
import numpy as np
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import colors

from origin_data_process import delete_locationids, print_one_day, read_zone_by_borough
plt.rcParams["font.family"] = "SimHei"  # 设置全局中文字体为黑体


def extract_from_shp(_day, _hour, location):
    #  2020年12月_day日_hour时
    zone_num, all_vehicle = print_one_day(_day, _hour, 20)
    #  好像是把zone和数量的键值对结构转化成pandas的DataFrame
    df = pd.DataFrame(pd.Series(zone_num), columns=['num'])
    #  把index变为locationID
    df = df.reset_index().rename(columns={'index': 'LocationID'})
    new_location = location.merge(df, on='LocationID', how='outer')
    new_location['num'].fillna(0, inplace=True)

    #  设置想要的zone
    #  Bronx, Brooklyn, Manhattan, Queens
    zone_name = ['Manhattan']
    _list, _other_list = read_zone_by_borough(zone_name)
    #  删除掉不想要的location区域
    new_location = delete_locationids(new_location, _other_list)
    print(new_location.head())
    return new_location


def first_pic():
    sf = gpd.read_file("./taxi_zones/taxi_zones.shp", encoding='utf-8').to_crs({'init': 'epsg:4326'})
    location = sf[['LocationID', 'geometry']]
    #  从指定的文件中读取车辆分布数据
    new_location08 = extract_from_shp(20, 8, location)
    new_location12 = extract_from_shp(20, 12, location)
    new_location15 = extract_from_shp(20, 15, location)
    new_location21 = extract_from_shp(20, 21, location)

    vmin = 0
    vmax = 293
    norm1 = colors.Normalize(0, 5)
    norm2 = colors.Normalize(0, 7)

    fig, axes = plt.subplots(1, 4, figsize=(14, 7))


    # 移除坐标轴
    axes[0].axis('off')
    axes[1].axis('off')
    axes[2].axis('off')
    axes[3].axis('off')

    legend_kwds08 = {'loc': 'lower right', 'title': '2020.12.20 07-08', 'shadow': True}
    legend_kwds12 = {'loc': 'lower right', 'shadow': True}
    legend_kwds15 = {'loc': 'lower right', 'title': '2020.12.20 14-15', 'shadow': True}
    legend_kwds21 = {'loc': 'lower right', 'title': '2020.12.20 20-21', 'shadow': True}

    # bb = (fig.subplotpars.left, fig.subplotpars.top + 0.02,
    #       fig.subplotpars.right - fig.subplotpars.left, .1)


    # new_location08.plot(column='num', cmap='OrRd', scheme='NaturalBreaks', legend=True, legend_kwds=legend_kwds08,
    #                   edgecolor='0.5', ax=ax1, k=5)
    # new_location12.plot(column='num', cmap='OrRd', scheme='NaturalBreaks', legend=True, legend_kwds=legend_kwds12,
    #                   edgecolor='0.5', ax=ax2, k=5)
    # new_location15.plot(column='num', cmap='OrRd', scheme='NaturalBreaks', legend=True, legend_kwds=legend_kwds15,
    #                   edgecolor='0.5', ax=ax3, k=5)
    # new_location21.plot(column='num', cmap='OrRd', scheme='NaturalBreaks', legend=True, legend_kwds=legend_kwds21,
    #                   edgecolor='0.5', ax=ax4, k=5)

    new_location08.plot(column='num', cmap='OrRd', scheme='FisherJenks', edgecolor='0.5', k=3, ax=axes[0], norm=norm2)
    new_location12.plot(column='num', cmap='OrRd', scheme='FisherJenks', edgecolor='0.5', ax=axes[1], norm=norm1)
    new_location15.plot(column='num', cmap='OrRd', scheme='FisherJenks', edgecolor='0.5', ax=axes[2], norm=norm1)
    new_location21.plot(column='num', cmap='OrRd', scheme='FisherJenks', edgecolor='0.5', k=3, ax=axes[3], norm=norm2)
    axes[0].set_title('07:00 - 08:00')
    axes[1].set_title('11:00 - 12:00')
    axes[2].set_title('14:00 - 15:00')
    axes[3].set_title('20:00 - 21:00')
    # plt.suptitle('2020.12.20')


    # patch_col = ax2.collections[1]
    # fig.colorbar(patch_col, ax=[ax1, ax2, ax3, ax4])

    # cmaps['Sequential'] = [
    #             'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
    #             'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
    #             'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']
    # 图例
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.25, 0.01, 0.5])

    sm = plt.cm.ScalarMappable(cmap='OrRd')
    cbar = fig.colorbar(sm, cax=cbar_ax)
    bins = mapclassify.FisherJenks(new_location12['num'], 5).bins
    bins = np.insert(bins, 0, 0)
    _ = cbar.ax.set_yticklabels(bins)
    # fig.tight_layout()
    plt.show()
    fig.savefig(os.path.join('output', 'fist.pdf'), format='pdf', bbox_inches='tight', dpi=300)



if __name__ == '__main__':
    first_pic()
