import tkinter as tk
from tkinter import messagebox
import random, copy, math

# --- Core Graph Class ---
class Graph:
    def __init__(self, nodes=None):
        self.adj = {}
        if nodes:
            for n in nodes:
                self.add_node(n)

    def add_node(self, v):
        if v not in self.adj:
            self.adj[v] = set()

    def add_edge(self, a, b):
        if a == b:
            return
        for v in (a, b):
            if v not in self.adj:
                self.add_node(v)
        self.adj[a].add(b)
        self.adj[b].add(a)

    def neighbors(self, v):
        return self.adj[v]

    def nodes(self):
        return list(self.adj.keys())

# --- n-colorability check ---
def is_n_colorable(graph, n):
    color = {}
    nodes = graph.nodes()
    def backtrack(idx):
        if idx == len(nodes):
            return True
        v = nodes[idx]
        for c in range(n):
            if all(color.get(u) != c for u in graph.neighbors(v)):
                color[v] = c
                if backtrack(idx+1):
                    return True
                del color[v]
        return False
    return backtrack(0)

# --- Game Logic ---
class GraphColoringGame:
    def __init__(self, graph, n_colors, first_turn="Painter"):
        self.graph = graph
        self.n = n_colors
        self.color = {v: None for v in graph.nodes()}
        self.turn = first_turn

    def legal_colors_for_vertex(self, v):
        used = {self.color[u] for u in self.graph.neighbors(v) if self.color[u] is not None}
        return [c for c in range(self.n) if c not in used]

    def is_over(self):
        if all(self.color[v] is not None for v in self.graph.nodes()):
            return True
        for v in self.graph.nodes():
            if self.color[v] is None and not self.legal_colors_for_vertex(v):
                return True
        return False

    def winner(self):
        if all(self.color[v] is not None for v in self.graph.nodes()):
            return "Painter"
        if any(self.color[v] is None and not self.legal_colors_for_vertex(v) for v in self.graph.nodes()):
            return "Spoiler"
        return None

# --- AI ---
def random_ai(game):
    moves = []
    for v in game.graph.nodes():
        if game.color[v] is None:
            for c in game.legal_colors_for_vertex(v):
                moves.append((v, c))
    return random.choice(moves) if moves else None

def minimax_ai(game, depth=3):
    def evaluate_position(g):
        dead = sum(1 for v in g.color if g.color[v] is None and not g.legal_colors_for_vertex(v))
        uncolored = sum(1 for v in g.color if g.color[v] is None)
        return uncolored - 3 * dead
    def minimax(g, depth, maximizing):
        if depth == 0 or g.is_over():
            score = evaluate_position(g)
            if g.winner() == "Painter": score += 1000
            elif g.winner() == "Spoiler": score -= 1000
            return score, None
        moves = []
        for v in g.graph.nodes():
            if g.color[v] is None:
                for c in g.legal_colors_for_vertex(v):
                    moves.append((v, c))
        if not moves:
            return evaluate_position(g), None
        if maximizing:
            best_val, best_move = -math.inf, None
            for move in moves:
                g2 = copy.deepcopy(g)
                g2.color[move[0]] = move[1]
                g2.turn = "Spoiler"
                val, _ = minimax(g2, depth-1, False)
                if val > best_val:
                    best_val, best_move = val, move
            return best_val, best_move
        else:
            best_val, best_move = math.inf, None
            for move in moves:
                g2 = copy.deepcopy(g)
                g2.color[move[0]] = move[1]
                g2.turn = "Painter"
                val, _ = minimax(g2, depth-1, True)
                if val < best_val:
                    best_val, best_move = val, move
            return best_val, best_move
    _, move = minimax(game, depth, game.turn == "Painter")
    return move

# --- GUI ---
class GraphColoringGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Urinal Game")

        self.canvas = tk.Canvas(master, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<ButtonRelease-1>", self.left_release)
        self.canvas.bind("<Button-3>", self.right_click_start)
        self.canvas.bind("<B3-Motion>", self.right_drag)
        self.canvas.bind("<ButtonRelease-3>", self.right_release)
        self.master.bind("<Configure>", self.on_resize)

        self.status = tk.Label(master, text="Draw graph: left click vertices/edges, right click to drag", font=("Arial", 12))
        self.status.pack()

        self.graph = Graph()
        self.node_positions = {}
        self.node_circles = {}
        self.color_palette = ["#FF6666", "#66FF66", "#6666FF", "#FFFF66", "#FF66FF", "#66FFFF"]
        self.history = []

        self.game = None
        self.mode = "edit"
        self.selected_color = None
        self.current_mode = "HvC"
        self.ai_type = "random"
        self.ai_depth = 2
        self.num_colors = 3
        self.first_turn = "Painter"
        self.painter_type = "Human"
        self.painter_is_human = True
        self.spoiler_is_human = False
        self.dragging_node = None
        self.left_drag_start = None
        self.game_over_popup_shown = False
        self.waiting_for_human = False

        # Panel
        self.panel_frame = tk.Frame(self.canvas, bg="#dddddd", bd=2, relief="raised")
        self.panel_frame.place(x=5, y=5)
        self.play_mode_buttons = {}
        self.ai_type_buttons = {}
        self.first_turn_buttons = {}
        self.painter_type_buttons = {}

        row=0
        tk.Label(self.panel_frame, text="Play Mode:").grid(row=row,column=0,columnspan=3, sticky="w")
        row+=1
        for i,mode in enumerate(["HvH","HvC","CvC"]):
            btn=tk.Button(self.panel_frame,text=mode,width=5,command=lambda m=mode:self.set_play_mode(m))
            btn.grid(row=row,column=i)
            self.play_mode_buttons[mode]=btn
        row+=1

        tk.Label(self.panel_frame,text="AI Type:").grid(row=row,column=0,columnspan=2, sticky="w")
        row+=1
        for i,ai in enumerate(["random","minimax"]):
            btn=tk.Button(self.panel_frame,text=ai,width=7,command=lambda a=ai:self.set_ai_type(a))
            btn.grid(row=row,column=i)
            self.ai_type_buttons[ai]=btn
        row+=1

        tk.Label(self.panel_frame,text="Minimax Depth:").grid(row=row,column=0, sticky="w")
        self.depth_entry=tk.Entry(self.panel_frame,width=5)
        self.depth_entry.insert(0,str(self.ai_depth))
        self.depth_entry.grid(row=row,column=1)
        row+=1

        tk.Label(self.panel_frame,text="Num Colors:").grid(row=row,column=0, sticky="w")
        self.colors_entry=tk.Entry(self.panel_frame,width=5)
        self.colors_entry.insert(0,str(self.num_colors))
        self.colors_entry.grid(row=row,column=1)
        row+=1

        tk.Label(self.panel_frame,text="First Turn:").grid(row=row,column=0, sticky="w")
        row+=1
        for i,ft in enumerate(["Painter","Spoiler"]):
            btn=tk.Button(self.panel_frame,text=ft,width=7,command=lambda f=ft:self.set_first_turn(f))
            btn.grid(row=row,column=i)
            self.first_turn_buttons[ft]=btn
        row+=1

        tk.Label(self.panel_frame,text="Painter Type:").grid(row=row,column=0, sticky="w")
        row+=1
        for i,pt in enumerate(["Human","Computer"]):
            btn=tk.Button(self.panel_frame,text=pt,width=7,command=lambda p=pt:self.set_painter_type(p))
            btn.grid(row=row,column=i)
            self.painter_type_buttons[pt]=btn
        row+=1

        tk.Button(self.panel_frame,text="Start Game",command=self.start_game,bg="#88ff88").grid(row=row,column=0,columnspan=2,pady=3)
        tk.Button(self.panel_frame,text="Undo",command=self.undo_action).grid(row=row,column=2)
        tk.Button(self.panel_frame,text="Reset",command=self.reset_graph).grid(row=row,column=3)

        self.color_frame = tk.Frame(self.canvas, bg="#cccccc")
        self.color_buttons=[]
        self.color_frame.place_forget()

        self.update_highlights()

    # --- Panel methods ---
    def update_highlights(self):
        for m,btn in self.play_mode_buttons.items():
            btn.config(bg="#88ff88" if m==self.current_mode else "#f0f0f0")
        for a,btn in self.ai_type_buttons.items():
            btn.config(bg="#88ff88" if a==self.ai_type else "#f0f0f0")
        for f,btn in self.first_turn_buttons.items():
            btn.config(bg="#88ff88" if f==self.first_turn else "#f0f0f0")
        for p,btn in self.painter_type_buttons.items():
            btn.config(bg="#88ff88" if p==self.painter_type else "#f0f0f0")
            # Disable disallowed buttons based on mode
            if self.current_mode=="HvH":
                btn.config(state="disabled" if p=="Computer" else "normal")
            elif self.current_mode=="CvC":
                btn.config(state="disabled" if p=="Human" else "normal")
            else:
                btn.config(state="normal")

    def set_play_mode(self, mode):
        self.current_mode = mode
        # Enforce painter type automatically
        if mode=="HvH":
            self.painter_type="Human"
        elif mode=="CvC":
            self.painter_type="Computer"
        self.update_highlights()
        self.status.config(text=f"Mode set to {mode}")


    def set_ai_type(self, ai):
        self.ai_type=ai
        self.status.config(text=f"AI set to {ai}")
        self.update_highlights()

    def set_first_turn(self, ft):
        self.first_turn=ft
        self.status.config(text=f"First turn: {ft}")
        self.update_highlights()

    def set_painter_type(self, pt):
        self.painter_type=pt
        self.status.config(text=f"Painter: {pt}")
        self.update_highlights()

    # --- Mouse methods ---
    def left_click(self, event):
        if self.mode != "edit": return
        clicked = self.find_node_at(event.x, event.y)
        if clicked: self.left_drag_start = clicked
        else:
            name = chr(65 + len(self.node_positions))
            self.graph.add_node(name)
            self.node_positions[name] = (event.x, event.y)
            self.history.append(("add_node", name))
            self.draw_graph()

    def left_release(self, event):
        if self.mode != "edit" or not self.left_drag_start: return
        end = self.find_node_at(event.x, event.y)
        if end and end != self.left_drag_start:
            self.graph.add_edge(self.left_drag_start, end)
            self.history.append(("add_edge", (self.left_drag_start, end)))
            self.draw_graph()
        self.left_drag_start = None

    def right_click_start(self,event):
        if self.mode!="edit": return
        clicked=self.find_node_at(event.x,event.y)
        if clicked: self.dragging_node=clicked

    def right_drag(self,event):
        if self.mode!="edit" or not self.dragging_node: return
        self.node_positions[self.dragging_node]=(event.x,event.y)
        self.draw_graph()

    def right_release(self,event):
        self.dragging_node=None

    def find_node_at(self,x,y):
        for node,(nx,ny) in self.node_positions.items():
            if (x-nx)**2+(y-ny)**2<25**2: return node
        return None

    def undo_action(self):
        if not self.history: return
        action,data=self.history.pop()
        if action=="add_node":
            node=data
            self.graph.adj.pop(node,None)
            self.node_positions.pop(node,None)
            for v in self.graph.adj: self.graph.adj[v].discard(node)
        elif action=="add_edge":
            a,b=data
            self.graph.adj[a].discard(b)
            self.graph.adj[b].discard(a)
        self.draw_graph()

    def on_resize(self,event):
        self.draw_graph()

    # --- Color Buttons ---
    def update_color_buttons(self):
        for btn in self.color_buttons:
            btn.destroy()
        self.color_buttons=[]
        for i in range(self.num_colors):
            c=self.color_palette[i]
            btn=tk.Button(self.color_frame,bg=c,width=4,command=lambda col=i:self.choose_color(col))
            btn.pack(side="left", padx=2)
            self.color_buttons.append(btn)
        self.update_color_selection_highlight()

    def update_color_selection_highlight(self):
        for i,btn in enumerate(self.color_buttons):
            btn.config(relief="sunken" if self.selected_color==i else "raised")

    def choose_color(self,c):
        self.selected_color=c
        self.update_color_selection_highlight()
        # If waiting for human turn, process it immediately
        if self.waiting_for_human:
            self.waiting_for_human=False
            self.next_turn_ai()

    # --- Start / Reset ---
    def start_game(self):
        try:
            self.ai_depth=int(self.depth_entry.get())
            self.num_colors=int(self.colors_entry.get())
        except:
            messagebox.showerror("Error","Invalid depth or number of colors")
            return
        if len(self.node_positions)==0:
            messagebox.showerror("Error","Draw at least one vertex")
            return
        if not is_n_colorable(self.graph,self.num_colors):
            messagebox.showerror("Error",f"Graph cannot be colored with {self.num_colors} colors")
            return
        self.mode="play"
        self.game=GraphColoringGame(self.graph,self.num_colors,self.first_turn)
        self.selected_color=None
        self.game_over_popup_shown=False

        self.painter_is_human = (self.painter_type=="Human")
        if self.current_mode=="HvH":
            self.spoiler_is_human = True
        elif self.current_mode=="HvC":
            self.spoiler_is_human = not self.painter_is_human
        elif self.current_mode=="CvC":
            self.spoiler_is_human = False

        self.update_color_buttons()
        self.color_frame.place(x=5, y=self.canvas.winfo_height()-50)
        self.status.config(text=f"{self.game.turn}'s turn")
        self.draw_graph()
        self.waiting_for_human = False
        self.master.after(500, self.next_turn_ai)

    def reset_graph(self):
        self.graph=Graph()
        self.node_positions.clear()
        self.node_circles.clear()
        self.game=None
        self.mode="edit"
        self.selected_color=None
        self.dragging_node=None
        self.left_drag_start=None
        self.history.clear()
        self.game_over_popup_shown=False
        self.waiting_for_human=False
        self.canvas.delete("all")
        self.color_frame.place_forget()
        self.canvas.create_window(5,5,anchor="nw",window=self.panel_frame)
        self.status.config(text="Draw graph: left click vertices/edges, right click to drag")

    # --- Draw ---
    def draw_graph(self):
        self.canvas.delete("all")
        radius=25
        for a in self.graph.adj:
            for b in self.graph.adj[a]:
                if a<b:
                    xa,ya=self.node_positions[a]
                    xb,yb=self.node_positions[b]
                    self.canvas.create_line(xa,ya,xb,yb,fill="black")
        for node,(x,y) in self.node_positions.items():
            fill="white"
            if self.game and self.game.color.get(node) is not None:
                fill=self.color_palette[self.game.color[node]]
            circ=self.canvas.create_oval(x-radius,y-radius,x+radius,y+radius,fill=fill,outline="black",width=2)
            self.canvas.create_text(x,y,text=node,font=("Arial",12))
            self.canvas.tag_bind(circ,"<Button-1>",lambda e,n=node:self.click_node(n))
            self.node_circles[node]=circ
        self.canvas.create_window(5,5,anchor="nw",window=self.panel_frame)
        if self.mode=="play":
            self.color_frame.place(x=5, y=self.canvas.winfo_height()-50)

    # --- Gameplay ---
    def click_node(self,node):
        if self.mode!="play": return
        turn_is_human = (self.game.turn=="Painter" and self.painter_is_human) or \
                        (self.game.turn=="Spoiler" and self.spoiler_is_human)
        if not turn_is_human: return
        if self.selected_color is None:
            self.status.config(text="Choose color first")
            return
        if self.game.color[node] is not None:
            self.status.config(text="Vertex already colored")
            return
        if self.selected_color not in self.game.legal_colors_for_vertex(node):
            self.status.config(text="Illegal color")
            return
        self.game.color[node] = self.selected_color
        self.draw_graph()
        if self.game.is_over(): self.end_game(); return
        self.game.turn = "Painter" if self.game.turn=="Spoiler" else "Spoiler"
        self.next_turn_ai()  # immediately trigger next turn

    def next_turn_ai(self):
        if self.mode != "play" or self.game_over_popup_shown: return
        if self.game.is_over():
            self.end_game()
            return

        if self.game.turn=="Painter":
            ai_turn = not self.painter_is_human
            self.waiting_for_human = not ai_turn
        else:
            ai_turn = not self.spoiler_is_human
            self.waiting_for_human = not ai_turn

        if ai_turn:
            move = minimax_ai(self.game, self.ai_depth) if self.ai_type=="minimax" else random_ai(self.game)
            if move:
                v,c = move
                self.game.color[v] = c
                self.draw_graph()
            if self.game.is_over():
                self.end_game()
                return
            self.game.turn = "Painter" if self.game.turn=="Spoiler" else "Spoiler"
            self.master.after(500, self.next_turn_ai)

    def end_game(self):
        if self.game_over_popup_shown: return
        winner=self.game.winner()
        if winner:
            self.status.config(text=f"{winner} wins! Reset to play again")
            messagebox.showinfo("Game Over",f"{winner} wins!")
            self.game_over_popup_shown=True

# --- Run ---
if __name__=="__main__":
    root=tk.Tk()
    app=GraphColoringGUI(root)
    root.mainloop()
