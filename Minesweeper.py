"""
COMP.CS.100 Ohjelmointi 1 / Programming 1

Minesweeper game template

Minesweeper is an always solvable puzzle game. Numbers represent the amount of
mines touching the tile vertically, horizontally or diagonally. Maximum number
is obviously 8 and minimum is 0. If user presses zero, the game shows all zeros
touching it and numbers touching that area. If you press all tiles
without pressing a mine, you win. If you press a mine, you lose.

Program is an advanced version of project.

Student Id: H291837
Name:       Taneli Liedes
Email:      taneli.liedes@tuni.fi

Student Id: H292323
Name:       Jaakko Nikkilä
Email:      jaakko.nikkila@tuni.fi
"""


from tkinter import *
import random


class Minesweeper:
    """
    implements user interface
    """
    def __init__(self):
        """
        Constructor
        """
        self.__window = Tk()

        # Set the game over variable to false
        self.__game_over = False
        # Set the title
        self.__window.title("Minesweeper")

        # Set the window size
        self.__window.geometry("570x677")

        # Make the window not resizable
        self.__window.resizable(False, False)
        # Creating a variable which is used in creating the different sizes
        # of games
        self.__size = IntVar()
        self.__size.set(15)

        # Creating string variables for the timer
        self.__minute = IntVar()
        self.__second = IntVar()

        # Creating the labels for timer names and text variables
        self.__minute_label = Label(textvariable=self.__minute)
        self.__minutes = Label(text="Mins")

        self.__second_label = Label(textvariable=self.__second)
        self.__seconds = Label(text="Secs")

        # Create menu
        self.create_menu()

        # Setting default values for scores
        self.__10score = 99999
        self.__15score = 99999
        self.__20score = 99999

        # Start a new game
        self.new_game()

        # Start the timer
        self.timer()

    def clear_frame(self):
        """
        Clears the screen of everything and recreates the menu
        """
        for widget in self.__window.winfo_children():
            widget.destroy()

        self.create_menu()

    def create_menu(self):
        """
        Creates a menu where you can exit the game or start a new game
        """
        # Creating the menubar
        self.__menubar = Menu(self.__window)
        game_menu = Menu(self.__menubar, tearoff=0)

        # Creating various of menu items
        game_menu.add_command(label="New Game (10x10)",
                              command=lambda:
                              [self.__size.set(10), self.new_game()])

        game_menu.add_command(label="New Game (15x15)",
                              command=lambda:
                              [self.__size.set(15), self.new_game()])

        game_menu.add_command(label="New Game (20x20)",
                              command=lambda:
                              [self.__size.set(20), self.new_game()])

        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.stop)

        # Adding the Game menu to the menubar
        self.__menubar.add_cascade(label="Game", menu=game_menu)
        self.__window.config(menu=self.__menubar)

    def new_game(self):
        """
        Creates new game

        """
        # Getting the size value
        size = self.__size.get()
        # Setting different sizes to the window depending on the game size
        if size == 10:
            self.__window.geometry("380x472")
        elif size == 15:
            self.__window.geometry("570x677")
        else:
            self.__window.geometry("760x882")

        # Creating an empty lists for the buttons and commands
        self.__buttons = []
        self.__commands = []

        # creating empty dict for tile numbers
        self.__tile_numbers = {}

        # Clearing the window of everything
        self.clear_frame()

        # Adding the buttons and commands to the list
        for row in range(size+2):
            self.__buttons.append([None] * size)
            self.__commands.append([None] * size)

        for y in range(2, size+2):
            # creating a dict into the dict so that searching
            # for buttons is easier: {2: {0: 0, 1: 0,..,14: 0}, 3: {0: 0,..}}
            dict_in_dict = {}
            self.__tile_numbers[y] = dict_in_dict

            for x in range(size):
                # Filling dict with zeros
                dict_in_dict[x] = 0

                # Creating the commands for the buttons
                def button_press(button_y_coord=y, button_x_coord=x):
                    # All buttons have the same "reveal" command at first
                    self.reveal(button_y_coord, button_x_coord)

                # Adding the command to list including the commands
                self.__commands[y][x] = button_press

                # Creating buttons
                new_button = Button(self.__window, command=button_press,
                                    width=4, height=2)
                # Adding button to the list including every button
                self.__buttons[y][x] = new_button
                # Adding the button to the grid
                new_button.grid(row=y, column=x)

        # Calling for a function that creates the mines
        self.mine_locations()

        # Counting tile numbers for every tile
        self.setting_tile_numbers()

        # Creating the labels for timer names and textvariables
        minutes_label = Label(textvariable=self.__minute)
        minutes = Label(text="Mins")

        seconds_label = Label(textvariable=self.__second)
        seconds = Label(text="Secs")

        # Putting the labels to the grid on the right side
        minutes.grid(row=0, column=size-2, sticky=E + W)
        seconds.grid(row=0, column=size-1, sticky=E + W)

        minutes_label.grid(row=1, column=size-2, sticky=N)
        seconds_label.grid(row=1, column=size-1, sticky=N)

        # If highscore exists display it (different highscores for different
        # sizes)
        if size == 10 and self.__10score != 99999:
            mins, secs = divmod(self.__10score, 60)
            highscore_label = Label(
                text="Highscore: " + str(mins) + ":" + str(secs))
            highscore_label.grid(row=0, column=3, columnspan=3, rowspan=2,
                                 sticky=W)

        elif size == 15 and self.__15score != 99999:
            mins, secs = divmod(self.__15score, 60)
            highscore_label = Label(
                text="Highscore: " + str(mins) + ":" + str(secs))
            highscore_label.grid(row=0, column=3, columnspan=3, rowspan=2,
                                 sticky=W)

        elif size == 20 and self.__20score != 99999:
            mins, secs = divmod(self.__20score, 60)
            highscore_label = Label(
                text="Highscore: " + str(mins) + ":" + str(secs))
            highscore_label.grid(row=0, column=3, columnspan=3, rowspan=2,
                                 sticky=W)

        # Setting the timer to 0 when starting a new game
        self.__temp = 0

        # Setting game_over status to false
        self.__game_over = False

    def won_game(self):
        """
        Checks if the game is won (checks if every button is disabled
        except mines)
        return: Bool, True if won
        """
        counter = 0
        size = self.__size.get()
        for y in range(2, size+2):
            for x in range(size):
                if self.__buttons[y][x].cget('state') == "disabled":
                    counter += 1

        if counter == size*size-self.__mine_count:
            return True

    def timer(self):
        """
        Works as a timer for the game
        """
        # divmod(mins = self.__temp//60, secs = self.__temp%60)
        mins, secs = divmod(self.__temp, 60)

        # Setting the values
        self.__minute.set(mins)
        self.__second.set(secs)

        # Adding 1 sec to the variable
        if not self.__game_over:
            self.__temp += 1

        # Start again after 1000ms=1s
        self.__window.after(1000, self.timer)

    def mine_locations(self):
        """
        Places the mines in the grid
        """
        size = self.__size.get()

        # Mine count depends on the size of the game
        if size == 10:
            self.__mine_count = 10
        elif size == 15:
            self.__mine_count = 25
        else:
            self.__mine_count = 40

        count = 0
        mine_coordinates = []
        while count < self.__mine_count:
            mine_list = []
            # Randomizing the places for the mines
            mine_x = random.randint(0, size - 1)
            mine_y = random.randint(2, size + 1)
            mine_list.append(mine_x)
            mine_list.append(mine_y)

            # Check for duplicates
            if mine_list in mine_coordinates:
                continue
            else:
                mine_coordinates.append(mine_list)
                count += 1

            # Adding the command to the list
            self.__commands[mine_y][mine_x] = self.explosion

            # Saving mines as -1 to matrix dict
            self.__tile_numbers[mine_y][mine_x] = -1

            mine_button = Button(self.__window, text="",
                                 command=self.explosion, width=4, height=2)

            self.__buttons[mine_y][mine_x] = mine_button
            mine_button.grid(row=mine_y, column=mine_x)

    def setting_tile_numbers(self):
        """
        Overwrites dict self.__tile_numbers to format where every button has
        number of mines touching it as value. If button is a mine, value is -1.
        """
        size = self.__size.get()

        for y in range(2, size+2):
            for x in range(size):

                if self.__tile_numbers[y][x] != -1:  # if button is not a mine

                    # going through every direction where
                    # a mine could be touching the tile
                    # using method get to avoid KeyError
                    if y != 2 and self.__tile_numbers.get(y-1).get(x-1) == -1:
                        self.__tile_numbers[y][x] += 1

                    if y != 2 and self.__tile_numbers.get(y-1).get(x) == -1:
                        self.__tile_numbers[y][x] += 1

                    if y != 2 and self.__tile_numbers.get(y-1).get(x+1) == -1:
                        self.__tile_numbers[y][x] += 1

                    if self.__tile_numbers.get(y).get(x-1) == -1:
                        self.__tile_numbers[y][x] += 1

                    if self.__tile_numbers.get(y).get(x+1) == -1:
                        self.__tile_numbers[y][x] += 1

                    if y != size+1 and self.__tile_numbers.get(y+1).get(x-1) == -1:
                        self.__tile_numbers[y][x] += 1

                    if y != size+1 and self.__tile_numbers.get(y+1).get(x) == -1:
                        self.__tile_numbers[y][x] += 1

                    if y != size+1 and self.__tile_numbers.get(y+1).get(x+1) == -1:
                        self.__tile_numbers[y][x] += 1

    def update_highscore(self):
        """
        If you made a better time than last time updates the highscore for the
        certain game (10x10,15x15,20x20)
        """
        size = self.__size.get()
        # Saving the time in seconds
        highscore = self.__temp

        # Different times and highscores for different sizes
        if size == 10 and highscore < self.__10score:
            self.__10score = highscore
            mins, secs = divmod(self.__10score, 60)
            highscore_label = Label(
                text="Highscore: " + str(mins) + ":" + str(secs))
            highscore_label.grid(row=0, column=3, columnspan=3, rowspan=2,
                                 sticky=W)

        elif size == 15 and highscore < self.__15score:
            self.__15score = highscore
            mins, secs = divmod(self.__15score, 60)
            highscore_label = Label(
                text="Highscore: " + str(mins) + ":" + str(secs))
            highscore_label.grid(row=0, column=3, columnspan=3, rowspan=2,
                                 sticky=W)

        elif size == 20 and highscore < self.__20score:
            self.__20score = highscore
            mins, secs = divmod(self.__20score, 60)
            highscore_label = Label(
                text="Highscore: " + str(mins) + ":" + str(secs))
            highscore_label.grid(row=0, column=3, columnspan=3, rowspan=2,
                                 sticky=W)

    def reveal(self, y, x):
        """
        Reveals tile's number when user clicks it.
        If number is zero, the mechanic is more complicated,
        calls another method to reveal zeros.

        :param y: Int, tile's y-coordinate
        :param x: Int, tile's x-coordinate
        """
        # searching for tile's number from dict
        number = self.__tile_numbers[y][x]

        if number != 0:

            # setting different color for numbers
            if number == 1:
                color = "cyan2"
            elif number == 2:
                color = "lawn green"
            elif number == 3:
                color = "pink"
            elif number == 4:
                color = "yellow"
            else:
                color = "deep pink"

            self.__buttons[y][x].configure(state='disabled', text=number,
                                           bg=color)
        else:
            self.click_zero(x, y)

        # Checks if the player has won the game
        if self.won_game():
            winner = Label(text="You Win!")
            self.__game_over = True
            winner.grid(row=0, column=0, columnspan=2, rowspan=2, sticky=W)
            # Checks if the score is better than the highscore
            self.update_highscore()

    def click_zero(self, x, y):
        """
        What happens if you click tile which doesnt touch any mine.
        :param y: tile's y-coordinate
        :param x: tile's x-coordinate
        """
        # Get the size of the board
        size = self.__size.get()

        # Return if the button is already disabled (already handled)
        if self.__buttons[y][x].cget('state') == "disabled":
            return
        # Get the number of the tile
        number = self.__tile_numbers[y][x]

        # If the button has a number greater than 0, revealing it
        if number > 0:
            if number == 1:
                color = "cyan2"
            elif number == 2:
                color = "lawn green"
            elif number == 3:
                color = "pink"
            elif number == 4:
                color = "yellow"
            else:
                color = "deep pink"
            self.__buttons[y][x].configure(state='disabled', text=number,
                                           bg=color)
        else:  # number = 0
            self.__buttons[y][x].configure(state='disabled', bg='gray66')

        # Create a loop where u check the close by buttons to see if they are
        # 0's too, but doesn't go over the grid
        if number == 0:
            if x != 0 and y != 2:
                self.click_zero(x - 1, y - 1)
            if x != 0:
                self.click_zero(x - 1, y)
            if x != 0 and y != size + 1:
                self.click_zero(x - 1, y + 1)
            if y != 2:
                self.click_zero(x, y - 1)
            if y != size + 1:
                self.click_zero(x, y + 1)
            if x != size - 1 and y != 2:
                self.click_zero(x + 1, y - 1)
            if x != size - 1:
                self.click_zero(x + 1, y)
            if x != size - 1 and y != size + 1:
                self.click_zero(x + 1, y + 1)

    def explosion(self):
        """
        What happens when a mine button is pressed
        """
        loser = Label(text="You Lose!")
        loser.grid(row=0, column=0, columnspan=2, rowspan=2, sticky=W)

        self.__game_over = True
        size = self.__size.get()

        # Disabling all the buttons in game and revealing all bombs
        for y in range(2, size + 2):
            for x in range(size):
                if self.__tile_numbers[y][x] == -1:
                    self.__buttons[y][x].configure(bg='black')
                self.__buttons[y][x].configure(state='disabled')


    def stop(self):
        """
        Ends the execution of the program.
        """
        self.__window.destroy()

    def start(self):
        """
        Starts the execution of the program.
        """
        self.__window.mainloop()


def main():

    minesweeper = Minesweeper()
    minesweeper.start()


if __name__ == "__main__":
    main()
