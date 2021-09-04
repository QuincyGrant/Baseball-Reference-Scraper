from bs4 import BeautifulSoup, Comment
import pandas as pd
import time
import requests


def get_years():

    print("Enter in the range of seasons (years)...")
    y1 = int(input("From: "))
    y2 = int(input("To: "))
    print("Gathering data from the {} through {} seasons...".format(y1, y2))

    return(y1,y2)


def batting_stats(bstat, batting_table):
    tables = batting_table.find_all("td", attrs={"data-stat": bstat})

    b_stats = []
    for table in tables:
        b_stat = table.text
        b_stat = float(b_stat)
        b_stats.append(b_stat)

    b_stats = b_stats[:-2]  # exclude total and average

    return b_stats


def pitching_stats(pstat, pitching_table):
    tables = pitching_table.find_all("td", attrs={"data-stat": pstat})

    p_stats = []
    for table in tables:
        p_stat = table.text
        if p_stat == '':
            p_stat = "empty"
        else:
            p_stat = float(p_stat)

        p_stats.append(p_stat)

    p_stats = p_stats[:-2]

    return p_stats


def postseason(team_names, yr):  # 1 if a team made the playoff that year 0 if not
    playoff_teams = []

    go = True
    while go:
        team = input("Enter playoff teams for {}. Enter any number when all are in \n".format(yr))
        playoff_teams.append(team)

        if team.isdigit():
            go = False
            print("{} Postseason teams: ".format(yr), playoff_teams[:-1])
        else:
            print(playoff_teams)

    playoff = []
    for a in range(0, len(team_names)):
        if team_names[a] in playoff_teams:
            playoff.append(1)
        else:
            playoff.append(0)

    return playoff


def get_data(year1, year2):

    all_years = []
    leagues = ("NL","AL")

    for league in leagues:
        for year in range(year1, year2+1):

            url = "https://www.baseball-reference.com/leagues/{}/{}.shtml".format(league,year)
            headers = {'user-agent': "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.text, 'lxml')

            # doesn't work,cant find table on website.. returns NONE
            #pitching_table = soup.find("div", attrs={"id": "teams_standard_pitching"})

            batting_table = soup.find("div", attrs={"id": "div_teams_standard_batting"})

            comments = soup.find_all(text=lambda text: isinstance(text, Comment))
            indices = [i for i, s in enumerate(comments) if 'div_teams_standard_pitching' in s]

            pitching_html = comments[indices[0]]
            pitching_table = BeautifulSoup(pitching_html, 'lxml')

            #Use if pitching data isn't getting pulled to locate the index, it may change
            # ('Command(ctrl) + /' <- comment shortcut)

            # count = 0
            # for comment in comments:
            #    print(count)
            #    print("--------------------------")
            #    print(comment)
            #    count+=1

           # Creating columns for team names, year, and league
            name_table = batting_table.find_all("th", attrs={"data-stat": "team_name"})
            names = []
            for name in name_table:  # Get team names
                n = name.text
                names.append(n)
            names = names[:-2]
            names = names[1:]

            years = []
            for i in range(0, len(names)):  # Get the year of the season
                years.append(year)

            lg = []
            for j in range(0,len(names)):
                if league == 'NL':
                    lg.append(1)
                else:
                    lg.append(0)

            # If the team made the postseason
            # playoffs = postseason(names, year)
            # b_dict = {'Tm': names, 'Yr': years, 'Playoff': playoffs}
            # p_dict = {'Tm': names, 'Yr': years, 'Playoff': playoffs}

            b_dict = {'Tm': names, 'Yr': years}
            p_dict = {'Tm': names, 'Yr': years, 'NL': lg}

            b_stat_names = ['batters_used', 'age_bat', 'runs_per_game', 'G', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI',
                            'SB', 'CS', 'BB', 'SO', 'batting_avg', 'onbase_perc', 'slugging_perc', 'onbase_plus_slugging',
                            'TB'
                , 'GIDP', 'HBP', 'SH', 'SF', 'IBB', 'LOB']

            p_stat_names = ['pitchers_used', 'age_pitch', 'runs_allowed_per_game', 'W', 'L', 'win_loss_perc',
                            'earned_run_avg',
                            'G', 'GS', 'GF', 'CG', 'SHO_team', 'SHO_cg', 'SV', 'IP', 'H', 'R', 'ER', 'HR', 'BB', 'IBB',
                            'SO',
                            'HBP', 'BK', 'WP', 'batters_faced', 'fip', 'whip', 'hits_per_nine', 'home_runs_per_nine',
                            'bases_on_balls_per_nine', 'strikeouts_per_nine', 'strikeouts_per_base_on_balls', 'LOB']

            for x in p_stat_names:
                p_dict[x] = pitching_stats(x, pitching_table)

            for i in b_stat_names:
                b_dict[i] = batting_stats(i, batting_table)

            print("{} season done".format(year,league))

            df_batting = pd.DataFrame.from_dict(b_dict)
            df_pitching = pd.DataFrame.from_dict(p_dict)
            df_batting_pitching = df_pitching.merge(df_batting, on=['Yr', 'Tm'], how='left',
                                                    suffixes=('_pitching', '_batting'))
            all_years.append(df_batting_pitching)

            time.sleep(6)

    df = pd.concat(all_years, ignore_index=True)

    return df
