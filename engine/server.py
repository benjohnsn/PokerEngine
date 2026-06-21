from fastapi import FastAPI
from pydantic import BaseModel

from engine.src.game import Game
from engine.src.player import Player
from engine.src.controllers import ServerHumanController, TightAggressiveController

app = FastAPI()

players = [
    Player("P1", controller=ServerHumanController()),
    Player("P2", controller=TightAggressiveController()),
    Player("P3", controller=TightAggressiveController()),
]

game = Game(players)

def getPlayer(game, name):
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
def doAction(req: ActionRequest):
    player = getPlayer(game, req.player)

    if player is None:
        raise ValueError("Player not found")

    currentPlayer = game.getCurrentPlayer()

    if currentPlayer is None or currentPlayer.name != player.name:
        raise ValueError("Not this player's turn")

    player.controller.setAction(req.action, req.targetBet)

    return game.getState()


@app.post("/next")
def nextStep():
    game.step()
    return game.getState()
