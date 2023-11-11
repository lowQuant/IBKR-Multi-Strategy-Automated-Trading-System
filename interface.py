import threading
import time
import curses, textwrap
import configparser
import os
import importlib.util
from shared_resources import ib, add_log, log_buffer, log_lock, start_event
from strategies.strategy1 import strategy1
from strategies.strategy2 import strategy2


def main(stdscr):
    global strategies_active
    stdscr.nodelay(True)
    stdscr.clear()
    stdscr.refresh()

    t1 = threading.Thread(target=strategy1)
    t2 = threading.Thread(target=strategy2)

    t1.daemon = True
    t2.daemon = True

    t1.start()
    t2.start()

    while True:
        height, width = stdscr.getmaxyx()
        stdscr.addstr(0, 0, "=" * width)
        title = "Multi Strategy Automated Trading System by Lange Invest"
        stdscr.addstr(1, (width - len(title)) // 2, title)
        stdscr.addstr(2, 0, "=" * width)

        menu_title = "============== Menu =============="
        stdscr.addstr(6, (width - len(menu_title)) // 2, menu_title)
        stdscr.addstr(7, (width - len("| 0. Settings                      |")) // 2, "| 0. Settings                     |")
        stdscr.addstr(8, (width - len("| 1. Go Live                     |")) // 2, "| 1. Go Live                     |")
        stdscr.addstr(9, (width - len("| 2. Status Report               |")) // 2, "| 2. Status Report               |")
        stdscr.addstr(10, (width - len("| 3. Performance Report          |")) // 2, "| 3. Performance Report          |")
        stdscr.addstr(11, (width - len("| q. Quit                        |")) // 2, "| q. Quit                        |")
        stdscr.addstr(12, (width - len("==================================")) // 2, "==================================")


        if start_event.is_set():
            stdscr.addstr(15, 0, f"Recent Logs:".ljust(width))

            with log_lock:
                for i, log_line in enumerate(list(log_buffer)[-5:]):
                    stdscr.addstr(16 + i, 0, log_line[:width])

        stdscr.refresh()

        choice = stdscr.getch()
        if choice == ord('0'):
            manage_settings(stdscr,width)

        elif choice == ord('1'):
            stdscr.nodelay(False)  # Make getch() blocking temporarily
            stdscr.addstr(13, 0, "Are you sure you want to go live? (y/n)".ljust(width))
            stdscr.refresh()
            confirmation = stdscr.getch()
            if confirmation == ord('y'):
                start_event.set()
                stdscr.addstr(13, 0, "System is Live".ljust(width))
            elif confirmation == ord('n'):
                stdscr.addstr(13, 0, "".ljust(width))  # Clear the quit message
            stdscr.nodelay(True)  # Make getch() non-blocking again

        elif choice == ord('2'):
            stdscr.addstr(13, 0, "Status Report".ljust(width))
        elif choice == ord('3'):
            stdscr.addstr(13, 0, "Performance Report".ljust(width))
        elif choice == ord('q'):
            stdscr.nodelay(False)  # Make getch() blocking temporarily
            stdscr.addstr(13, 0, "Are you sure you want to quit? (y/n)".ljust(width))
            stdscr.refresh()
            confirmation = stdscr.getch()
            if confirmation == ord('y'):
                break
            elif confirmation == ord('n'):
                stdscr.addstr(13, 0, "".ljust(width))  # Clear the quit message
            stdscr.nodelay(True)  # Make getch() non-blocking again

        stdscr.refresh()
        time.sleep(0.1)

def manage_settings(stdscr,width):
    settings_file = 'settings.ini'
    config = configparser.ConfigParser()

    if not os.path.exists(settings_file):
        config['DEFAULT'] = {'StrategyCount': '0'}
        with open(settings_file, 'w') as configfile:
            config.write(configfile)
    config.read(settings_file)

    # Initial draw of the settings menu
    draw_settings_menu(stdscr,width)
    while True:
        # No need to clear and redraw here, we only redraw when needed
        choice = stdscr.getch()
        if choice == ord('1'):
            stdscr.clear()
            stdscr.addstr(6, (width // 2) - 10, "General Settings:")
            stdscr.addstr(8, (width // 2) - 10, "1. Change Port for IBKR Connection")
            stdscr.addstr(10, (width // 2) - 10, "b. back")
            stdscr.refresh()

            while True:  # Begin nested loop for the General Settings submenu
                sub_choice = stdscr.getch()
                if sub_choice == ord('1'):
                    # Handle the change port action here
                    change_port(stdscr, config, settings_file,width)
                    draw_settings_menu(stdscr, width)  # Make sure to redraw the menu after changing the port

                elif sub_choice == ord('b'):
                    break
            
            draw_settings_menu(stdscr,width)

        elif choice == ord('2'):
            stdscr.clear()
            strategy_count = config['DEFAULT'].getint('strategycount', 0)  # Get the number of strategies
            header = "Strategy List                 -                 Allocation"
            stdscr.addstr(5, (width // 2) - len(header) // 2, header)
            stdscr.addstr(6, (width // 2) - len(header) // 2, "-" * len(header))  # Underline the header
            line = 8

            if strategy_count > 0:
                for i in range(1, strategy_count + 1):
                    strategy_section = f'Strategy{i}'
                    if strategy_section in config:
                        name = config[strategy_section].get('name', 'N/A')
                        symbol = config[strategy_section].get('symbol', 'N/A')
                        allocation = config[strategy_section].get('allocation', 'N/A')
                        # Left-align name and symbol, and right-align the allocation, ensuring even spacing
                        display_line = f"{i}. {name} ({symbol})".ljust(40) + f"{allocation}%".rjust(15)
                        stdscr.addstr(line, (width // 2) - len(header) // 2, display_line)
                        line += 1
            
            stdscr.addstr(line + 5, (width // 2) - len(header) // 2, "b. back")
            stdscr.refresh()

            if strategy_count == 0:
                stdscr.addstr(line , (width // 2) - len(header) // 2, "0. Add a strategy")
                while True:  # Strategy List submenu if no strategy is present
                    sub_choice = stdscr.getch()
                    if sub_choice == ord('0'):
                        add_strategy(stdscr, config, settings_file)
                        draw_settings_menu(stdscr,width)  # Redraw menu after adding a strategy
                    elif sub_choice == ord('b'):
                        break  # Breaks the nested loop and returns to the main settings menu
            else:
                while True:  # Begin nested loop for the Strategy List submenu
                    sub_choice = stdscr.getch()
                    if sub_choice == ord('b'):
                        break  # Breaks the nested loop and returns to the main settings menu
                    elif sub_choice in [ord(str(i)) for i in range(1, strategy_count + 1)]:
                        strategy_num = int(chr(sub_choice))
                        strategy_section = f'Strategy{strategy_num}'
                        manage_strategy(stdscr, config, settings_file, strategy_section, width)  # Call a new function to manage the strategy

            draw_settings_menu(stdscr, width)  # Redraw the main settings menu

        elif choice == ord('3'):
            add_strategy(stdscr, config, settings_file)
            draw_settings_menu(stdscr,width)  # Redraw menu after adding a strategy
        elif choice == ord('b'):
            break  # Exit settings menu

        # You may want to include a timeout for getch if it's blocking
        time.sleep(0.1)  # Sleep to reduce CPU usage

def draw_settings_menu(stdscr,width):
    stdscr.clear()
    stdscr.addstr(0, 0, "=" * width)
    title = "Multi Strategy Automated Trading System by Lange Invest"
    stdscr.addstr(1, (width - len(title)) // 2, title)
    stdscr.addstr(2, 0, "=" * width)
    stdscr.addstr(6, (width // 2) - 10, "Settings Menu:")
    stdscr.addstr(8, (width // 2) - 10, "1. General Settings")
    stdscr.addstr(9, (width // 2) - 10, "2. Strategy Settings")
    stdscr.addstr(10, (width // 2) - 10, "3. Add a Strategy")
    stdscr.addstr(12, (width // 2) - 10, "b. Back to Main Menu")
    stdscr.refresh()

def add_strategy(stdscr, config, settings_file):
    height, width = stdscr.getmaxyx()
    curses.echo()

    # Create a new window for the form and display a border
    win = curses.newwin(height, width, 0, 0)
    win.box()

    # Fixed positions for the input cursor
    input_x = max(width // 4, 30)  # Adjust the x value as needed for layout

    # Input fields
    strategy_name = prompt_user(win, "Enter Strategy Name: ", 5, input_x, visible_length=60,total_length=100, width=width)
    strategy_abbreviation = prompt_user(win, "Enter Symbol for Strategy: ", 7, input_x, visible_length=60, total_length=20, width=width)
    file_name = prompt_user(win, "Enter Python File Name: ", 9, input_x, visible_length=60, total_length=20, width=width)
    allocation = prompt_user(win, "Enter Allocation (0-100): ", 11, input_x, visible_length=60, total_length=10, width=width)

    # Validation
    curses.noecho()
    curses.curs_set(0)  # Hide cursor after inputs

    try:
        allocation_int = int(allocation)
        if not 0 <= allocation_int <= 100:
            win.addstr(16, 2, "Allocation must be between 0 and 100.".ljust(width))
            win.refresh()
            stdscr.nodelay(False) 
            stdscr.getch()
            stdscr.nodelay(True) 
            raise ValueError("Allocation must be between 0 and 100.")
             
    except ValueError as e:
        win.addstr(22, 0, f"Error: {e}. Press any key to continue...".ljust(width))
        win.refresh()
        stdscr.nodelay(False) 
        stdscr.getch()
        stdscr.nodelay(True) 
        return  # Exit the function if validation fails

    # Confirmation before saving
    win.addstr(15, 2, "Save this information? (y/n): ")
    win.refresh()
    confirmation = win.getch()
    if confirmation in [ord('n'), ord('N')]:
        win.addstr(16, 2, "Operation cancelled. Press any key to continue...")
        win.refresh()
        stdscr.nodelay(False) 
        stdscr.getch()
        stdscr.nodelay(True) 
        return  # Return without saving
    
    if confirmation in [ord('y'), ord('Y')]:
        # Assuming validation passed and confirmed, update the config
        strategy_count = int(config['DEFAULT'].get('StrategyCount', 0))
        strategy_section = f'Strategy{strategy_count + 1}'

        config[strategy_section] = {
            'Name': strategy_name,
            'Symbol': strategy_abbreviation,
            'FileName': file_name,
            'Description': "",
            'Allocation': allocation}
        
        config['DEFAULT']['StrategyCount'] = str(strategy_count + 1)

        # Write changes back to settings.ini
        with open(settings_file, 'w') as configfile:
            config.write(configfile)

        # Success message
        success_msg = f"{strategy_name} strategy added successfully! Press any key to continue..."
        success_msg_x = (width - len(success_msg)) // 2  # Center the message
        win.addstr(17, success_msg_x, success_msg)
        win.refresh()

        stdscr.nodelay(False) 
        stdscr.getch()  # Wait for user input before continuing
        stdscr.nodelay(True)
        win.clear() # Clear the window and return to the main screen
        win.refresh()

def manage_strategy(stdscr, config, settings_file, strategy_section, width):
    strategy_name = config[strategy_section].get('name', 'N/A')
    needs_update = True

    # Define the width for the description
    description_width = width - 4  # Adjust the width as needed for your interface

    while True:
        if needs_update:
            stdscr.clear()
            strategy_params = load_and_initialize_strategy_params(config, settings_file, strategy=strategy_section)
            stdscr.addstr(2, 2, f"Editing Strategy: {strategy_name}")
            stdscr.addstr(4, 2, "Parameter".ljust(15) + "Name".ljust(40) + "Value".ljust(30))
            stdscr.addstr(5, 2, "-" * (15 + 40 + 30))  # Heading underline

            line = 6
            for param_id, details in strategy_params.items():
                stdscr.addstr(line, 2, f"{param_id}".ljust(15) + f"{details['name']}".ljust(40) + f"{details['value']}".ljust(30))
                line += 2
                
                # Wrap the description text to fit into the specified width
                wrapped_description = textwrap.fill(details['description'], description_width)
                description_lines = wrapped_description.split('\n')
                
                for desc_line in description_lines:
                    stdscr.addstr(line, 4, desc_line)
                    line += 1
                
                stdscr.addstr(line, 2, "-" * (15 + 40 + 30))
                line += 1

            stdscr.addstr(line + 1, 2, "Press the parameter number to edit, 'w' to change the weight, or 'b' to go back.")
            stdscr.addstr(line + 3, 2, "Press 'd' to delete this strategy.")
            stdscr.refresh()
            needs_update = False

        param_choice = stdscr.getch()
        if param_choice in [ord(str(i)) for i in range(1, len(strategy_params) + 1)]:
            param_num = int(chr(param_choice))
            param_key = f"param{param_num}"
            edit_param(stdscr, config, settings_file, strategy_section, param_key, width)
            needs_update = True  # Mark to update the display after editing

        elif param_choice == ord('w'):
            edit_weight(stdscr, config, settings_file, strategy_section, width)
            needs_update = True  # Mark to update the display after editing

        elif param_choice == ord('d'):
            delete_strategy(stdscr,config, settings_file, strategy_section)
            needs_update = True  # Mark to update the display after deletion, which will also exit the loop

        elif param_choice == ord('b'):
            break  # Exit the while loop to go back

def edit_param(stdscr, config, settings_file, strategy_section, param_key, width):
    # Clear the screen before displaying anything new
    stdscr.clear()

    # Disable nodelay to make sure getch() and getstr() block for input
    stdscr.nodelay(False)

    # Retrieve the current value and description of the parameter
    param_name = config[strategy_section][param_key + '_name']
    current_value = config[strategy_section][param_key + '_value']
    description = config[strategy_section][param_key + '_description']

    # Prompt user for new value
    stdscr.addstr(2, 2, f"Editing {param_name} (Current Value: {current_value})")
    stdscr.addstr(4, 2, description)
    stdscr.addstr(6, 2, f"Enter new value for {param_name}: ")

    # Enable echoing of input to show the user what they're typing
    curses.echo()

    # Get the new value from the user
    new_value = stdscr.getstr(6, len(f"Enter new value for {param_name}: ") + 2, 20).decode('utf-8')

    # Disable echoing of input after getting the input
    curses.noecho()

    # Validate and save the new value if needed, then update the configuration
    try:
        # Convert the new value to the appropriate type and validate it
        new_value = int(new_value)  # Example: converting to integer
        if new_value <= 0:
            raise ValueError("The value must be positive.")

        # Update the configuration
        config[strategy_section][param_key + '_value'] = str(new_value)
        with open(settings_file, 'w') as configfile:
            config.write(configfile)
        stdscr.addstr(8, 2, "Value updated successfully.")
    except ValueError as e:
        stdscr.addstr(8, 2, f"Invalid input: {e}")

    # Refresh to show the update and then wait for a key press to return
    stdscr.refresh()
    stdscr.getch()  # Now this should block since nodelay is set to False

    # If necessary, re-enable nodelay after getting the input
    stdscr.nodelay(True)

def edit_weight(stdscr, config, settings_file, strategy_section, width):
    stdscr.clear()
    stdscr.nodelay(False)
    # Prompt the user to enter a new weight
    prompt = "Enter new weight (0-100): "
    stdscr.addstr(20, 2, prompt)
    stdscr.refresh()
    curses.echo()
    new_weight = stdscr.getstr(20, 2 + len(prompt), 5).decode('utf-8')
    stdscr.nodelay(True)
    # Validate the new weight
    try:
        new_weight = int(new_weight)
        if not 0 <= new_weight <= 100:
            raise ValueError
    except ValueError:
        stdscr.addstr(22, 2, "Invalid weight. Please enter a number between 0 and 100.")
        stdscr.refresh()
        curses.napms(2000)  # Wait 2 seconds
        return

    # Update the settings.ini file with the new weight
    config.set(strategy_section, 'allocation', str(new_weight))
    with open(settings_file, 'w') as configfile:
        config.write(configfile)

def delete_strategy(stdscr, config, settings_file, strategy_section):
    stdscr.clear()
    # Confirm with the user
    stdscr.addstr(20, 2, f"Are you sure you want to delete the strategy '{config[strategy_section]['name']}'? (y/n): ")
    stdscr.refresh()
    stdscr.nodelay(False)
    confirmation = stdscr.getch()
    if confirmation in [ord('y'), ord('Y')]:
        # Remove the section from settings.ini
        config.remove_section(strategy_section)
        strategy_count = config.getint('DEFAULT', 'strategycount') - 1
        config.set('DEFAULT', 'strategycount', str(strategy_count))

        with open(settings_file, 'w') as configfile:
            config.write(configfile)

        stdscr.addstr(22, 2, "Strategy deleted successfully.")
        stdscr.refresh()
        curses.napms(2000)  # Wait 2 seconds
    else:
        stdscr.addstr(22, 2, "Deletion canceled.")
        stdscr.refresh()
        curses.napms(2000)  # Wait 2 seconds
    stdscr.nodelay(True)

def load_and_initialize_strategy_params(config, settings_file, strategy):
    strategy_params = {}

    # Extract the filename from the config
    strategy_file = config.get(strategy, 'filename', fallback=None)

    if not strategy_file:
        print(f"No strategy file specified for {strategy}.")
        return strategy_params

    try:
        # Load the strategy module from the given file name
        module_name = os.path.splitext(strategy_file)[0]
        module_path = os.path.join('strategies', strategy_file)
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        strategy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(strategy_module)

        # Check if PARAMS dictionary exists and has content
        if hasattr(strategy_module, 'PARAMS') and strategy_module.PARAMS:
            default_params = strategy_module.PARAMS
        else:
            raise ImportError(f"No editable parameters found for strategy {strategy}.")

    except ImportError as e:
        # If strategy file not found or PARAMS not defined, notify the user and exit
        print(str(e))
        return strategy_params

    # Ensure the configuration file section exists
    if not config.has_section(strategy):
        config.add_section(strategy)

    # Initialize or update parameters in the config
    for param_id, details in default_params.items():
        for key in ['name', 'value', 'description']:
            config_key = f'param{param_id}_{key}'
            if not config.has_option(strategy, config_key):
                config.set(strategy, config_key, str(details[key]))

    # Save the changes to the settings file
    with open(settings_file, 'w') as configfile:
        config.write(configfile)

    # Load the parameters from the config to a dictionary
    for param_id, details in default_params.items():
        strategy_params[param_id] = {
            'name': config.get(strategy, f'param{param_id}_name'),
            'value': config.get(strategy, f'param{param_id}_value'),
            'description': config.get(strategy, f'param{param_id}_description')
        }

    return strategy_params

def prompt_user(win, prompt, y, input_x, visible_length, total_length, width):
    # Display the prompt at a fixed position
    win.addstr(y, 2, prompt)  # 2 to offset from the window border
    win.refresh()

    # Create an input pad where the user can enter more text than is visible
    input_pad = curses.newpad(1, total_length)
    input_pad.scrollok(True)
    input_pad.idlok(True)

    # Initial cursor and pad positions
    pad_x = 0
    cursor_x = input_x

    # Loop for handling input with scrolling
    while True:
        input_pad.refresh(0, pad_x, y, input_x, y, input_x + visible_length - 1)
        ch = input_pad.getch(0, cursor_x - input_x + pad_x)

        # Handle backspace/delete
        if ch in (curses.KEY_BACKSPACE, 127):
            if cursor_x > input_x:
                input_pad.delch(0, cursor_x - input_x + pad_x - 1)
                cursor_x -= 1
        # Handle left arrow
        elif ch == curses.KEY_LEFT:
            if cursor_x > input_x:
                cursor_x -= 1
        # Handle right arrow
        elif ch == curses.KEY_RIGHT:
            if cursor_x - input_x < pad_x + visible_length and cursor_x < total_length:
                cursor_x += 1
        # Handle other printable characters
        elif 32 <= ch < 127:
            input_pad.addch(0, cursor_x - input_x + pad_x, ch)
            if cursor_x - input_x < pad_x + visible_length:
                cursor_x += 1
        # Enter/return key
        elif ch == 10:
            break

        # Adjust pad position if necessary
        if cursor_x - input_x >= pad_x + visible_length:
            pad_x += 1
        elif cursor_x - input_x < pad_x:
            pad_x -= 1

    # Get the input data from the pad
    input_pad.refresh(0, pad_x, y, input_x, y, input_x + visible_length - 1)
    input_str = input_pad.instr(0, 0, total_length).decode().strip()

    return input_str

def change_port(stdscr, config, settings_file,width):
    curses.echo()
    win = curses.newwin(10, 50, 5, (width - 50) // 2)  # Adjust size and position as needed
    win.box()
    win.addstr(1, 2, "Enter new port (4 digits): ")
    win.refresh()
    curses.curs_set(1)  # Show cursor
    while True:
        try:
            win.move(1, 28)  # Move cursor to the right of the prompt
            new_port_str = win.getstr().decode().strip()
            if len(new_port_str) == 4 and new_port_str.isdigit():
                new_port = int(new_port_str)
                config['DEFAULT']['Port'] = str(new_port)
                with open(settings_file, 'w') as configfile:
                    config.write(configfile)
                win.addstr(3, 2, "Port changed successfully.", curses.A_BOLD)
                win.refresh()
                break
            else:
                raise ValueError
        except ValueError:
            win.move(2, 2)
            win.clrtoeol()
            win.addstr(2, 2, "Invalid port. Try again.", curses.A_BOLD)
            win.refresh()

    curses.curs_set(0)  # Hide cursor
    curses.noecho()
    win.getch()  # Wait for user input before closing the window
    win.clear()
    win.refresh()


if __name__ == '__main__':
    curses.wrapper(main)
