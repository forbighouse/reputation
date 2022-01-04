import csv
import datetime
from utility import rec_dd, random_int_list, calculate


def read_zone_by_borough(borough):
    """
    从taxi+_zone_lookup.csv中按区块名返回locationID
    :param borough:    想要的区块列表
    :return:           想要的locationID的列表, 其他的locationID的列表
    """
    if not len(borough):
        print("In Function {}, input list is empty".format(__name__))
        return 0
    file = "data/taxi+_zone_lookup.csv"
    _re_in_borough = []
    _re_out_borough = []
    with open(file, 'rt') as f:
        reader = csv.reader(f)
        head = next(reader)
        for row in reader:
            for i in borough:
                if row[1] == i:
                    _re_in_borough.append(int(row[0]))
                else:
                    _re_out_borough.append(int(row[0]))
    return _re_in_borough, _re_out_borough


def split_by_day():
    file = "data/yellow_tripdata_2020-12.csv"
    out_month = 12
    out_day = 18

    location_dict = rec_dd()
    writer_content = []

    for j in range(19, 21):
        hours_zone = rec_dd()
        out_day = j
        for i in range(0, 24):
            hours_zone[i] = []

        print("Reading ~~~~~~~ date", str(out_month) + "-" + str(out_day))  # 7-th pick-up, 8-th put-down

        with open(file, 'rt') as f:
            reader = csv.reader(f)
            head = next(reader)
            for row in reader:
                time0 = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                if time0.date().month == out_month:
                    if time0.date().day == out_day:
                        hours_zone[int(time0.time().hour)].append(row[7])

                time1 = datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
                if time1.date().month == out_month:
                    if time1.date().day == out_day:
                        hours_zone[int(time1.time().hour)].append(row[8])

        print("Start to write")  # 7-th pick-up, 8-th put-down

        for i in hours_zone.keys():
            file = "./" + str(out_day) + "/2020-12_" + str(out_day) + "_" + str(i) + ".csv"
            with open(file, 'w', encoding='utf8', newline='') as csvfile:
                fieldnames = ['zone']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for itms in hours_zone[i]:
                    writer.writerow({'zone': itms})

            csvfile.close()


def read_by_day(read_date):
    location_dict = rec_dd()
    day_vehicle = rec_dd()
    for i in range(0, 24):
        file = "./data/" + str(read_date) + "/2020-12_" + str(read_date) + "_" + str(i) + ".csv"
        totall_vehicle = 0
        with open(file, 'rt') as f:
            reader = csv.reader(f)
            head = next(reader)
            for row in reader:
                if row[0] not in location_dict[i].keys():
                    location_dict[i][row[0]] = 1
                else:
                    location_dict[i][row[0]] += 1
                totall_vehicle += 1
        day_vehicle[i] = totall_vehicle
    return location_dict, day_vehicle


def print_one_day(read_date=14, read_clock=14, upper=20):
    """
    获取某一天的某一具体时刻的车辆分布
    :param upper:        输出的区块条件，当区块内车的数量大于upper时就显示
    :param read_date:    具体某一天，默认12月14号
    :param read_clock:   具体某一个时刻，默认下午14点
    :return:   分区和其中的车数量、 车辆总数
    """
    location, tatoll_num = read_by_day(read_date)
    num_all_vehicle = 0
    num_zone = 0
    list_vehicle_each_zone = []
    dict_zone_num = rec_dd()
    # for i in range(0, 24):
    #     print(i, " ", "Partitions: ", len(location[i].keys()), " ", "Vehicles: ", totall_num[i])
    for zone, num in location[read_clock].items():
        if num > upper:
            num_all_vehicle += num
            num_zone += 1
            list_vehicle_each_zone.append(num)
            dict_zone_num[int(zone)] = num
            print("zone:  {:<5}, num:  {:<5}".format(zone, num))
    #  显示统计结果
    sum_min, sum_mean, sum_max, sum_std, sum_med, sum_ppf = calculate(list_vehicle_each_zone, 0.95)
    print("")
    print("[RESULT] Day （", read_date, ")", "Time", "(", read_clock, ")")
    print("      SUM MIN           : ", int(sum_min))
    print("      SUM MEAN          : ", int(sum_mean))
    print("      SUM MAX           : ", int(sum_max))
    print("      SUM MED           : ", int(sum_med))
    print("      SUM PPF(0.95)     : ", int(sum_ppf))
    print("      nZone:            : ", num_zone)
    print("      nAllVehicleNum    : ", num_all_vehicle)
    print("")

    return dict_zone_num, num_all_vehicle


def delete_locationids(geo_df, ids):
    """
    根据LocationID删除数据
    :param : geo_df GeoDataFrame类型数据
    :param : ids  列表，元素为LocationID
    :return:   删除过的GeoDataFrame类型数据
    """
    if not ids:
        pass
    else:
        for id in ids:
            geo_df.drop(geo_df[geo_df['LocationID'] == id].index, inplace=True)
    return geo_df
