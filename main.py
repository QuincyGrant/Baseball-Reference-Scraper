import baseball_scraper as bs


def main():

    years = bs.get_years()
    df = bs.get_data(years[0], years[1])

    print(df.head())
    print(df.tail())

    print("Dataset contains {} rows and {} columns \n".format(len(df), len(df.columns)))

    filename = input("Enter filename: ")
    df.to_csv("~/Documents/Data/{}".format(filename))

    return 0


if __name__ == "__main__":

    main()
