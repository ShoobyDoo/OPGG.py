from opgg.opgg import OPGG
from opggtests import OPGGTests


def main():
    # Call page props once so it doesnt have to be called each time 
    page_props = OPGG.get_page_props("ColbyFaulkn1")
    results = [OPGGTests.verify_seasoninfo(page_props), OPGGTests.verify_champion(page_props)]
    
    test_count = len(results)
    passed_count = sum(results)
    failed_count = test_count - passed_count
    
    print(f"Summary: {passed_count} of {test_count} tests passed. {failed_count} tests failed.\n\n")


if __name__ == "__main__":
    main()
