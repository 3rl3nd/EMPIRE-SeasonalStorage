import pandas as pd
import numpy as np
import os

def gather_season(data, season):
    if season=="winter":
        return data.loc[data.month.isin([12, 1, 2]), :]
    elif season=="spring":
        return data.loc[data.month.isin([3, 4, 5]), :]
    elif season=="summer":
        return data.loc[data.month.isin([6, 7, 8]), :]
    elif season=="fall":
        return data.loc[data.month.isin([9, 10, 11]), :]

def season_month(month_name):
    months = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12
    }
    return [months[month_name.lower()]]

def year_month_filter(data, sample_year, sample_month):
    data = data.loc[data.year.isin([sample_year]), :]
    data = data.loc[data.month.isin([sample_month]), :]
    return data

def remove_time_index(data):
    data = data.reset_index(drop=True)
    data = data.drop(['time', 'year', 'month', 'dayofweek', 'hour'], axis=1)
    return data


def filter_sample_year(data, sample_year):
    data["time"] = pd.to_datetime(data["time"])
    data['year'] = data['time'].dt.year
    data['month'] = data['time'].dt.month
    data['hour'] = data['time'].dt.hour
    data['dayofweek'] = data['time'].dt.dayofweek
    if sample_year != None:
        data = data.loc[data.year.isin(sample_year), :]
    return data

def make_datetime(data, time_format):
    data["time"] = pd.to_datetime(data["time"],
                                  format=time_format,
                                  exact=False)
    data['year'] = data['time'].dt.year
    data['month'] = data['time'].dt.month
    data['hour'] = data['time'].dt.hour
    data['dayofweek'] = data['time'].dt.dayofweek
    return data

def gather_regular_sample(data, season, seasons, weekHours,
                          sample_hour, hoursOfWeek):
    # data = gather_season(data=data, season=season)
    data = data.reset_index(drop=True)
    data = data.sort_values(by=['time','dayofweek','hour'])

    sample_data = data.iloc[sample_hour:sample_hour + weekHours,:]
    
    # Sort sample_data to start on midnight monday
    #sample_data = sample_data.sort_values(by=['time','dayofweek','hour'])
    
    # Drop non-country columns
    sample_data = remove_time_index(sample_data)
    
    hours = hoursOfWeek
    return [sample_data, hours]

def sample_generator(data, weekHours, branch, season, seasons,
                     period, generator, sample_hour, hoursOfWeek):
    [sample_data, hours] = gather_regular_sample(data, season, seasons,
                                                 weekHours,
                                                 sample_hour, hoursOfWeek)
    generator_data = pd.DataFrame()
    if generator=='Windoffshoregrounded' or generator=='Windoffshorefloating':
        startNOnode = 2
    else:
        startNOnode = 1
    for c in sample_data.columns:
        if c == "NO":
            for i in range(startNOnode, 6):
                c_no = c + str(i)
                df = pd.DataFrame(
                    data={'Node': c_no, "IntermitentGenerators": generator,
                          "Branch": branch,
                          "Operationalhour": hours,
                          "Period": period,
                          "GeneratorStochasticAvailabilityRaw": 
                              sample_data[c].values})
                generator_data = pd.concat([generator_data,df], ignore_index=True)
        else:
            df = pd.DataFrame(
                data={'Node': c, "IntermitentGenerators": generator,
                      "Branch": branch,
                      "Operationalhour": hours,
                      "Period": period,
                      "GeneratorStochasticAvailabilityRaw": 
                          sample_data[c].values})
            generator_data = pd.concat([generator_data,df], ignore_index=True)
    return generator_data

def sample_hydro(data, weekHours, branch, season,
                 seasons, period, sample_hour, hoursOfWeek):
    [sample_data, hours] = gather_regular_sample(data, season, seasons,
                                                 weekHours,
                                                 sample_hour, hoursOfWeek)
    hydro_data = pd.DataFrame()
    for c in sample_data.columns:
        if c != 'time':
            df = pd.DataFrame(
                data={'Node': c, "Period": period, "Branch": branch,
                      "Season": season,
                      "Operationalhour": hours, 
                      "HydroGeneratorMaxSeasonalProduction": 
                          sample_data[c].values})
            hydro_data = pd.concat([hydro_data,df], ignore_index=True)
    return hydro_data

def sample_load(data, weekHours, branch, season, seasons,
                period, sample_hour, hoursOfWeek):
    [sample_data, hours] = gather_regular_sample(data, season, seasons,
                                                 weekHours,
                                                 sample_hour, hoursOfWeek)
    load = pd.DataFrame()
    for c in sample_data.columns:
        if c != 'time':
            df = pd.DataFrame(
                data={'Node': c, "Period": period,
                      "Branch": branch, 
                      "Operationalhour": hours,
                      "ElectricLoadRaw_in_MW": sample_data[c].values})
            load = pd.concat([load,df], ignore_index=True)
    return load

def sample_h2_load(data, weekHours, branch, season, seasons,
                period, sample_hour, hoursOfWeek):
    [sample_data, hours] = gather_regular_sample(data, season, seasons,
                                                 weekHours,
                                                 sample_hour, hoursOfWeek)
    load = pd.DataFrame()
    for c in sample_data.columns:
        if c != 'time':
            df = pd.DataFrame(
                data={'Node': c, "Period": period,
                      "Branch": branch, 
                      "Operationalhour": hours,
                      "HydrogenLoadRaw_in_ton": sample_data[c].values})
            load = pd.concat([load,df], ignore_index=True)
    return load

def gather_peak_sample(data, season, seasons, weekHours, peakSeasonHours,
                       country_sample, overall_sample, HoursOfPeakSeason):
    data = data.reset_index(drop=True)
    country_peak = data.iloc[
        int(country_sample - (peakSeasonHours/2)):int(
            country_sample + (peakSeasonHours/2)),
        :]
    overall_peak = data.iloc[
        int(overall_sample - (peakSeasonHours/2)):int(
            overall_sample + (peakSeasonHours/2)),
        :]
    
    # Sort data to start on midnight 
    country_peak = country_peak.sort_values(by=['hour'])
    overall_peak = overall_peak.sort_values(by=['hour'])
    
    # Drop non-country columns
    country_peak = remove_time_index(country_peak)
    overall_peak = remove_time_index(overall_peak)
    
    # country_hours = list(
    #     range(1 + weekHours * len(seasons),
    #           weekHours * len(seasons) + peakSeasonHours + 1)
    #     )
    # overall_hours = list(
    #     range(1 + weekHours * len(seasons) + peakSeasonHours,
    #           weekHours * len(seasons) + 2 * peakSeasonHours + 1)
    #     )
    
    country_hours = list(
        range(min([number for key, number in HoursOfPeakSeason if key == 'peak1']),
                       max([number for key, number in HoursOfPeakSeason if key == 'peak1']) + 1))
    
    overall_hours = list(
        range(min([number for key, number in HoursOfPeakSeason if key == 'peak2']),
                       max([number for key, number in HoursOfPeakSeason if key == 'peak2']) + 1))
    
    if season == 'peak1':
        return [country_peak, country_hours]
    else:
        return [overall_peak, overall_hours]

def sample_hydro_peak(data, season, seasons, branch, period, weekHours,
                      peakSeasonHours, overall_sample, country_sample, HoursOfPeakSeason):
    peak_data = pd.DataFrame()
    [peak, hours] = gather_peak_sample(data, season, seasons,
                                                        weekHours,
                                                        peakSeasonHours,
                                                        country_sample,
                                                        overall_sample,
                                                        HoursOfPeakSeason)
    
    for c in peak.columns:
        df = pd.DataFrame(
            data={'Node': c, "Period": period, "Branch": branch,
                  "Season": season,
                  "Operationalhour": hours,
                  "HydroGeneratorMaxSeasonalProduction": 
                      peak[c].values})
        peak_data = pd.concat([peak_data,df], ignore_index=True)
    return peak_data

def sample_load_peak(data, season, seasons, branch, period, weekHours,
                     peakSeasonHours, overall_sample, country_sample, HoursOfPeakSeason):
    peak_data = pd.DataFrame()
    [peak, hours]= gather_peak_sample(data, season, seasons,
                                                        weekHours, 
                                                        peakSeasonHours, 
                                                        country_sample,
                                                        overall_sample,
                                                        HoursOfPeakSeason)
    for c in peak.columns:
        df = pd.DataFrame(
            data={'Node': c, "Period": period,
                  "Branch": branch,
                  "Operationalhour": hours,
                  "ElectricLoadRaw_in_MW": peak[c].values})
        peak_data = pd.concat([peak_data,df], ignore_index=True)
    return peak_data

def sample_generator_peak(data, season, seasons, g, branch,
                          period, weekHours, peakSeasonHours,
                          overall_sample, country_sample, HoursOfPeakSeason):
    peak_data = pd.DataFrame()
    [peak, hours] = gather_peak_sample(data, season, seasons,
                                                        weekHours,
                                                        peakSeasonHours, 
                                                        country_sample, 
                                                        overall_sample,
                                                        HoursOfPeakSeason)
    if g=='Windoffshoregrounded' or g=='Windoffshorefloating':
        startNOnode = 2
    else:
        startNOnode = 1
    for c in peak.columns:
        if c == "NO":
            for i in range(startNOnode, 6):
                c_no = c + str(i)
                df = pd.DataFrame(
                data={'Node': c_no, "IntermitentGenerators": g,
                      "Branch": branch,
                      "Operationalhour": hours,
                      "Period": period, 
                      "GeneratorStochasticAvailabilityRaw": 
                          peak[c].values})
                peak_data = pd.concat([peak_data,df], ignore_index=True)
        else:
            df = pd.DataFrame(
            data={'Node': c, "IntermitentGenerators": g, 
                  "Branch":branch,
                  "Operationalhour": hours,
                  "Period": period,
                  "GeneratorStochasticAvailabilityRaw": 
                      peak[c].values})
            peak_data = pd.concat([peak_data,df], ignore_index=True)
    return peak_data

def generate_random_scenario(filepath, tab_file_path, number_of_branches, parent_dictionary, season_dictionary, regular_seasons,
                             Periods, weekHours, weeksPerMonth, peakSeasonHours,
                             HoursOfRegSeason, HoursOfPeakSeason,
                             dict_countries,representative_countries,representative_countries_h2,HEATMODULE=False,
                             fix_sample=False,REDUCED_GEN=False):
    if fix_sample:
        print("Generating scenarios according to key...")
    else:
        print("Generating random scenarios...")

    # Generate dataframes to print as stochastic-files
    genAvail = pd.DataFrame()
    elecLoad = pd.DataFrame()
    h2Load = pd.DataFrame()
    hydroSeasonal = pd.DataFrame()

    if HEATMODULE:
        heatLoad = pd.DataFrame()
        cop = pd.DataFrame()
    
    # Load all the raw scenario data
    solar_data = pd.read_csv(filepath + "/solar.csv")
    windonshore_data = pd.read_csv(filepath + "/windonshore.csv")
    windoffshore_data = pd.read_csv(filepath + "/windoffshore.csv")
    hydrorunoftheriver_data = pd.read_csv(filepath + "/hydroror.csv")
    hydroseasonal_data = pd.read_csv(filepath + "/hydroseasonal.csv")
    electricload_data = pd.read_csv(filepath + "/electricload.csv")
    hydrogenload_data = pd.read_csv(filepath + "/hydrogenload.csv")

    if HEATMODULE:
        heatload_data = pd.read_csv(filepath + "/HeatModule/heatload.csv")
        cop_data = pd.read_csv(filepath + "/HeatModule/cop_ashp.csv")

    solar_data = make_datetime(solar_data, "%d/%m/%Y %H:%M")
    windonshore_data = make_datetime(windonshore_data, "%d/%m/%Y %H:%M")
    windoffshore_data = make_datetime(windoffshore_data, "%d/%m/%Y %H:%M")
    hydroror_data = make_datetime(hydrorunoftheriver_data, "%Y-%m-%d %H:%M")
    hydroseasonal_data = make_datetime(hydroseasonal_data, "%Y-%m-%d %H:%M")
    electricload_data = make_datetime(electricload_data, "%d/%m/%Y %H:%M")
    hydrogenload_data = make_datetime(hydrogenload_data, "%d/%m/%Y %H:%M")

    if HEATMODULE:
        heatload_data = make_datetime(heatload_data, "%Y-%m-%d %H:%M")
        cop_data = make_datetime(cop_data, "%Y-%m-%d %H:%M")

    if fix_sample:
        sampling_key = pd.read_csv(filepath + "/sampling_key.csv")
        sampling_key = sampling_key.set_index(['Period','Branch','Season'])
    else:
        sampling_key = pd.DataFrame(columns=['Period','Branch','Season','Year','Month','Hour'])

    for i in range(1,Periods+1):
        print('------------PERIOD '+str(i)+'------------')
        for branch  in range(1,number_of_branches+1):
            s = season_dictionary[branch]
            if s in regular_seasons:
                #print('------------PERIOD '+str(i)+'------------')
                #print('------------BRANCH '+str(branch)+'------------')
                #print('------------SEASON '+str(s)+'------------')
                ###################
                ##REGULAR SEASONS##
                ###################
                for month in season_month(s):

                    if fix_sample:
                        sample_year = sampling_key.loc[(i,branch,s),'Year']
                        sample_month = month #sampling_key.loc[(i,branch,s),'Month']
                    else:
                        # Get sample year (2015-2019) and month for each season/scenario
                        sample_year = np.random.choice(list(range(2015,2020)))
                        sample_month = month

                    for week in range(weeksPerMonth):
                        # Filter out the hours within the sample year
                        firstHourOfWeek = min([number for key, number in HoursOfRegSeason if key == s])
                        hoursOfWeek = list(range(firstHourOfWeek, firstHourOfWeek + weekHours))

                        solar_month = year_month_filter(solar_data,
                                                                sample_year,
                                                                sample_month)
                        windonshore_month = year_month_filter(windonshore_data,
                                                            sample_year,
                                                            sample_month)
                        windoffshore_month = year_month_filter(windoffshore_data,
                                                            sample_year,
                                                            sample_month)
                        hydroror_month = year_month_filter(hydroror_data,
                                                        sample_year,
                                                        sample_month)
                        hydroseasonal_month = year_month_filter(hydroseasonal_data,
                                                                sample_year,
                                                                sample_month)
                        electricload_month = year_month_filter(electricload_data,
                                                            sample_year,
                                                            sample_month)
                        hydrogenload_month = year_month_filter(hydrogenload_data,
                                                            sample_year,
                                                            sample_month)


                        if HEATMODULE:
                            heatload_month = year_month_filter(heatload_data,
                                                            sample_year,
                                                            sample_month)
                            cop_month = year_month_filter(cop_data,
                                                        sample_year,
                                                        sample_month)
                        if fix_sample:
                            sample_hour = sampling_key.loc[(i,branch,s),'Hour']
                        else:
                            sample_hour = np.random.randint(0, solar_month.shape[0] - weekHours - 1)
                            sampling_key = pd.concat([sampling_key, pd.Series({'Period': i,
                                                                'Branch': branch,
                                                                'Season': s,
                                                                'Year': sample_year,
                                                                'Month': sample_month,
                                                                'Hour': sample_hour}).to_frame().T],ignore_index=True)

                            # Sample generator availability for regular seasons
                        genAvail = pd.concat([genAvail,
                            sample_generator(data=solar_month,
                                        weekHours=weekHours,
                                        branch=branch, season=s,
                                        seasons=regular_seasons, period=i,
                                        generator="Solar",
                                        sample_hour=sample_hour,
                                        hoursOfWeek=hoursOfWeek)],ignore_index=True)
                        genAvail = pd.concat([genAvail,
                            sample_generator(data=windonshore_month,
                                        weekHours=weekHours,
                                        branch=branch, season=s,
                                        seasons=regular_seasons, period=i,
                                        generator="Windonshore",
                                        sample_hour=sample_hour,
                                        hoursOfWeek=hoursOfWeek)],ignore_index=True)
                        genAvail = pd.concat([genAvail,
                            sample_generator(data=windoffshore_month,
                                        weekHours=weekHours,
                                        branch=branch, season=s,
                                        seasons=regular_seasons, period=i,
                                        generator="Windoffshoregrounded",
                                        sample_hour=sample_hour,
                                        hoursOfWeek=hoursOfWeek)],ignore_index=True)
                        if REDUCED_GEN is False:
                            genAvail = pd.concat([genAvail,
                                sample_generator(data=windoffshore_month,
                                                weekHours=weekHours,
                                                branch=branch, season=s,
                                                seasons=regular_seasons, period=i,
                                                generator="Windoffshorefloating",
                                                sample_hour=sample_hour,
                                                hoursOfWeek=hoursOfWeek)],ignore_index=True)
                        genAvail = pd.concat([genAvail,
                            sample_generator(data=hydroror_month,
                                            weekHours=weekHours,
                                            branch=branch, season=s,
                                            seasons=regular_seasons, period=i,
                                            generator="Hydrorun-of-the-river",
                                            sample_hour=sample_hour,
                                            hoursOfWeek=hoursOfWeek)],ignore_index=True)

                        # Sample electric load for regular seasons
                        elecLoad = pd.concat([elecLoad,
                            sample_load(data=electricload_month,
                                    weekHours=weekHours,
                                    branch=branch, season=s,
                                    seasons=regular_seasons, period=i,
                                    sample_hour=sample_hour,
                                    hoursOfWeek=hoursOfWeek)],ignore_index=True)
                        
                        # Sample hydrogenload
                        h2Load = pd.concat([h2Load,
                            sample_h2_load(data=hydrogenload_month,
                                    weekHours=weekHours,
                                    branch=branch, season=s,
                                    seasons=regular_seasons, period=i,
                                    sample_hour=sample_hour,
                                    hoursOfWeek=hoursOfWeek)],ignore_index=True)

                        # Sample seasonal hydro limit for regular seasons
                        hydroSeasonal = pd.concat([hydroSeasonal,
                            sample_hydro(data=hydroseasonal_month,
                                    weekHours=weekHours,
                                    branch=branch, season=s,
                                    seasons=regular_seasons, period=i,
                                    sample_hour=sample_hour,
                                    hoursOfWeek=hoursOfWeek)],ignore_index=True)

                        # Sample HEATMODULE profiles
                        if HEATMODULE:
                            heatLoad = pd.concat([heatLoad,
                                sample_load(data=heatload_month,
                                            weekHours=weekHours,
                                            branch=branch, season=s,
                                            seasons=regular_seasons, period=i,
                                            sample_hour=sample_hour,
                                            hoursOfWeek=hoursOfWeek)],ignore_index=True)

                            cop = pd.concat([cop,
                                sample_generator(data=cop_month,
                                                weekHours=weekHours,
                                                branch=branch, season=s,
                                                seasons=regular_seasons, period=i,
                                                generator="HeatPumpAir",
                                                sample_hour=sample_hour,
                                                hoursOfWeek=hoursOfWeek)],ignore_index=True)
                    
            ################
            ##PEAK SEASONS##
            ################
            else:
            # Get peak sample year (2015-2019)
                sample_year = np.random.choice(list(range(2015,2020)))

                if fix_sample:
                    sample_year = sampling_key.loc[(i,branch,s),'Year']
                else:
                    sampling_key = pd.concat([sampling_key,pd.Series({'Period': i,
                                                        'Branch': branch,
                                                        'Season': s,
                                                        'Year': sample_year,
                                                        'Month': 0,
                                                        'Hour': 0}).to_frame().T],
                                                        ignore_index=True)

                solar_data_year = solar_data.loc[solar_data.year.isin([sample_year]), :]
                windonshore_data_year = windonshore_data.loc[windonshore_data.year.isin([sample_year]), :]
                windoffshore_data_year = windoffshore_data.loc[windoffshore_data.year.isin([sample_year]), :]
                hydroror_data_year = hydroror_data.loc[hydroror_data.year.isin([sample_year]), :]
                hydroseasonal_data_year = hydroseasonal_data.loc[hydroseasonal_data.year.isin([sample_year]), :]
                electricload_data_year = electricload_data.loc[electricload_data.year.isin([sample_year]), :]

                if HEATMODULE:
                    heatload_year = heatload_data.loc[heatload_data.year.isin([sample_year])]
                    cop_year = cop_data.loc[cop_data.year.isin([sample_year])]
                
                #Peak1: The highest load when all loads are summed together
                electricload_data_year_notime = remove_time_index(electricload_data_year)
                overall_sample = electricload_data_year_notime.sum(axis=1).idxmax()
                #Peak2: The highest load of a single country
                max_load_country = electricload_data_year_notime.max().idxmax()
                country_sample = electricload_data_year_notime[max_load_country].idxmax()

                #Sample generator availability for peak seasons
                genAvail = pd.concat([genAvail,
                    sample_generator_peak(data=solar_data_year, season=s,
                                        seasons=regular_seasons,
                                        g="Solar", branch=branch, period=i,
                                        weekHours=weekHours,
                                        peakSeasonHours=peakSeasonHours,
                                        overall_sample=overall_sample,
                                        country_sample=country_sample,
                                        HoursOfPeakSeason=HoursOfPeakSeason)],ignore_index=True)
                genAvail = pd.concat([genAvail,
                    sample_generator_peak(data=windonshore_data_year, season=s,
                                        seasons=regular_seasons, 
                                        g="Windonshore", branch=branch, 
                                        period=i, 
                                        weekHours=weekHours,
                                        peakSeasonHours=peakSeasonHours,
                                        overall_sample=overall_sample, 
                                        country_sample=country_sample,
                                        HoursOfPeakSeason=HoursOfPeakSeason)],ignore_index=True)
                genAvail = pd.concat([genAvail,
                    sample_generator_peak(data=windoffshore_data_year, season=s,
                                        seasons=regular_seasons, 
                                        g="Windoffshoregrounded", branch=branch,
                                        period=i, 
                                        weekHours=weekHours, 
                                        peakSeasonHours=peakSeasonHours, 
                                        overall_sample=overall_sample, 
                                        country_sample=country_sample,
                                        HoursOfPeakSeason=HoursOfPeakSeason)],ignore_index=True)
                if REDUCED_GEN is False:
                    genAvail = pd.concat([genAvail,
                        sample_generator_peak(data=windoffshore_data_year, season=s,
                                            seasons=regular_seasons, 
                                            g="Windoffshorefloating", branch=branch,
                                            period=i, 
                                            weekHours=weekHours, 
                                            peakSeasonHours=peakSeasonHours, 
                                            overall_sample=overall_sample, 
                                            country_sample=country_sample,
                                            HoursOfPeakSeason=HoursOfPeakSeason)],ignore_index=True)
                genAvail = pd.concat([genAvail,
                    sample_generator_peak(data=hydroror_data_year, season=s,
                                        seasons=regular_seasons, 
                                        g="Hydrorun-of-the-river",
                                        branch=branch, period=i, 
                                        weekHours=weekHours,
                                        peakSeasonHours=peakSeasonHours,
                                        overall_sample=overall_sample, 
                                        country_sample=country_sample,
                                        HoursOfPeakSeason=HoursOfPeakSeason)],ignore_index=True)
                
                #Sample electric load for peak seasons
                elecLoad = pd.concat([elecLoad,
                    sample_load_peak(data=electricload_data_year, season=s,
                                    seasons=regular_seasons,
                                    branch=branch, period=i, 
                                    weekHours=weekHours, 
                                    peakSeasonHours=peakSeasonHours,
                                    overall_sample=overall_sample, 
                                    country_sample=country_sample,
                                    HoursOfPeakSeason=HoursOfPeakSeason)],ignore_index=True)
                
                #Sample seasonal hydro limit for peak seasons
                hydroSeasonal = pd.concat([hydroSeasonal,
                    sample_hydro_peak(data=hydroseasonal_data_year, season=s,
                                    seasons=regular_seasons,
                                    branch=branch, period=i, 
                                    weekHours=weekHours, 
                                    peakSeasonHours=peakSeasonHours,
                                    overall_sample=overall_sample, 
                                    country_sample=country_sample,
                                    HoursOfPeakSeason=HoursOfPeakSeason)],ignore_index=True)

                # Sample HEATMODULE profiles
                if HEATMODULE:
                    heatLoad = pd.concat([heatLoad,
                        sample_load_peak(data=heatload_year, season=s,
                                        seasons=regular_seasons,
                                        branch=branch, period=i,
                                        weekHours=weekHours,
                                        peakSeasonHours=peakSeasonHours,
                                        overall_sample=overall_sample,
                                        country_sample=country_sample,
                                        HoursOfPeakSeason=HoursOfPeakSeason)],ignore_index=True)

                    cop = pd.concat([cop,
                        sample_generator_peak(data=cop_year, season=s,
                                            seasons=regular_seasons,
                                            g="HeatPumpAir",
                                            branch=branch, period=i,
                                            weekHours=weekHours,
                                            peakSeasonHours=peakSeasonHours,
                                            overall_sample=overall_sample,
                                            country_sample=country_sample,
                                            HoursOfPeakSeason=HoursOfPeakSeason)],ignore_index=True)

    #Replace country codes with country names
    genAvail = genAvail[genAvail['Node'].isin(representative_countries)]
    genAvail = genAvail.replace({"Node": dict_countries})

    elecLoad = elecLoad[elecLoad['Node'].isin(representative_countries)]
    elecLoad = elecLoad.replace({"Node": dict_countries})

    h2Load = h2Load[h2Load['Node'].isin(representative_countries_h2)]
    h2Load = h2Load.replace({"Node": dict_countries})

    hydroSeasonal = hydroSeasonal.replace({"Node": dict_countries})
    hydroSeasonal = hydroSeasonal.groupby(['Node', 'Period', 'Branch', 'Season', 'Operationalhour']).sum().reset_index()
    if HEATMODULE:
        heatLoad = heatLoad.replace({"Node": dict_countries})
        cop = cop.replace({"Node": dict_countries})

    #Make header for .tab-file
    genAvail = genAvail[["Node", "IntermitentGenerators",
                         "Branch", "Operationalhour", "Period",
                         "GeneratorStochasticAvailabilityRaw"]]
    elecLoad = elecLoad[["Node", "Period", "Branch", "Operationalhour",
                         'ElectricLoadRaw_in_MW']]
    h2Load = h2Load[["Node", "Period", "Branch", "Operationalhour",
                         'HydrogenLoadRaw_in_ton']]
    hydroSeasonal = hydroSeasonal[["Node", "Period", "Branch", "Season", 
                                   "Operationalhour", 
                                   "HydroGeneratorMaxSeasonalProduction"]]

    if HEATMODULE:
        heatLoad = heatLoad[["Node", "Branch", "Operationalhour", "Period",
                             'ElectricLoadRaw_in_MW']]
        cop = cop[["Node", "IntermitentGenerators", "Period",
                   "Branch", "Operationalhour", "GeneratorStochasticAvailabilityRaw"]]

    #Make filepath (if it does not exist) and print .tab-files
    if not os.path.exists(tab_file_path):
        os.makedirs(tab_file_path)

    # Save sampling key
    if fix_sample:
        sampling_key = sampling_key.reset_index(level=['Period','Branch', 'Season'])

    sampling_key.to_csv(
        tab_file_path + "/sampling_key" + '.csv',
        header=True, index=None, mode='w')

    genAvail.to_csv(
        tab_file_path + "/Stochastic_StochasticAvailability" + '.tab',
        header=True, index=None, sep='\t', mode='w')
    elecLoad.to_csv(
        tab_file_path + "/Stochastic_ElectricLoadRaw" + '.tab',
        header=True, index=None, sep='\t', mode='w')
    h2Load.to_csv(
        tab_file_path + "/Stochastic_HydrogenLoadRaw" + '.tab',
        header=True, index=None, sep='\t', mode='w')
    hydroSeasonal.to_csv(
        tab_file_path + "/Stochastic_HydroGenMaxSeasonalProduction" + '.tab',
        header=True, index=None, sep='\t', mode='w')

    if HEATMODULE:
        if not os.path.exists(tab_file_path + "/HeatModule"):
            os.makedirs(tab_file_path + "/HeatModule")
        heatLoad.to_csv(
            tab_file_path + "/HeatModule/HeatModuleStochastic_HeatLoadRaw.tab",
            header=True, index=None, sep='\t', mode='w')
        cop.to_csv(
            tab_file_path + "/HeatModule/HeatModuleStochastic_ConverterAvail.tab",
            header=True, index=None, sep='\t', mode='w')