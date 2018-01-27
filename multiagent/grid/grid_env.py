import time
import numpy as np
import tkinter as tk
from PIL import ImageTk, Image

np.random.seed(1)
PhotoImage = ImageTk.PhotoImage
UNIT = 100  # pixels
HEIGHT = 5  # grid height
WIDTH = 5  # grid width

class Victim(object):
    def __init__(self, victim_id):
        self.id = victim_id
        self.pos = None
        self.resource_id = None

    def get_id(self):
        return self.id

    def set_position(self, pos):
        self.pos = pos

    def get_position(self):
        return self.pos

    def set_resource_id(self, resource_id):
        if self.resource_id is not None:
            raise Exception("Resource id for this victim has been assigned to " + self.resource_id)

        self.resource_id = resource_id

    def get_resource_id(self):
        return self.resource_id


class Env(tk.Tk):
    def __init__(self, max_agent_count, max_victim_count):
        super(Env, self).__init__()
        self.action_space = ['u', 'd', 'l', 'r']
        self.max_a_count = max_agent_count
        self.max_v_count = max_victim_count
        self.n_actions = len(self.action_space)

        self.title('Q Learning')
        self.geometry('{0}x{1}'.format(HEIGHT * UNIT, HEIGHT * UNIT))
        self.shapes = self.load_images()

        self.canvas = self._build_canvas()

        self._reset_agents()
        self.texts = []
        self.agents = []
        self.agent_positions = {}

        self.victims = []
        self.victim_positions = {}

    def _build_canvas(self):
        canvas = tk.Canvas(self, bg='white',
                           height=HEIGHT * UNIT,
                           width=WIDTH * UNIT)
        # create grids
        for c in range(0, WIDTH * UNIT, UNIT):  # 0~400 by 80
            x0, y0, x1, y1 = c, 0, c, HEIGHT * UNIT
            canvas.create_line(x0, y0, x1, y1)
        for r in range(0, HEIGHT * UNIT, UNIT):  # 0~400 by 80
            x0, y0, x1, y1 = 0, r, HEIGHT * UNIT, r
            canvas.create_line(x0, y0, x1, y1)
        #
        # # add img to canvas
        # self.rectangle = canvas.create_image(50, 50, image=self.shapes[0])
        # self.triangle1 = canvas.create_image(250, 150, image=self.shapes[1])
        # self.triangle2 = canvas.create_image(150, 250, image=self.shapes[1])
        #
        #
        # self.circle = canvas.create_image(250, 250, image=self.shapes[2])
        #
        # # pack all
        # canvas.pack()

        return canvas

    def pack_canvas(self):
        self.canvas.pack()

    def load_images(self):
        rectangle = PhotoImage(
            Image.open("../img/rectangle.png").resize((65, 65)))
        triangle = PhotoImage(
            Image.open("../img/triangle.png").resize((65, 65)))
        circle = PhotoImage(
            Image.open("../img/circle.png").resize((65, 65)))

        return rectangle, triangle, circle

    def text_value(self, row, col, contents, action, font='Helvetica', size=10,
                   style='normal', anchor="nw"):

        if action == 0:
            origin_x, origin_y = 7, 42
        elif action == 1:
            origin_x, origin_y = 85, 42
        elif action == 2:
            origin_x, origin_y = 42, 5
        else:
            origin_x, origin_y = 42, 77

        x, y = origin_y + (UNIT * col), origin_x + (UNIT * row)
        font = (font, str(size), style)
        text = self.canvas.create_text(x, y, fill="black", text=contents,
                                       font=font, anchor=anchor)
        return self.texts.append(text)

    def print_value_all(self, q_table):
        for i in self.texts:
            self.canvas.delete(i)
        self.texts.clear()
        for i in range(HEIGHT):
            for j in range(WIDTH):
                for action in range(0, 4):
                    state = [i, j]
                    if str(state) in q_table.keys():
                        temp = q_table[str(state)][action]
                        self.text_value(j, i, round(temp, 2), action)

    def coords_to_state(self, coords):
        x = int((coords[0] - 50) / 100)
        y = int((coords[1] - 50) / 100)
        return [x, y]

    def state_to_coords(self, state):
        x = int(state[0] * 100 + 50)
        y = int(state[1] * 100 + 50)
        return [x, y]

    def _reset_agents(self):
        x, y = self.canvas.coords(self.rectangle)
        self.canvas.move(self.rectangle, UNIT / 2 - x, UNIT / 2 - y)

    # return the state of the agent (position of the agent in the grid)
    def reset(self):
        self.update()
        time.sleep(0.5)

        self._reset_agents()

        self.render()
        coords = self.canvas.coords(self.rectangle)

        # return observation
        return self.coords_to_state(coords=coords)

    def reset_n(self):
        self.update()
        time.sleep(0.5)

        # set random position for agents

        self.render()


    def step(self, action):
        state = self.canvas.coords(self.rectangle)
        base_action = np.array([0, 0])
        self.render()

        if action == 0:  # up
            if state[1] > UNIT:
                base_action[1] -= UNIT
        elif action == 1:  # down
            if state[1] < (HEIGHT - 1) * UNIT:
                base_action[1] += UNIT
        elif action == 2:  # left
            if state[0] > UNIT:
                base_action[0] -= UNIT
        elif action == 3:  # right
            if state[0] < (WIDTH - 1) * UNIT:
                base_action[0] += UNIT

        # move agent
        self.canvas.move(self.rectangle, base_action[0], base_action[1])
        # move rectangle to top level of canvas
        self.canvas.tag_raise(self.rectangle)
        next_state = self.canvas.coords(self.rectangle)

        # reward function
        if next_state == self.canvas.coords(self.circle):
            reward = 100
            done = True
        elif next_state in [self.canvas.coords(self.triangle1),
                            self.canvas.coords(self.triangle2)]:
            reward = -100
            done = True
        else:
            reward = 0
            done = False

        next_state = self.coords_to_state(next_state)
        return next_state, reward, done

    def render(self):
        time.sleep(0.03)
        self.update()

    def _contain_agent(self, agent):
        for a in self.agents:
            if a.get_id() == agent.get_id():
                return True

        return False

    def add_agent(self, agent):
        if self._contain_agent(agent):
            return False

        if len(self.agents) >= self.max_a_count:
            return False

        positions = self.agent_positions.values()

        pos = self._generate_new_position(positions)
        self.agent_positions[agent.get_agent_id()] = pos

        # add image
        r_pixel = self.get_row_center_pixel(pos)
        c_pixel = self.get_column_center_pixel(pos)

        resource_id = self.canvas.create_image(r_pixel, c_pixel, image=self.shapes[0])
        agent.set_resource_id(resource_id)

        self.agents.append(agent)

        return agent

    def set_agent_position(self, agent):
        del self.agent_positions[agent.get_id()]

    def _generate_new_position(self, existing_positions):
        while True:
            pos = np.random.randint(0, WIDTH * HEIGHT)
            if pos not in existing_positions:
                return pos

    def add_victim(self):
        if len(self.victims) > self.max_v_count:
            return False

        v = Victim(len(self.victims))

        positions = self.victim_positions.values()

        pos = self._generate_new_position(positions)
        self.victim_positions[v.get_id()] = pos

        # add image
        r_pixel = self.get_row_center_pixel(pos)
        c_pixel = self.get_column_center_pixel(pos)
        resource_id = self.canvas.create_image(r_pixel, c_pixel, image=self.shapes[2])
        v.set_resource_id(resource_id)

        self.victims.append(v)

        return v

    def get_row(self, pos):
        return pos // WIDTH

    def get_col(self, pos):
        return pos % WIDTH

    def get_row_center_pixel(self, pos):
        row = self.get_row(pos)

        return row*UNIT + UNIT / 2

    def get_column_center_pixel(self, pos):
        col = self.get_col(pos)

        return col*UNIT + UNIT / 2
