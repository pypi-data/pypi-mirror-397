import numpy as np
import traceback

# --- Color Helper Functions ---
def print_white(msg):
    print(msg)

def print_green(msg):
    print('\033[1m' + '\033[92m' + msg + '\033[0m')

def print_red(msg):
    print('\033[1m' + '\033[91m' + msg + '\033[0m')

def print_blue(msg):
    print('\033[1m' + '\033[94m' + msg + '\033[0m')

def print_yellow(msg):
    print('\033[1m' + '\033[93m' + msg + '\033[0m')

def print_magenta(msg):
    print('\033[1m' + '\033[38;5;201m' + msg + '\033[0m')

def print_cyan(msg):
    print('\033[1m' + '\033[96m' + msg + '\033[0m')

# --- Check Functions ---

def checkNone(func):
    if func is None:
        print_red('\u2718 - Function is None!')
        return False
    return True

def checkReturnNone(retval):
    if retval is None:
        print_red('\u2718 - Function returned None!')
        return False
    return True


def compNum(v1_act, v2_des, tol=1e-3):
    try:
        if v1_act is None or v2_des is None:
            return False
        # np.testing.assert_allclose works for scalars too
        np.testing.assert_allclose(v1_act, v2_des, atol=tol)
        return True
    except Exception as e:
        print("--------------------------------")
        print_red(f'\u2718 - Result(s) do not match: {e}')
        print_blue(f'Expected:\n{v2_des}')
        print_yellow(f'Current:\n{v1_act}')        
        return False
    
# def compNPArray(actual, desired):
#     try:
#         if actual is None or desired is None:
#             return False
#         # np.testing.assert_array_equal checks shape and values
#         np.testing.assert_array_equal(actual, desired)
#         return True
#     except Exception as e:
#         print("--------------------------------")
#         print_magenta(f'!!Result not equal:')
#         print(f"{e}\n")
#         print_blue(f'Desired: {desired}')
#         print_yellow(f'Actual: {actual}\n')        
#         return False

def compNPArray(a_act, b_des, tol=1e-3):
    try:
        if a_act is None or b_des is None:
            return False
        # np.testing.assert_allclose checks shape and values within tolerance
        np.testing.assert_allclose(a_act, b_des, atol=tol)
        return True
    except Exception as e:
        print("--------------------------------")
        print_red(f'\u2718 - Result(s) do not match: {e}')
        print_blue(f'Expected:\n{b_des}')
        print_yellow(f'Current:\n{a_act}\n')
        return False

def checker(cond, msg):
    if cond:
        print_green(f'\u2714 - {msg}')
    else:
        print_red(f'\u2718 - {msg}')

def run_safe(func, *args, **kwargs):
    """
    Safely run a function and return the result, printing errors if any.
    Returns None on failure.
    If 'func' is not callable, it is assumed to be a result value and returned as-is.
    """
    
    try:
        if func is None:
            raise ValueError("Function not implemented")
        exec_result = func(*args, **kwargs)
        if (exec_result is None):
            name = getattr(func, '__name__', str(func))
            print_red(f'\u2718 - Is [{name}] implemented at all?')
        return exec_result
    except Exception as e:
        name = getattr(func, '__name__', str(func))
        print_red(f'\u2718 - Execution failed for {name}: {e}')
        # magenta
        print_cyan(f'\n\nTraceback: {traceback.format_exc(limit=-1)}')
        return None


if __name__ == "__main__":
    checker(checkNone(None) == False, "checkNone with None")
