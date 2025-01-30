import curses
import time

def main(stdscr):
    stdscr.clear()
    
    nodes = ["Node A","Node B", "Node C","Node D"]
    connections = [(0,1), (1,2)]
    current_row = 0
    connecting_from = None
    disconnecting_from = None
    status_message = ""
    status_timestamp = 0

    def print_menu():
        stdscr.clear()
        for idx, node in enumerate(nodes):
            x = 0
            y = idx
            if idx == current_row:
                stdscr.addstr(y, x, node, curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, node)
            
            # Highlight the selected first node during connection/disconnection
            if idx == connecting_from:
                stdscr.addstr(y, len(node) + 2, "[Connecting from]")
            elif idx == disconnecting_from:
                stdscr.addstr(y, len(node) + 2, "[Disconnecting from]")
        
        # Print existing connections
        y = len(nodes) + 1
        for i, conn in enumerate(connections):
            stdscr.addstr(y + i, 0, f"Connection: {nodes[conn[0]]} -> {nodes[conn[1]]}")
        
        # Print status message if within timeout
        if status_message and time.time() - status_timestamp < 5:
            stdscr.addstr(len(nodes) + len(connections) + 2, 0, status_message)
        
        stdscr.refresh()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    while True:
        print_menu()
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(nodes) - 1:
            current_row += 1
        elif key == ord('c'):
            if connecting_from is None:
                connecting_from = current_row
                status_message = "Select second node to connect to"
                status_timestamp = time.time()
            else:
                if connecting_from != current_row:  # Prevent self-connections
                    new_connection = (connecting_from, current_row)
                    if new_connection not in connections:
                        connections.append(new_connection)
                        status_message = f"Connected: {nodes[connecting_from]} -> {nodes[current_row]}"
                        status_timestamp = time.time()  # Reset timestamp for new message
                    else:
                        status_message = "Connection already exists!"
                else:
                    status_message = "Cannot connect node to itself!"
                    status_timestamp = time.time()
                connecting_from = None
        elif key == ord('d'):
            if disconnecting_from is None:
                disconnecting_from = current_row
                status_message = "Select second node to disconnect from"
                status_timestamp = time.time()
            else:
                connection_to_remove = (disconnecting_from, current_row)
                if connection_to_remove in connections:
                    connections.remove(connection_to_remove)
                    status_message = f"Disconnected: {nodes[disconnecting_from]} -> {nodes[current_row]}"
                    status_timestamp = time.time()  # Reset timestamp for new message
                else:
                    status_message = "No such connection exists!"
                    status_timestamp = time.time()
                disconnecting_from = None
        elif key == ord('q'):
            break
        elif key == 27:  # ESC key
            connecting_from = None
            disconnecting_from = None
            status_message = "Operation cancelled"
        
        stdscr.refresh()

curses.wrapper(main)
