from graphics import *
import time
from random import *
import tkinter

'''
=======================================CLASS INITIALIZATIONS AND FUNCTIONS=======================================
'''
station_name = {
    1: "(1) Queen Street",
    2: "(2) Commercial",
    3: "(3) Campus",
    4: "(4) Park Road",
    5: "(5) City Station",
    6: "(6) General Hospital",
    7: "(7) Riverside",
    8: "(8) Francis International",
    9: "(9) Savanna",
    10: "(10) Crusader Gate",
    11: "(11) Secretariat",
    12: "(12) Paddington"
}

'''
=============================================VEHICLE CLASS FUNCTIONS=============================================
'''


class bus:
    def __init__(self):
        self.route = None
        self.speed = 60
        self.graph = [Circle(Point(0, 0), 3), Text(Point(335, 670), " ")]
        self.seats = 0
        self.capacity = []
        print("\nclass initialized!")

    def assign_route(self, r):
        self.route = r
        print("\nroute assigned!")

    def traverse_route(self, win, skipped):
        print("route traversal starts!")
        self.graph[1] = Text(Point(win.getWidth() / 2, 670), " ")
        self.graph[1].draw(win)
        if self.route is None:
            return
        else:
            message = Text(Point(win.getWidth() / 2, 700), " ")
            message.draw(win)
            message2 = Text(Point(win.getWidth() / 2, 720), " ")
            message2.draw(win)
            print("message drawn out")

            temp = self.route.start
            print("Moving forward!")
            while temp.next_point is not None:
                if is_station(temp):
                    message2.undraw()
                    message2 = Text(Point(win.getWidth() / 2, 720), "Next Station: "
                                    + station_name[int(temp.station_number + 1)])
                    message2.draw(win)
                    self.load_unload(temp, win, "f", message, skipped)
                self.move_forward(temp, win, "f")
                temp = temp.next_point

            print("Moving backward!")
            while temp is not self.route.start:
                if is_station(temp):
                    message2.undraw()
                    message2 = Text(Point(win.getWidth() / 2, 720), "Next Station: "
                                    + station_name[int(temp.station_number - 1)])
                    message2.draw(win)
                    self.load_unload(temp, win, "r", message, skipped)

                self.move_forward(temp, win, "r")
                temp = temp.previous_point

            if is_station(temp):
                self.load_unload(temp, win, "r", message, skipped)

            print("Traversal Finished!")

    def load_unload(self, node, win, direction, message, skipped):
        print("\nstation: ", node.station_number)
        self.graph[0] = Circle(Point(node.x, node.y), 5)
        self.graph[0].setFill("blue")
        self.graph[0].draw(win)

        if node.station_number == skipped:
            message.undraw()
            message = Text(Point(win.getWidth() / 2, 700), station_name[node.station_number] + " is skipped!")
            message.draw(win)
            time.sleep(0.5)
            message.undraw()
            self.graph[0].undraw()
            return

        message.undraw()
        message = Text(Point(win.getWidth() / 2, 700), "Current Station: " + station_name[node.station_number])
        message.draw(win)

        # unloading passengers
        items = []
        print("Dropped off: ", end='')
        for x in self.capacity:
            if x != node.station_number:
                items.append(x)
                continue
            else:
                print(x, end=', ')
        self.capacity = items[:]
        items.clear()
        print()

        # loading passengers
        print("Picked up: ", end='')
        not_going = []
        if direction == "f":
            for y in node.capacity:
                if y < node.station_number:
                    not_going.append(y)
                else:
                    self.capacity.append(y)
                    print(y, end=', ')
            node.capacity = not_going[:]

        elif direction == "r":
            for y in node.capacity:
                if y > node.station_number:
                    not_going.append(y)
                else:
                    self.capacity.append(y)
                    print(y, end=', ')

            node.capacity = not_going[:]
        not_going.clear()
        print()

        time.sleep(1.5)
        self.graph[1].undraw()
        self.graph[1] = Text(Point(win.getWidth() / 2, 670), "Total Passengers: " + str(len(self.capacity)))
        self.graph[1].draw(win)
        message.undraw()
        self.graph[0].undraw()
        return

    def move_forward(self, temp, win, direction):
        # assign start and end
        start_point = [temp.x, temp.y]

        if direction == "f":
            end_point = [temp.next_point.x, temp.next_point.y]
        elif direction == "r":
            end_point = [temp.previous_point.x, temp.previous_point.y]

        # prepare position and step
        step_x = int((end_point[0] - start_point[0]) / 20)
        step_y = int((end_point[1] - start_point[1]) / 20)
        cur_position = start_point[:]

        self.graph[0] = Circle(Point(start_point[0], start_point[1]), 5)
        self.graph[0].setFill("red")

        # actual traversal
        while cur_position != end_point:
            # show on screen
            self.graph[0].draw(win)
            time.sleep(1 / self.speed)
            self.graph[0].undraw()
            # change coordinates
            cur_position[0] += step_x
            cur_position[1] += step_y

            self.graph[0] = Circle(Point(cur_position[0], cur_position[1]), 5)
            self.graph[0].setFill("red")


'''
==============================================ROUTE CLASS FUNCTIONS==============================================
'''


class grid_point:
    def __init__(self, x, y, t, c):
        self.type = t
        self.x = x
        self.y = y

        if self.type == 's':
            self.location = [x, y]
            self.capacity = []
            self.station_number = c

        elif self.type == 'r':
            self.location = [x, y]

        self.next_point = None
        self.previous_point = None


class line_route:
    def __init__(self):
        self.start = None
        self.end = None
        self.station_count = 0

    def create_station(self, x, y):
        self.station_count += 1
        new = grid_point(x, y, 's', self.station_count)
        if self.start is None:
            self.start = new
            self.end = new
            return

        temp = self.start
        while temp.next_point is not None:
            temp = temp.next_point

        temp.next_point = new
        new.previous_point = temp
        self.end = new

    def create_road(self, x, y):
        new = grid_point(x, y, 'r', None)
        if self.start is None:
            print("ERROR, No station to start from")
            return

        temp = self.start
        while temp.next_point is not None:
            temp = temp.next_point

        temp.next_point = new
        new.previous_point = temp
        self.end = new

    def remove_road(self):
        temp = self.start
        while temp is not self.end:
            temp = temp.next_point

        self.end = temp.previous_point
        self.end.next_point = None
        print("removed road!")

    def remove_route(self):
        print("Removing route")
        temp = self.start
        while temp is not self.end:
            self.start = temp
            if temp.graph is not None:
                if temp.type == 's':
                    print("station ", temp.station_number, ": ", temp.capacity)
                temp.graph.undraw()
            temp = temp.next_point
            time.sleep(0.08)
        # final station
        if temp.graph is not None:
            print("station ", temp.station_number, ": ", temp.capacity)
            temp.graph.undraw()
        print("Removed route!")

    def replace_node(self):
        temp = self.end.previous_point
        x = temp.x
        y = temp.y

        new = grid_point(x, y, 's', self.station_count)

        self.end = self.end.previous_point
        self.end = new

    def print_route(self, win):
        temp = self.start
        while temp is not None:
            if temp.type == 's':
                temp.graph = Circle(Point(temp.x, temp.y), 3)
                temp.graph.setFill("green")
                temp.graph.draw(win)

                # assign random passengers to station
                i = 0
                while i < 10:
                    x = randint(1, self.station_count)
                    if x == temp.station_number:
                        continue
                    else:
                        temp.capacity.append(x)
                        i += 1
                print("station ", temp.station_number, ": ", temp.capacity)

            elif temp.type == 'r':
                temp.graph = Line(Point(temp.previous_point.x, temp.previous_point.y), Point(temp.x, temp.y))
                temp.graph.draw(win)

            temp = temp.next_point
            time.sleep(0.08)


'''
=======================================OUTSIDE FUNCTIONS AND ALGORITHMS=======================================
'''


def create_grid():
    grid = []
    for y in range(1, 18):
        for x in range(1, 18):
            grid.append([x * 40, y * 40])
    return grid


def road_alg(old_cords, route_check):
    option_list = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
    options = option_list[:]
    length = len(options)
    while length != 0:

        x = int(old_cords[0])
        y = int(old_cords[1])

        # creating a line from old point
        rand = randint(0, length - 1)
        op = options.pop(rand)
        r1 = op[0]
        r2 = op[1]

        x = x + (r1 * 40)
        y = y + (r2 * 40)

        temp = [x, y]  # store coordinates

        for a in range(len(route_check)):
            t1 = route_check[a]
            if temp == t1:
                route_check.pop(a)  # ok there's a free vertex nobody used
                return temp
        length -= 1
    return "Error"


def is_station(node):
    if node.type != 's':
        return False
    else:
        return True


def create_route(grid_list, win, no_of_stations, road_length):
    route_options = grid_list[:]  # need a copy of the grid list for route options

    line1 = line_route()  # create the route linked list
    old_cords = route_options.pop(int(len(grid_list) / 2))  # starting point at center of window

    for i in range(0, no_of_stations - 1):  # will make 'x' total stations     EDITABLE
        line1.create_station(old_cords[0], old_cords[1])

        # create road
        length = randint(2, road_length)  # selects a random road length 'y'       DON'T MESS TOO MUCH WITH LENGTH
        for j in range(0, length):
            new_cords = road_alg(old_cords, route_options)  # find coordinates

            while new_cords == "Error":  # this doesn't happen often so couldn't debug properly
                line1.remove_road()
                old_cords = [line1.end.x, line1.end.y]
                new_cords = road_alg(old_cords, route_options)

            line1.create_road(new_cords[0], new_cords[1])  # create road to coordinates
            old_cords = new_cords  # new coordinates are now old

    # last station
    line1.create_station(int(old_cords[0]), int(old_cords[1]))

    line1.print_route(win)
    return line1


'''
===============================================UI FUNCTIONS===================================================
'''


def random_route():  # customize skip feature                  THIS IS THE SECOND BUTTON FROM THE MAIN MENU
    st_skip = randint(0, 12)
    stat = randint(2, 12)
    road = randint(1, 10)
    sp = randint(1, 10)
    main(stat, road, sp, st_skip)


def station_list():  # INTERNAL LITTLE MENU
    window3 = tkinter.Tk()
    window3.title("Station List")
    window3.geometry('400x400')
    window3.bell()
    window3.configure(bg='white')

    for i in range(1, 13):
        ans = tkinter.Label(window3)
        if i == 1:
            ans.pack(pady=10)
        ans.pack(pady=5)
        ans.config(text=str(station_name[i]))
        ans.config(bg='white')


def stations():  # Customize Number of Stations         THIS IS THE FIRST BUTTON FROM THE MAIN MENU
    window3 = tkinter.Tk()
    window3.title("Number of Stations")
    window3.configure(bg='#66FCF1')
    frame = tkinter.Frame(window3, padx=10, pady=10)
    frame.place(in_=window3, anchor="center")
    frame.grid()

    def check():
        st_skip = int(skip_slider.get())
        stat = int(st_slider.get())
        road = int(rd_slider.get())
        sp = int(sp_slider.get())

        window3.destroy()
        main(stat, road, sp, st_skip)

    label = tkinter.Label(frame, text='Number of Stations: ', font=('Helvetica', 14))
    label.grid(row=0, column=0)
    st_slider = tkinter.Scale(frame, from_=2, to=12, orient=tkinter.HORIZONTAL)
    st_slider.grid(row=0, column=1)

    label2 = tkinter.Label(frame, text='Maximum Road Length: ', font=('Helvetica', 14))
    label2.grid(row=1, column=0)
    rd_slider = tkinter.Scale(frame, from_=2, to=9, orient=tkinter.HORIZONTAL)
    rd_slider.grid(row=1, column=1)

    label3 = tkinter.Label(frame, text='Bus Speed: ', font=('Helvetica', 14))
    label3.grid(row=2, column=0)
    sp_slider = tkinter.Scale(frame, from_=1, to=10, orient=tkinter.HORIZONTAL)
    sp_slider.grid(row=2, column=1)

    label4 = tkinter.Label(frame, text='Skip Station: ', font=('Helvetica', 14))
    label4.grid(row=3, column=0)
    skip_slider = tkinter.Scale(frame, from_=0, to=12, orient=tkinter.HORIZONTAL)
    skip_slider.grid(row=3, column=1)

    label4 = tkinter.Label(frame, text=' ', font=('Helvetica', 14))
    label4.grid(row=4, column=0)

    bt4 = tkinter.Button(frame, text='View Station List', font=('Helvetica', 14), width=16, height=1, fg='#66FCF1', bg="#1F2833", command=station_list)
    bt4.grid(row=5, column=0)

    # regular route traversal
    confirm_button = tkinter.Button(frame, text='Enter', font=('Helvetica', 14), width=16, height=1, fg='#66FCF1', bg="#1F2833", command=check)
    confirm_button.grid(row=5, column=1)


def quit_p():  # THIRD BUTTON
    exit(0)


def gui():  # yes officer we actually did it
    window1 = tkinter.Tk()
    window1.title("Metro Simulator")
    window1.configure(bg='white')
    window1.geometry('420x696')
    welcome = tkinter.Label(window1, text=' Metro \n Simulator', bg='white', fg="#1F2833",
                            font=('Helvetica', 36, 'bold'))
    welcome.pack(pady=(80, 30))

    start_route_button = tkinter.Button(window1, text='Start Route', bd=5, borderwidth=0, width=25, height=2,
                                        fg='#66FCF1', bg="#1F2833", command=stations, font=('Helvetica', 18, 'bold'))
    start_route_button.pack(pady=(50,20), padx=20)
    skip_station_button = tkinter.Button(window1, text='Random Route', bd=5, borderwidth=0, width=25, height=2,
                                         fg='#66FCF1', bg="#1F2833", command=random_route, font=('Helvetica', 18, 'bold'))
    skip_station_button.pack(pady=20, padx=20)
    quit_button = tkinter.Button(window1, text='Quit Program', bd=5, borderwidth=0, width=25, height=2,
                                 fg='#66FCF1', bg="#1F2833", command=quit_p, font=('Helvetica', 18, 'bold'))
    quit_button.pack(pady=20, padx=20)
    passenger = tkinter.Label(window1, text='To View Debug Information See Console', bg='white', fg="#1F2833",
                              font=('Helvetica', 10))
    passenger.pack(pady=30)
    window1.mainloop()


def main(st_num, rd_num, speed, sk):  # Starts Program: sk is the Station Number to be skipped
    window = GraphWin('Metro Simulator', 720, 800)
    s = speed * 10
    print(s)

    grid_list = create_grid()
    route = create_route(grid_list, window, st_num, rd_num)
    bus1 = bus()
    bus1.speed = s
    bus1.assign_route(route)
    bus1.traverse_route(window, sk)
    route.remove_route()
    window.close()


gui()
# just to make it an even 500!
