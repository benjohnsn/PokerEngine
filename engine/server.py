from fastapi import FastAPI
from pydantic import BaseModel

from engine.src.game import Game
from engine.src.player import Player
from engine.src.controllers import HumanController, TightAggressiveController

app = FastAPI()

players = [
    Player("P1", controller=HumanController()),
    Player("P2", controller=TightAggressiveController()),
    Player("P3", controller=TightAggressiveController()),
]

game = Game(players)

def get_player(game, name):
    for player in game.players:
        if player.name == name:
            return player
    return None

class ActionRequest(BaseModel):
    player: str
    action: str
    targetBet: int | None = None

@app.get("/state")
def getState():
    return game.getState()

@app.post("/action")
def do_action(req: ActionRequest):
    player = get_player(game, req.player)

    if player is None:
        raise ValueError("Player not found")

    player.controller.setAction(req.action, req.targetBet)

    game.bettingRound()

    return game.getState()