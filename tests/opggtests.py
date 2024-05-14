import time
from opgg.opgg import OPGG
from opgg.season import SeasonInfo
from opgg.champion import Champion


class OPGGTests:
    """
    Represents a collection of tests for OPGG
    """
    
    @staticmethod
    def verify_seasoninfo(page_props: dict = None, summoner: str = "ColbyFaulkn1") -> bool:
        """
        Test the properties `SeasonInfo` has against what's returned by `page_props`
        
        ### Returns:
            `bool` - `True` if test passed. Otherwise, returns `False`
        """
        test_for = "SeasonInfo"
        
        print(f"Running test for {test_for}...\n")
        
        if not page_props: page_props = OPGG.get_page_props(summoner) # get latest
        
        msg = "Test was completed with {_pass} passes and {_fail} fails. See below for details:\n"
        msg_summary = ""
        
        latest_attrs = []
        obj_attrs = []
        
        pass_count = 0
        fail_count = 0
        
        for attr in dict(list(dict(page_props['seasonsById']).values())[0]).keys():
            print(f"{test_for} has {str(attr).ljust(25)}", end='')
            latest_attrs.append(attr)
            
            if hasattr(SeasonInfo, attr):
                print(": Pass ✔")
                pass_count += 1
                obj_attrs.append(attr)
            else:
                print(": FAIL ✘")
                fail_count += 1
            
            # slow print effect
            time.sleep(0.1)
        
        msg = msg.format(_pass=pass_count, _fail=fail_count)

        msg_summary += f"\n{test_for} has {len(obj_attrs)} attributes:\n"
        for attr in obj_attrs:
            msg_summary += f"    -> {attr}\n"
        
        msg_summary += f"\nLatest page_props has {len(latest_attrs)} attributes:\n"
        for attr in latest_attrs:
            msg_summary += f"    -> {attr}\n"
        
        msg_summary += f"\nLatest page_props has {len(latest_attrs) - len(obj_attrs)} more attributes than {test_for}:\n"
        for diffs in list(set(latest_attrs) - set(obj_attrs)):
            msg_summary += f"    -> {diffs}\n"
        
        msg_summary += f"\nAll checks for '{test_for}' have been completed.\nResult: {'PASS ✔' if fail_count == 0 else 'FAIL ✘'}\n\n"
        
        print(msg_summary)
        
        return True if fail_count == 0 else False
    
    
    @staticmethod
    def verify_champion(page_props: dict = None, summoner: str = "ColbyFaulkn1") -> bool:
        """
        Test the properties `Champion` has against what's returned by `page_props`
        
        ### Returns:
            `bool` - `True` if test passed. Otherwise, returns `False`
        """
        test_for = "Champion"
        
        print(f"Running test for {test_for}...\n")
        
        if not page_props: page_props = OPGG.get_page_props(summoner) # get latest
        
        msg = "Test was completed with {_pass} passes and {_fail} fails. See below for details:\n"
        msg_summary = ""
        
        latest_attrs = []
        obj_attrs = []
        
        pass_count = 0
        fail_count = 0
        
        for attr in dict(list(dict(page_props['championsById']).values())[0]).keys():
            print(f"{test_for} has {str(attr).ljust(25)}", end='')
            latest_attrs.append(attr)
            
            if hasattr(Champion, attr):
                print(": Pass ✔")
                pass_count += 1
                obj_attrs.append(attr)
            else:
                print(": FAIL ✘")
                fail_count += 1
            
            # slow print effect
            time.sleep(0.1)
        
        msg = msg.format(_pass=pass_count, _fail=fail_count)

        msg_summary += f"\n{test_for} has {len(obj_attrs)} attributes:\n"
        for attr in obj_attrs:
            msg_summary += f"    -> {attr}\n"
        
        msg_summary += f"\nLatest page_props has {len(latest_attrs)} attributes:\n"
        for attr in latest_attrs:
            msg_summary += f"    -> {attr}\n"
        
        msg_summary += f"\nLatest page_props has {len(latest_attrs) - len(obj_attrs)} more attributes than {test_for}:\n"
        for diffs in list(set(latest_attrs) - set(obj_attrs)):
            msg_summary += f"    -> {diffs}\n"
        
        msg_summary += f"\nAll checks for '{test_for}' have been completed.\nResult: {'PASS ✔' if fail_count == 0 else 'FAIL ✘'}\n\n"
        
        print(msg_summary)
        
        return True if fail_count == 0 else False