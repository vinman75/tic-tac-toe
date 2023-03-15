import tkinter as tk
from PIL import ImageTk, Image
import random
import threading


class TicTacToe:
    def __init__(self):

        self.player_x_score = 0
        self.player_o_score = 0
        self.window = tk.Tk()
        self.window.resizable(False, False)
        self.window.wm_attributes("-toolwindow", True)
        self.current_player = random.choice(["X", "O"])

        self.status_label = tk.Label(self.window, text=f"Player {self.current_player}'s Turn", bg='#2c2c2c', fg='#ffffff')

        image_size = (50, 50)  # Set the desired size for the images
        # Create a transparent background with the desired size
        transparent_bg = Image.new('RGBA', image_size, (0, 0, 0, 0))
        # Create an empty_image with the same size as the other images
        self.empty_image = ImageTk.PhotoImage(transparent_bg)
        # Load the image, resize it, and composite it onto the transparent background
        self.x_image = ImageTk.PhotoImage(Image.alpha_composite(transparent_bg, Image.open("images/X.png").convert('RGBA').resize(image_size, Image.LANCZOS)))
        self.o_image = ImageTk.PhotoImage(Image.alpha_composite(transparent_bg, Image.open("images/O.png").convert('RGBA').resize(image_size, Image.LANCZOS)))
        self.blank_image = ImageTk.PhotoImage(transparent_bg)  # Create a transparent image for initial button state

        self.window.title("Tic Tac Toe")
        self.window.configure(bg='#2c2c2c')

        self.board = [[None, None, None],
                      [None, None, None],
                      [None, None, None]]
        self.current_player = "X"

        for i in range(3):
            for j in range(3):
                self.board[i][j] = tk.Button(self.window, image=self.blank_image, text="", command=lambda i=i, j=j: self.on_click(i, j),
                                            bg='#4a4a4a', fg='#ffffff', activebackground='#666666', activeforeground='#ffffff',
                                            compound='center')
                self.board[i][j].grid(row=i, column=j)
                self.board[i][j].config(width=self.x_image.width(), height=self.x_image.height(), padx=0, pady=0)

        self.status_label = tk.Label(self.window, text="Player X's Turn", bg='#2c2c2c', fg='#ffffff')
        self.status_label.grid(row=3, column=0, columnspan=3)

        self.new_game_button = tk.Button(self.window, text="New Game", command=self.reset_game,
                                        bg='#4a4a4a', fg='#ffffff', activebackground='#666666', activeforeground='#ffffff')
        self.new_game_button.grid(row=3, column=3)  # Change this line

        # Add scoreboard labels
        self.scoreboard_label = tk.Label(self.window, text="Scoreboard", bg='#2c2c2c', fg='#ffffff')
        self.scoreboard_label.grid(row=0, column=3)
        self.player_x_score_label = tk.Label(self.window, text=f"Player X: {self.player_x_score}", bg='#2c2c2c', fg='#ffffff')
        self.player_x_score_label.grid(row=1, column=3)
        self.player_o_score_label = tk.Label(self.window, text=f"Player O: {self.player_o_score}", bg='#2c2c2c', fg='#ffffff')
        self.player_o_score_label.grid(row=2, column=3)
        self.start_game()
        self.window.mainloop()


    def reset_game(self):
        self.current_player = "X"
        self.status_label["text"] = "Player X's Turn"
        for i in range(3):
            for j in range(3):
                self.board[i][j]["text"] = ""

    def on_click(self, i, j):
        if self.board[i][j]["text"] == "" and not self.check_winner():
            self.board[i][j]["text"] = self.current_player
            self.board[i][j].config(image=self.x_image if self.current_player == "X" else self.o_image)

            if self.check_winner():
                self.status_label["text"] = f"Player {self.current_player} Wins!"
                if self.current_player == "X":
                    self.player_x_score += 1
                else:
                    self.player_o_score += 1
                self.update_scoreboard()
                self.set_new_game_button_color('#00ff00')  # Add this line
            elif self.check_draw():
                self.status_label["text"] = "It's a Draw!"
                self.set_new_game_button_color('#00ff00')  # Add this line
            else:
                self.current_player = "O"
                self.status_label["text"] = "AI is thinking..."
                self.window.after(250, self.ai_move)


    def ai_move(self):
        ai_thread = threading.Thread(target=self._ai_move, daemon=True)
        ai_thread.start()


    def _ai_move(self):
        game_state = TicTacToeGameState()
        game_state.board = [[self.board[i][j]["text"] for j in range(3)] for i in range(3)]
        game_state.current_player = self.current_player

        best_score = float('-inf')
        best_move = None

        for i in range(3):
            for j in range(3):
                if game_state.is_empty(i, j):
                    game_state.make_move(i, j)
                    score = self.minimax(game_state, False)
                    game_state.undo_move(i, j)
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)

        self.window.after(0, lambda: self.update_move_on_gui(best_move))


    def update_move_on_gui(self, best_move):
        self.board[best_move[0]][best_move[1]]["text"] = self.current_player
        self.board[best_move[0]][best_move[1]].config(image=self.x_image if self.current_player == "X" else self.o_image)

        if self.check_winner():
            self.status_label["text"] = f"Player {self.current_player} Wins!"
            if self.current_player == "X":
                self.player_x_score += 1
            else:
                self.player_o_score += 1
            self.update_scoreboard()
            self.set_new_game_button_color('#00ff00')
        elif self.check_draw():
            self.status_label["text"] = "It's a Draw!"
            self.set_new_game_button_color('#00ff00')
        else:
            self.current_player = "X"
            self.status_label["text"] = f"Player {self.current_player}'s Turn"


    def minimax(self, game_state, is_maximizing, alpha=float('-inf'), beta=float('inf')):
        result = game_state.get_winner()
        if result is not None:
            return {"X": -1, "O": 1, "Draw": 0}[result]

        if is_maximizing:
            best_score = float('-inf')
            for i in range(3):
                for j in range(3):
                    if game_state.is_empty(i, j):
                        game_state.make_move(i, j)
                        score = self.minimax(game_state, False, alpha, beta)
                        game_state.undo_move(i, j)
                        best_score = max(score, best_score)
                        alpha = max(alpha, best_score)
                        if beta <= alpha:
                            break
            return best_score
        else:
            best_score = float('inf')
            for i in range(3):
                for j in range(3):
                    if game_state.is_empty(i, j):
                        game_state.make_move(i, j)
                        score = self.minimax(game_state, True, alpha, beta)
                        game_state.undo_move(i, j)
                        best_score = min(score, best_score)
                        beta = min(beta, best_score)
                        if beta <= alpha:
                            break
            return best_score


    def check_winner(self):
        for row in self.board:
            if row[0]["text"] == row[1]["text"] == row[2]["text"] != "":
                return row[0]["text"]
        for col in range(3):
            if self.board[0][col]["text"] == self.board[1][col]["text"] == self.board[2][col]["text"] != "":
                return self.board[0][col]["text"]
        if self.board[0][0]["text"] == self.board[1][1]["text"] == self.board[2][2]["text"] != "":
            return self.board[0][0]["text"]
        if self.board[0][2]["text"] == self.board[1][1]["text"] == self.board[2][0]["text"] != "":
            return self.board[0][2]["text"]
        return None


    def check_draw(self):
        for row in self.board:
            for button in row:
                if button["text"] == "":
                    return False
        return True


    def reset_game(self):
        for i in range(3):
            for j in range(3):
                self.board[i][j]["text"] = ""
                self.board[i][j].config(image=self.empty_image)
        self.set_new_game_button_color('#4a4a4a')
        self.start_game()


    def start_game(self):
        self.current_player = random.choice(["X", "O"])
        self.status_label["text"] = f"Player {self.current_player}'s Turn"
        if self.current_player == "O":
            self.status_label["text"] = "AI is thinking..."
            self.window.after(250, self.ai_move)


    def update_scoreboard(self):
        self.player_x_score_label["text"] = f"Player X: {self.player_x_score}"
        self.player_o_score_label["text"] = f"AI O: {self.player_o_score}"

    def set_new_game_button_color(self, color):
        self.new_game_button.configure(bg=color, activebackground=color)


class TicTacToeGameState:
    def __init__(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'

    def make_move(self, i, j):
        if self.board[i][j] == '':
            self.board[i][j] = self.current_player

    def undo_move(self, i, j):
        self.board[i][j] = ''

    def get_winner(self):
        for row in self.board:
            if row[0] == row[1] == row[2] != '':
                return row[0]
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                return self.board[0][col]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return self.board[0][2]
        return None

    def is_draw(self):
        for row in self.board:
            for cell in row:
                if cell == '':
                    return False
        return True

    def is_empty(self, i, j):
        return self.board[i][j] == ''

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'


if __name__ == "__main__":
    TicTacToe()