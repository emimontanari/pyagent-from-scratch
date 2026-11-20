import tkinter as tk
import random

class SnakeGame:
    def __init__(self, master):
        self.master = master
        self.master.title('Snake Game')
        self.canvas = tk.Canvas(self.master, width=400, height=400, bg='black')
        self.canvas.pack()
        self.snake = [(20, 20), (20, 30), (20, 40)]
        self.food = self.place_food()
        self.direction = 'Down'
        self.score = 0
        self.game_over = False
        self.master.bind('<KeyPress>', self.change_direction)
        self.update_game()

    def place_food(self):
        x = random.randint(0, 39) * 10
        y = random.randint(0, 39) * 10
        return (x, y) 

    def change_direction(self, event):
        if event.keysym in ['Up', 'Down', 'Left', 'Right']:
            self.direction = event.keysym

    def update_game(self):
        if self.game_over:
            self.canvas.create_text(200, 200, text='Game Over', fill='white', font=('Arial', 30))
            self.canvas.create_text(200, 250, text=f'Score: {self.score}', fill='white', font=('Arial', 20))
            return

        head_x, head_y = self.snake[0]
        if self.direction == 'Up':
            head_y -= 10
        elif self.direction == 'Down':
            head_y += 10
        elif self.direction == 'Left':
            head_x -= 10
        elif self.direction == 'Right':
            head_x += 10

        new_head = (head_x, head_y)

        # Check for collisions
        if (head_x < 0 or head_x >= 400 or head_y < 0 or head_y >= 400 or new_head in self.snake):
            self.game_over = True

        # Check for food
        if new_head == self.food:
            self.snake.insert(0, new_head)
            self.food = self.place_food()
            self.score += 1
        else:
            self.snake.insert(0, new_head)
            self.snake.pop()

        self.draw()
        self.master.after(100, self.update_game)

    def draw(self):
        self.canvas.delete(tk.ALL)
        for segment in self.snake:
            self.canvas.create_rectangle(segment[0], segment[1], segment[0] + 10, segment[1] + 10, fill='green')
        food_x, food_y = self.food
        self.canvas.create_oval(food_x, food_y, food_x + 10, food_y + 10, fill='red')
        self.canvas.create_text(350, 10, text=f'Score: {self.score}', fill='white', font=('Arial', 12))

if __name__ == '__main__':
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()