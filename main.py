import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
import math
import random
from Emoji import emoji1, emoji2
import os
from itertools import cycle
from keep_alive import keep_alive

bot = commands.Bot(command_prefix=".")
client = commands.Bot(command_prefix=".")

status = cycle([
    '.help', '.collatz', '.abc', '.ttt', '.p', '.grid', '.array',
    '.capital_indexes', 'middle'
])


@bot.event
async def on_ready():
    change_status.start()
    print("Your bot is ready")


@tasks.loop(seconds=5)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))


def floatToString(flt):
    return ('%.15f' % flt).rstrip('0').rstrip('.')


#currently not working
@client.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(
        name='www.capellensg.nl', url='https://capellensg.nl'))
    print('We have logged in as {0.user}'.format(client))


#..collatz function
@bot.command(name="collatz", help="Fill in a number between 1 and 1000.")
async def collatz(ctx, number: int):
    final_awnser: int = number

    #Checks if final_awnser is smaller then 0 to disable negative numbers
    if final_awnser < 0:
        await ctx.send(f"collatz can't process negative numbers")
        return

    #Checks if final_awnser is bigger then 999 to disable large numbers
    if final_awnser > 999:
        await ctx.send(
            f'number "{floatToString(number)}" is to large to process ')
        await ctx.send(f'max allowed number is "999"')
        return

    #Checks if final_awnser bigger then 1 to apply calculations to
    while final_awnser > 1:
        if final_awnser % 2 == 0:
            final_awnser = final_awnser // 2
            await ctx.send(final_awnser)

        else:
            final_awnser = 3 * final_awnser + 1
            await ctx.send(final_awnser)

    #Checks if final_awnser is 1 to prevent repatative numbers
    if final_awnser == 1:
        await ctx.send("Process finished")
        return

    #Checks if final_number is 0 to remove excessive spamming
    if final_awnser == 0:
        await ctx.send(f"can't process ..collatz 0")


#Error checker for collatz
@collatz.error
async def collatzError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a number above 1 and lower than 1000")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter an integer.")


#Does the abc formula
@bot.command(name="abc", help="Does the abc formula")
async def abc(ctx, a: float, b: float, c: float):
    D = (b**2 - 4 * a * c)
    await ctx.send(f"Discriminant is {floatToString(D)}")
    if a != 0:
        if D < 0:
            await ctx.send(f"Discriminant is negatief dit geeft geen oplossing"
                           )
        elif D == 0:
            x1 = (-1 * b + math.sqrt(D)) / (2 * a)
            await ctx.send(f"X als Discriminant = 0: {floatToString(x1)}")
        else:
            x1 = (-1 * b + math.sqrt(D)) / (2 * a)
            x2 = (-1 * b - math.sqrt(D)) / (2 * a)
            await ctx.send(
                f"X is {floatToString(x1)} V X is {floatToString(x2)}")
    elif a == 0:
        await ctx.send("Can't devide by 0. ( A has to be > 0 )")


#Error checker for abc formula
@abc.error
async def abcError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter 3 numbers with spaces in between them")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter multiple integers.")


#Vars needed for tictactoe
winningConditions = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 4, 8], [6, 4, 2],
                     [0, 3, 6], [1, 4, 7], [2, 5, 8]]

p1 = ""
p2 = ""
PlayerInTurn = ""
game_over = True

board = []


#Main tictactoe command
@bot.command(help="Start a game of Tictactoe")
async def ttt(ctx, player1: discord.Member, player2: discord.Member):
    global count
    global p1
    global p2
    global PlayerInTurn
    global game_over

    if game_over and player1 != player2:
        global board
        board = [
            ":black_square_button:", ":black_square_button:",
            ":black_square_button:", ":black_square_button:",
            ":black_square_button:", ":black_square_button:",
            ":black_square_button:", ":black_square_button:",
            ":black_square_button:"
        ]
        PlayerInTurn = ""
        game_over = False
        count = 0

        p1 = player1
        p2 = player2

        #Print the board
        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        #Determine who gets to start the game
        num = random.randint(1, 2)
        if num == 1:
            PlayerInTurn = p1
            await ctx.send("It is " + player1.mention + "'s turn.")
            await ctx.send(p1.mention + "Is :x: and" + p2.mention + "is :o:")
        elif num == 2:
            PlayerInTurn = p2
            await ctx.send("It is " + p2.mention + "'s turn.")
            await ctx.send(p2.mention + "Is :x: and" + p1.mention + "is :o:")
    elif player1 == player2:
        await ctx.send("You can't play a game against yourself!")
    else:
        await ctx.send(
            "A game is already in progress! Finish it before starting a new one."
        )


#Error checker for tictactoe
@ttt.error
async def tttError(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention 2 players for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(
            "Please make sure to mention/ping players for example: ..ttt <@712216386482470992> <@849715092589379604>."
        )


#Create the ..p function to select square for tictactoe (use numbers from 1 through 9)
@bot.command(help="choose number from 1-9 to select a location for tictactoe")
async def p(ctx, position: int):
    global PlayerInTurn
    global p1
    global p2
    global board
    global count
    global game_over

    if not game_over:
        mark = ""
        if PlayerInTurn == ctx.author:
            if PlayerInTurn == p1:
                mark = ":x:"
            elif PlayerInTurn == p2:
                mark = ":o:"
            if 0 < position < 10 and board[position -
                                           1] == ":black_square_button:":
                board[position - 1] = mark
                count += 1

                #Print the board
                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)
                print(count)
                if game_over == True:
                    await ctx.send(mark + " wins!")
                elif count >= 9:
                    game_over = True
                    await ctx.send("It's a tie!")

                #Switch turns
                if PlayerInTurn == p1:
                    PlayerInTurn = p2
                elif PlayerInTurn == p2:
                    PlayerInTurn = p1
            else:
                await ctx.send(
                    "Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile."
                )
        else:
            await ctx.send("It is not your turn.")
    else:
        await ctx.send("Please start a new game using the ..ttt command.")


#Error checker for p command
@p.error
async def pError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a position you would like to mark.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter an integer.")


#Checks to see if there's a winner
def checkWinner(winningConditions, mark):
    global game_over
    for condition in winningConditions:
        if board[condition[0]] == mark and board[
                condition[1]] == mark and board[condition[2]] == mark:
            game_over = True


#Stores Pictures for ..pic command
Path = "PicturesDiscordPy/"
Pictures = [
    "P1.jpg", "P2.jpg", "P3.jpg", "P4.jpg", "P5.jpg", "P6.jpg", "P7.jpg",
    "P8.jpg", "P9.jpg", "P10.jpg", "P11.jpg", "P12.jpg", "P13.jpg", "P14.jpg",
    "P15.jpg", "P16.jpg", "P17.jpg", "P18.jpg", "P19.jpg", "P20.jpg",
    "P21.jpg", "P22.jpg", "P23.jpg", "P24.jpg", "P25.jpg", "P26.jpg",
    "P27.jpg", "P28.jpg", "P29.jpg", "P30.jpg", "P31.jpg", "P32.jpg",
    "P33.jpg", "P34.jpg", "P35.jpg", "P36.jpg", "P37.jpg", "P38.jpg",
    "P39.jpg", "P40.jpg", "P41.jpg", "P42.jpg", "P43.jpg", "P44.jpg",
    "P45.jpg", "P46.jpg", "P47.jpg", "P48.jpg", "P49.jpg", "P50.jpg",
    "P51.jpg", "P52.jpg", "P53.jpg", "P54.jpg", "P55.jpg", "P56.jpg",
    "P57.jpg", "P58.jpg", "P59.jpg", "P60.jpg"
]


#Deploys a Picture when ..pic is said
@bot.command(help="Shows a random picture when typed")
async def pic(ctx):
    WhichPic = random.randint(0, 59)
    await ctx.send(file=discord.File(Path + Pictures[WhichPic]))


#Array editor pre-test assingment
@bot.command(help="Does the Array question asked by bnk")
async def array(ctx, a: int, b: int, c: int):
    Array = list((a, b, c))
    if Array[0] > Array[2]:
        await ctx.send(f"Starting array: {Array}")
        Array[1] = Array[0]
        Array[2] = Array[0]
        await ctx.send(f"New array: {Array}")
    elif Array[2] > Array[0]:
        await ctx.send(f"Starting array: {Array}")
        Array[0] = Array[2]
        Array[1] = Array[2]
        await ctx.send(f"New array: {Array}")
    elif Array[0] == Array[2]:
        await ctx.send(f"Starting array: {Array}")
        Array[1] = Array[0]
        await ctx.send(f"New array: {Array}")


#Error checker for Array editor
@array.error
async def arrayError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter 3 integers.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to only enter integers.")


#rotates lists 90 degrees
def rotate90(grid):
    return list(zip(*grid[::-1]))


#prints the grid / Icon
@bot.command(help="Icons available: heart, smile")
async def grid(ctx, Icon: str):
    if Icon == "heart":
        rotatedemoji1 = rotate90(emoji1)
        for i in rotatedemoji1:
            space1 = " "
            for x1 in i:
                space1 += " " + x1
            await ctx.send(space1)
    elif Icon == "smile":
        rotatedemoji2 = rotate90(emoji2)
        for i in rotatedemoji2:
            space2 = ""
            for x2 in i:
                space2 += " " + x2
            await ctx.send(space2)


@grid.error
async def gridError(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "please fill in either heart or smile after the main command")
    if isinstance(error, commands.BadArgument):
        await ctx.send("please fill in a string after the main command")


#From here pythonpriniciples.com
@bot.command(help="shows location of capital letters in a word")
async def capital_indexes(ctx, word: str):
    count = []
    for x, y in enumerate(word):
        if y.isupper():
            count.append(x)
    await ctx.send(count)


@bot.command(help="")
async def middle(ctx, randomstring: str):
    for x in list(randomstring):
        if x.count % 2 == 0:
            await ctx.send("")
        elif x.count % 2 == 1:
            whichletter = x.count // 2 + 0.5
            await ctx.send(x[whichletter])


keep_alive()
bot.run(os.getenv('TOKEN'))