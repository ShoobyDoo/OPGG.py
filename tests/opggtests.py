from opgg.opgg import OPGG
from opgg.season import SeasonInfo


class OPGGTests:
    """
    Represents a collection of tests for OPGG
    """
    
    @staticmethod
    def verify_seasoninfo(page_props: dict = None) -> bool:
        """
        Test the properties `SeasonInfo` has against what's returned by `page_props`
        
        ### Returns:
            `bool` - Returns `True` if test passed. Otherwise, returns `False`
        """
        
        print("Running test for SeasonInfo...\n")
        
        if not page_props: page_props = OPGG.get_page_props() # get latest
        
        msg = "Test was completed with {_pass} passes and {_fail} fails. See below for details:\n"
        msg_summary = ""
        
        latest_attrs = []
        seasoninfo_attrs = []
        
        pass_count = 0
        fail_count = 0
        
        for attr in dict(list(dict(page_props['seasonsById']).values())[0]).keys():
            print(f"SeasonInfo has {str(attr).ljust(25)}", end='')
            latest_attrs.append(attr)
            
            if hasattr(SeasonInfo, attr):
                print(": Pass ✔")
                pass_count += 1
                seasoninfo_attrs.append(attr)
            else:
                print(": FAIL ✘")
                fail_count += 1
        
        msg = msg.format(_pass=pass_count, _fail=fail_count)

        msg_summary += f"\nSeasonInfo has {len(seasoninfo_attrs)} attributes:\n"
        for attr in seasoninfo_attrs:
            msg_summary += f"    -> {attr}\n"
        
        msg_summary += f"\nLatest page_props has {len(latest_attrs)} attributes:\n"
        for attr in latest_attrs:
            msg_summary += f"    -> {attr}\n"
        
        msg_summary += f"\nLatest page_props has {len(latest_attrs) - len(seasoninfo_attrs)} more attributes than SeasonInfo:\n"
        for diffs in list(set(latest_attrs) - set(seasoninfo_attrs)):
            msg_summary += f"    -> {diffs}\n"
        
        msg_summary += f"\nAll checks have been completed.\nResult: {'PASS ✔' if fail_count == 0 else 'FAIL ✘'}"
        
        print(msg_summary)
        
        return True if fail_count == 0 else False