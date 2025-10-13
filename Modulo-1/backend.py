import heapq
import copy

# NUEVA VERSION
class PuzzleSolver:
    def __init__(self, goal_state=None):
        self.goal_state = goal_state if goal_state else [[1,2,3],[4,5,6],[7,8,0]]
        self._update_goal_positions()

    def set_goal_state(self, new_goal):
        self.goal_state = new_goal
        self._update_goal_positions()

    def _update_goal_positions(self):
        flat = [n for row in self.goal_state for n in row]
        if sorted(flat) != list(range(9)):
            raise ValueError("La meta debe contener exactamente los números 0–8 una sola vez.")
        self.goal_positions = {self.goal_state[i][j]:(i,j) for i in range(3) for j in range(3)}

    @staticmethod
    def is_valid(state):
        flat = [n for row in state for n in row]
        return sorted(flat) == list(range(9))

    @staticmethod
    def is_solvable(state, goal):
        def inversions(arr):
            a = [x for x in arr if x != 0]
            inv = 0
            for i in range(len(a)):
                for j in range(i+1,len(a)):
                    if a[i] > a[j]:
                        inv += 1
            return inv
        s = [n for r in state for n in r]
        g = [n for r in goal for n in r]
        return inversions(s) % 2 == inversions(g) % 2

    def heuristic(self, state):
        # Distancia Manhattan
        distance = 0
        for i in range(3):
            for j in range(3):
                v = state[i][j]
                if v != 0:
                    gx, gy = self.goal_positions[v]
                    distance += abs(i-gx) + abs(j-gy)
        return distance

    def get_neighbors(self, state):
        x, y = [(i,j) for i in range(3) for j in range(3) if state[i][j]==0][0]
        neighbors = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<3 and 0<=ny<3:
                new_state = copy.deepcopy(state)
                new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
                neighbors.append(new_state)
        return neighbors

    def a_star(self, start_state):
        if not self.is_valid(start_state):
            raise ValueError("El estado inicial no es válido (debe tener 0–8 sin repetir).")
        if not self.is_solvable(start_state, self.goal_state):
            return None  # Insoluble

        start_h = self.heuristic(start_state)
        open_list = []
        # (f, g, estado, camino)
        import heapq
        heapq.heappush(open_list, (start_h, 0, start_state, []))
        closed = set()

        while open_list:
            f, g, current, path = heapq.heappop(open_list)
            tup = tuple(map(tuple, current))
            if current == self.goal_state:
                return path + [current]
            if tup in closed:
                continue
            closed.add(tup)
            for n in self.get_neighbors(current):
                nt = tuple(map(tuple, n))
                if nt not in closed:
                    h = self.heuristic(n)
                    heapq.heappush(open_list, (g+1+h, g+1, n, path+[current]))
        return None
