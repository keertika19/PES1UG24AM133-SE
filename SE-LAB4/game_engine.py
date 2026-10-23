import pygame
from game.maze import generate_maze, CELL
from game.entities import Player, Enemy

COLS, ROWS = 13, 11
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 50
FPS = 60

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Chase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont("monospace", 38, bold=True)
        self.reset()

    def reset(self):
        self.walls = generate_maze(COLS, ROWS)
        self.player = Player(0, 0)
        self.enemies = [
            Enemy(ROWS-1, 0),
            Enemy(0, COLS-1),
            Enemy(ROWS-1, COLS-1),
        ]
        for enemy in self.enemies:
            enemy.move_interval = 20
        self.enemy = self.enemies[0]
        self.score = 0
        self.speed_update_interval = 15000
        self.last_speed_update = pygame.time.get_ticks()
        self.speed_tier = 1
        self.freeze_until = 0
        self.pellet_active = True
        self.pellet_cell = self._find_pellet_cell()
        self.pellet_rect = self._pellet_rect(self.pellet_cell[0], self.pellet_cell[1])
        self.exit_rect = pygame.Rect((COLS//2)*CELL+5, (ROWS//2)*CELL+5, CELL-10, CELL-10)
        self.caught = False
        self.won = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset()
        return True

    def _find_pellet_cell(self):
        blocked = {(0, 0), (ROWS - 1, 0), (0, COLS - 1), (ROWS - 1, COLS - 1)}
        for r in range(ROWS):
            for c in range(COLS):
                if (r, c) in blocked:
                    continue
                if any(self.walls[r][c]):
                    continue
                if (r, c) == (self.player.r, self.player.c):
                    continue
                if any((enemy.r, enemy.c) == (r, c) for enemy in self.enemies):
                    continue
                return r, c
        return 1, 1

    def _pellet_rect(self, r, c):
        cx, cy = c*CELL + CELL//2, r*CELL + CELL//2
        return pygame.Rect(cx-7, cy-7, 14, 14)

    def _enemies_frozen(self):
        return pygame.time.get_ticks() < self.freeze_until

    def _update_enemy_speed(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.last_speed_update
        if elapsed < self.speed_update_interval:
            return
        while elapsed >= self.speed_update_interval:
            self.last_speed_update += self.speed_update_interval
            elapsed -= self.speed_update_interval
            for enemy in self.enemies:
                enemy.move_interval = max(5, enemy.move_interval - 2)
            self.speed_tier += 1

    def update(self):
        if self.caught or self.won: return
        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, ROWS, COLS)
        self.score += 1
        self._update_enemy_speed()
        if self.pellet_active and self.player.rect.colliderect(self.pellet_rect):
            self.pellet_active = False
            self.freeze_until = pygame.time.get_ticks() + 5000
        frozen = self._enemies_frozen()
        for enemy in self.enemies:
            enemy.frozen = frozen
            if not enemy.frozen:
                enemy.update(self.walls, self.player, ROWS, COLS)
        if any(self.player.rect.colliderect(enemy.rect) for enemy in self.enemies):
            self.caught = True
        if self.player.rect.colliderect(self.exit_rect):
            self.won = True

    def draw(self):
        self.screen.fill((230, 220, 210))
        wc=(50,40,60)
        for r in range(ROWS):
            for c in range(COLS):
                x,y=c*CELL,r*CELL
                w=self.walls[r][c]
                if w[0]: pygame.draw.line(self.screen,wc,(x,y),(x+CELL,y),3)
                if w[1]: pygame.draw.line(self.screen,wc,(x,y+CELL),(x+CELL,y+CELL),3)
                if w[2]: pygame.draw.line(self.screen,wc,(x+CELL,y),(x+CELL,y+CELL),3)
                if w[3]: pygame.draw.line(self.screen,wc,(x,y),(x,y+CELL),3)
        pygame.draw.rect(self.screen,(80,200,80),self.exit_rect,border_radius=4)
        lbl=self.font.render("EXIT",True,(20,80,20))
        self.screen.blit(lbl,(self.exit_rect.x+2,self.exit_rect.y+6))
        self.player.draw(self.screen)
        if self.pellet_active:
            pygame.draw.circle(self.screen, (255,220,60), self.pellet_rect.center, 7)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        hud=pygame.Rect(0,ROWS*CELL,WIDTH,100)
        pygame.draw.rect(self.screen,(30,30,50),hud)
        speed_lbl=self.font.render(f"Speed Tier: {self.speed_tier}",True,(200,200,200))
        self.screen.blit(speed_lbl,(8,ROWS*CELL+8))
        score_lbl=self.font.render(f"Survived: {self.score // 60}s",True,(200,200,200))
        self.screen.blit(score_lbl,(8,ROWS*CELL+30))
        info=self.font.render("Reach EXIT before the enemy catches you!  R=Restart",True,(200,200,200))
        self.screen.blit(info,(8,ROWS*CELL+52))
        if self._enemies_frozen():
            freeze_lbl=self.font.render("FROZEN! 5s",True,(120,200,255))
            self.screen.blit(freeze_lbl,(8,ROWS*CELL+74))
        if self.caught:
            self._overlay("CAUGHT!", (220,60,60), self.score)
        if self.won:
            self._overlay("ESCAPED!", (80,220,80), self.score)
        pygame.display.flip()

    def _overlay(self, text, color, score):
        surf=pygame.Surface((WIDTH,ROWS*CELL),pygame.SRCALPHA)
        surf.fill((0,0,0,140))
        self.screen.blit(surf,(0,0))
        msg=self.big_font.render(text,True,color)
        score_msg=self.font.render(f"Final Score: {score // 60}s",True,(200,200,200))
        sub=self.font.render("Press R to Restart",True,(200,200,200))
        self.screen.blit(msg,(WIDTH//2-msg.get_width()//2,ROWS*CELL//2-30))
        self.screen.blit(score_msg,(WIDTH//2-score_msg.get_width()//2,ROWS*CELL//2+10))
        self.screen.blit(sub,(WIDTH//2-sub.get_width()//2,ROWS*CELL//2+40))

    def run(self):
        running=True
        while running:
            running=self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
