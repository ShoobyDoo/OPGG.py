import argparse
from opgg.opgg import OPGG
from opgg.summoner import Summoner


def main():
    parser = argparse.ArgumentParser(description='A simple utility to pull some data from OPGG.',
                                    epilog="Compiled Usage: opgg_scraper.exe -r NA -s \"User1,User2,User3,User4,User5\"")

    parser.add_argument('-r', metavar='region', nargs='?', default='NA', help='Region to search in. Defaults to NA.')
    parser.add_argument('-s', metavar='summoners', nargs='?', help='Comma seperated list of summoners to look up. (Surround with quotes if any summoner name contains a space.)')

    args = parser.parse_args()


    if args.s:
        # Once we have those, we can create an OPGG object
        opgg = OPGG(None, args.r)
        summoner_ids = opgg.multi_search(args.s)
        
        summoners = []
        for summoner_id in summoner_ids:
            opgg.summoner_id = summoner_id
            summoners.append(opgg.get_summoner())
        
        summoner: Summoner
        for summoner in summoners:
            print(summoner)
        
        
if __name__ == "__main__":
    main()