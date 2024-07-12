import time


class OPGGTests:
    """
    Represents a collection of tests for OPGG
    """
    
    @staticmethod
    def verify_objects(objects_to_test: list, related_page_props: list) -> list[bool]:
        """
        Test any number of `objects` against what's returned by `page_props`
        
        ### Returns:
            `list[bool]` - A `list` containing the `bool` results of each test.
        """
        if len(objects_to_test) != len(related_page_props):
            raise Exception("The objects list does not match the length of related page props.")
        
        # Global counter
        result_bools = []
        
        for i, test_cls in enumerate(objects_to_test):
            print(f"{'=' * 80}\n\nRunning test for {test_cls.__name__}...\n")
            
            msg_summary = ""
            latest_attrs = []
            pass_count = 0
            fail_count = 0
            
            # get the properties of class and only properties that are NOT callable (excludes internal methods)
            obj_attrs = [prop for prop in vars(test_cls) if not str(prop).startswith('__') and not callable(getattr(test_cls, prop))]
        
            for attr in dict(related_page_props[i]).keys():
                print(f"Checking {test_cls.__name__} for {attr}".ljust(70), end='')
                latest_attrs.append(attr)
                
                if attr in obj_attrs:
                    print("| Pass ✔")
                    pass_count += 1
                else:
                    print("| FAIL ✘")
                    fail_count += 1
                
                # slow print effect
                time.sleep(0.025)

            msg_summary += f"\n-> {test_cls.__name__} has {len(obj_attrs)} attributes"
            msg_summary += f"\n-> OPGG response has {len(latest_attrs)} attributes\n"
            
            if (latest_attrs > obj_attrs):
                msg_summary += f"\nOPGG response contains the following additional attribute(s):\n"
            
            for diffs in list(set(latest_attrs) - set(obj_attrs)):
                msg_summary += f"    -> {diffs}\n"
            
            msg_summary += f"\nAll checks for '{test_cls.__name__}' have been completed.\nResult: {'PASS ✔' if fail_count == 0 else 'FAIL ✘'}\n"
            
            # If there are errors
            if fail_count > 0:
                result_bools.append(False)
            else:
                result_bools.append(True)
            
            print(msg_summary)
        
        return result_bools