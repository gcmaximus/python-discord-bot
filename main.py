import discord
from discord.ext import commands
import os
import random
import time
from keep_alive import keep_alive
from copy import deepcopy

client = discord.Client()
client2 = commands.Bot


@client.event
async def on_ready():
  print('Logged in as {0.user}'.format(client))
  await client2.change_presence(client,status=discord.Status.online, activity=discord.Game('$ineedhelp'))
  print('Bot is ready.')

@client.event
async def on_message(message):
  angry_words = []
  f = open("angry_words.txt","r")
  for line in f:
    y = line.strip()
    angry_words.append(y)
  f.close()

  angry_responses = []
  f = open("angry_responses.txt","r")
  for line in f:
    y = line.strip()
    angry_responses.append(y)
  f.close()

  if message.author == client.user:
    return

  msg = message.content
  channel = message.channel

  
  ## 1. HELPLINE
  if msg.startswith('$ineedhelp'):
    helptxt = ""
    f = open('help.txt','r')
    helptxt += f.read()
    f.close()
    await channel.send(helptxt)
    print('Helptxt printed.')

  def readsweartracker():
    sweartrack = {}
    f = open("sweartracker.txt","r")
    for line in f:
      user,swears = line.strip().split(';')
      swears = int(swears)
      sweartrack[user] = swears
    f.close()
    return sweartrack

  ## 2. SCAN FOR SWEAR WORDS IN MESSAGES
  if any(word in msg.lower() for word in angry_words):
    angry_response = random.choice(angry_responses)
    if "{author}" in angry_response:
      angry_response = angry_response.format(author = message.author.mention)
    await channel.send(angry_response)
    print('Angry response printed.')
    sweartrack = readsweartracker()
    if message.author.name not in sweartrack.keys():
      sweartrack[message.author.name] = 1
    else:
      sweartrack[message.author.name] += 1
    sweartracktxt = ""
    sweartrack = {user: swears for user, swears in sorted(sweartrack.items(), key=lambda item: item[1],reverse = True)}
    for user,swears in sweartrack.items():
      if sweartracktxt != "":
        sweartracktxt += "\n"
      sweartracktxt += f"{user};{swears}"
    f = open("sweartracker.txt","w")
    f.write(sweartracktxt)
    f.close()

  ## 3. SWEARING LEADERBOARD (who swore the most?)
  if msg.startswith('$sweartrack'):
    sweartrack = readsweartracker()
    if msg.strip() == "$sweartrack":
      if len(sweartrack) == 0:
        await channel.send('There are no naughty children in the server!')
        return
      displaysweartrack = '''
**Naughty children:**'''
      position = 0
      tmp = 0
      for user,swears in sweartrack.items():
        if sweartrack[user] != tmp:
          position += 1
        tmp = sweartrack[user]
        displaysweartrack += f"\n{user}: {swears} swears"
        if position < 4:
          displaysweartrack += f" (#{position})"
          
          
      await channel.send(displaysweartrack)
      print("Sweartracker printed.")
  
  ## 4. MAGIC 8 BALL
  if msg.startswith('$ask '):
    replies = ["of course","probably","yes","no","probably not","of course not"]
    reply = random.choice(replies)
    await channel.send(reply)
    print("Y/N reply printed.")

  ## 5. SPIN A WHEEL OF CHOICES
  ##    Option 1: Split ALL names into teams
  ##    Option 2: Pick a set number of names
  cont = False
  if msg.startswith('$spin '):
    try:
      names = []
      message = msg
      names = message.split("$spin ",1)[1]
      names = names.split(",")
      if any("" in names for name in names):
        raise Exception
      if len(names) <= 1:
        raise Exception
    except:
        if any("" in names for name in names):
          await channel.send("Please enter valid names!")
          return
        else:
          await channel.send("Please enter more than 1 name!")
          return
    for i in range(len(names)):
      names[i] = names[i].strip()
    for i in range(3):
      random.shuffle(names)
    print("Names randomized.")
    cont = True

  if cont:
    await channel.send("Enter $split [number] to specify number of teams to split names into\nEnter $pick [number] to specify number of names to be chosen")
    
    x = True
    while x:
      message = await client.wait_for("message")

      #split into teams
      if message.content.startswith("$split "):
        while True:
          if "$split " in message.content and message.channel == channel:
            try:
              no_of_teams = message.content.split("$split ")[1]
              no_of_teams = int(no_of_teams)
              if no_of_teams <= 0 or no_of_teams > len(names):
                raise Exception
              x = False
              break
            except:
              await channel.send("Please enter a valid number of teams!")
              break
        if x == False:
          await channel.send("Randomizing names...")
          time.sleep(2)
          if no_of_teams != 1:
            teams = []
            for i in range(no_of_teams):
              teams.append([])
            teamNo = 0
            while len(names) != 0:
              if teamNo == no_of_teams:
                teamNo = 0
              teams[teamNo].append(names[0])
              del names[0]
              teamNo += 1
            teams = teams[::-1]
            for team in teams:
              await channel.send(f"Team {teams.index(team) + 1}")
              time.sleep(1)
              memberstxt = ""
              for member in team:
                memberstxt += f"Member {team.index(member) + 1}: {member}\n"
              await channel.send(memberstxt)
              time.sleep(1)
          else:
            for name in names:
              time.sleep(1)
              await channel.send(name)
          await channel.send('All names printed.')
          print("Names are split.")
          return

      #pick a number of names
      elif message.content.startswith("$pick "):
        while True:
          if "$pick " in message.content and message.channel == channel:
            try:
              no_of_chosen = message.content.split("$pick ")[1]
              no_of_chosen = int(no_of_chosen)
              if no_of_chosen <= 0 or no_of_chosen > len(names):
                raise Exception
              x = False
              break
            except:
              await channel.send("Please enter a valid number of names to pick!")
              break
        if x == False:
          await channel.send("Randomizing names...")
          time.sleep(2)
          for i in range(no_of_chosen):
            time.sleep(1)
            await channel.send(f'Name {i+1}: {names[i]}')
          time.sleep(1)
          await channel.send(f'{no_of_chosen} names printed.')
          print("Names are picked.")
          return

  ## 6. LMLY SINGER (dedicated to ryan and ash)
  
  if msg.startswith('$lmly '):
    lmly_lyrics = []
    f = open('lmly.txt','r')
    for line in f:
      y = line.strip()
      lmly_lyrics.append(y)
    f.close()
    if "$lmly " in msg and message.channel == channel:
      first_line = msg.strip().split("$lmly ",1)[1]
      first_line = first_line.lower()
      first_line = first_line.replace(',','').replace('\'','')
      indices = []
      index = 0
      for line in lmly_lyrics:
        lineStr = line.replace(',','').replace('\'','')
        if first_line == lineStr.lower():
          indices.append(index)
        index += 1
      if len(indices) == 0:
        print('No LMLY line found.')
        return
      while True:
        random.shuffle(indices)
        second_line_index = indices[0] + 1
        try:
          second_line = lmly_lyrics[second_line_index]
          break
        except:
          print("Printing new lmly line..")
      await channel.send(second_line)
      print("LMLY line printed.")

  ## 7. 1V1 DUEL MATH PROBLEMS
  if msg.startswith("$duel "):
    def readduelDatabase():
      duelDatabase = {}
      f = open("duelDatabase.txt","r")
      for line in f:
        player,wins = line.strip().split(';')
        wins = int(wins)
        duelDatabase[player] = wins
      f.close()
      return duelDatabase
    duelDatabase = readduelDatabase()
    if msg.strip() == "$duel lb" and message.channel == channel:
      if len(duelDatabase) == 0:
        await channel.send("There are no users currently on the leaderboard.")
        return
      displayduelDatabase = '''
**Leaderboards**'''
      for player,wins in duelDatabase.items():
        displayduelDatabase += f"\n{player}: {wins} wins"
      await channel.send(displayduelDatabase)
      print('Duel leaderboards printed.')
      return
    elif "$duel " in msg and message.channel == channel:
      player1 = message.author.name
      player2 = msg.strip().split("$duel ",1)[1]
      try:
        player2id = int(player2[3:-1])
      except:
        return

      if player2id == client.user.id:
        await channel.send("yao da jia ah")
        return

      if player2id == message.author.id:
        await channel.send("can't fight yourself")
        return

      await channel.send(f"{player2}, type $acc or $dec to accept/decline the duel.")
      while True:
        message = await client.wait_for("message")
        if message.author.id == player2id and message.content.strip() == "$acc" and message.channel == channel:
          await channel.send("Duel accepted!")
          print("Duel accepted.")
          player2 = message.author.name
          break
        elif message.author.id == player2id and message.content.strip() == "$dec" and message.channel == channel:
          await channel.send("Duel declined!")
          print("Duel declined.")
          return
        else:
          pass
    else:
      return
    await channel.send("Type $qns [number] to set the number of questions.")
    while True:
      message = await client.wait_for("message")
      if (message.author.name == player1 or message.author.name == player2) and message.channel == channel:
        try:
          no_of_questions = message.content.strip().split("$qns ")[1]
          no_of_questions = int(no_of_questions)
          if no_of_questions <= 0:
            raise Exception
          break
        except:
          pass
    await channel.send("Setting up questions...")
    time.sleep(1)
    await channel.send("Questions set up!")
    time.sleep(1)
    await channel.send(f"{player1}, type $ready.")
    while True:
      message = await client.wait_for("message")
      if message.author.name == player1 and message.content.strip() == "$ready" and message.channel == channel:
        break
    await channel.send(f"{player2}, type $ready.")
    while True:
      message = await client.wait_for("message")
      if message.author.name == player2 and message.content.strip() == "$ready" and message.channel == channel:
        break
    print("Both users are ready for duel.")
    #quiz start
    await channel.send("The duel has commenced!")
    scoreData = {}
    scoreData[player1] = 0
    scoreData[player2] = 0
    a = [n for n in range(1,4)]
    b = [n for n in range(4,7)]
    c = [n for n in range(7,10)]
    d = [n for n in range(10,16)]
    for i in range(1,no_of_questions+1):
      scoreDisplay = ""
      time.sleep(0.5)
      #questions
      numbers = []
      first_num = random.choice(a)
      numbers.append(first_num)
      second_num = random.choice(b)
      numbers.append(second_num)
      third_num = random.choice(c)
      numbers.append(third_num)
      fourth_num = random.choice(d)
      numbers.append(fourth_num)
      random.shuffle(numbers)
      ops = ["+","-","x"]
      random.shuffle(ops)
      question = f"{numbers[0]} {ops[0]} {numbers[1]} {ops[1]} {numbers[2]} {ops[2]} { numbers[3]}"
      await channel.send(f"Question {i}:\n{question} = ____")
      question = question.replace("x","*")
      answer = str(eval(question))
      print(f"Question {i} printed.")
      while True:
        message = await client.wait_for("message")
        if message.content.strip() == answer and (message.author.name == player1 or message.author.name == player2):
          await channel.send(f"{message.author.name} got it right!")
          scoreData[message.author.name] += 1
          break
    if scoreData[player1] != scoreData[player2]:
      scoreData = {score:player for player,score in scoreData.items()}
      l = list(scoreData.items())
      l.sort(reverse=True)
      scoreData = dict(l)
      scoreData = {player:score for score,player in scoreData.items()}
    for player,score in scoreData.items():
      scoreDisplay += f"{player}: {score} points\n"
    print("Duel has ended.")
    #quiz end
    await channel.send("The duel has ended. Calculating scores...")
    time.sleep(3)
    player1score = scoreData[player1]
    player2score = scoreData[player2]
    if player1score > player2score:
      winner = player1
      loser = player2
    elif player2score > player1score:
      winner = player2
      loser = player1
    elif player1score == player2score:
      winner = f"Both {player1} and {player2}"
    await channel.send("The winner of the duel is...")
    time.sleep(1)
    await channel.send(f"{winner}!")
    time.sleep(1)
    await channel.send(f'''
**Final Scores**
{scoreDisplay}
GGWP''')
    print("Scores printed.")
    if winner == f"Both {player1} and {player2}":
      return
    #adding wins to duelDatabase
    if winner not in duelDatabase.keys():
      duelDatabase[winner] = 1
    elif winner in duelDatabase.keys():
      duelDatabase[winner] += 1
    if loser not in duelDatabase.keys():
      duelDatabase[loser] = 0
    elif loser in duelDatabase.keys():
      pass
    duelDatabase = {player: wins for player, wins in sorted(duelDatabase.items(), key=lambda item: item[1],reverse = True)}
    duelDatabasetxt = ""
    for player,wins in duelDatabase.items():
      if duelDatabasetxt != "":
        duelDatabasetxt += '\n'
      duelDatabasetxt += f"{player};{wins}"
    f = open("duelDatabase.txt","w")
    f.write(duelDatabasetxt)
    f.close()

  ## 8. FLIP A COIN
  if msg.strip() == '$coinflip':
    sides = ['Heads','Tails']
    reply = random.choice(sides)
    await channel.send(reply)
    print("Coin flipped.")
    
  ## 9. 1V1 BLACKJACK
  if msg.startswith('$bj '):
    player_obj = []
    player1 = message.author.name
    player1id = message.author.id
    player_obj.append(message.author)
    player2 = msg.strip().split("$bj ",1)[1]
    try:
      player2id = int(player2[3:-1])
    except:
      return
      
    if player2id == client.user.id:
      await channel.send("yao da jia ah")
      return

    if player2id == message.author.id:
      await channel.send("You can't fight yourself idiot")
      return
    await channel.send(f"{player2}, type $acc or $dec to accept/decline the blackjack match.")
    while True:
      message = await client.wait_for("message")


      if message.author.id == player2id and message.content.strip() == "$acc" and message.channel == channel:
        await channel.send("Match accepted!")
        print("Match accepted.")
        player2 = message.author.name
        player2id = message.author.id
        player_obj.append(message.author)
        break
      elif message.author.id == player2id and message.content.strip() == "$dec" and message.channel == channel:
        await channel.send("Match declined!")
        print("Match declined.")
        return
      else:
        pass
    deck = []
    suits = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

    deck = suits*4
    for i in range(3):
      random.shuffle(deck)
    print("Deck shuffled")

    player1cards = []
    player2cards = []
    for i in range(2):
      card_drawn = deck.pop(0)
      player1cards.append(card_drawn)
      card_drawn = deck.pop(0)
      player2cards.append(card_drawn)


    await channel.send('Distributing cards to players in DMs...')
    playernames = [player1,player2]
    playerid = [player1id,player2id]
    cards = [player1cards,player2cards]
    playerid_obj = []
    for i in range(2):
      id = await client.fetch_user(playerid[i])
      playerid_obj.append(id)
      cardstxt = f"""
**NEW ROUND START**
Type \'hit\' or \'stand\'.
Current hand:      """
      for card in cards[i]:
        cardstxt += f'**{card}**      '
      await id.send(cardstxt)

    print('Cards sent to players.')
    i = 0

    combi1 = checkcards(player1cards)
    combi2 = checkcards(player2cards)
    combi_list = [combi1,combi2]
    for c in range(2):
      if combi_list[c] == 'banluck':
        await channel.send(f'**{playernames[c]} got ban-luck!**' )
      elif combi_list[c] == 'banban':
        await channel.send(f'**{playernames[c]} got ban-ban!**' )


    if combi1 == 'banluck' and combi2 == 'banluck':
      await channel.send(f'**{player1} and {player2} have tied with ban-lucks!**')
      return
    elif combi1 == 'banban' and combi2 == 'banban':
      await channel.send(f'**{player1} and {player2} have tied with ban-bans!**')
      return
    elif 'banban' in combi_list and 'banluck' in combi_list:
      for elem in combi_list:
        if elem == 'banban':
          index = combi_list.index(elem)
          break
      await channel.send(f'**{playernames[index]} has won!**')
      return
    elif 'banluck' in combi_list or 'banban' in combi_list:
      for elem in combi_list:
        if elem == 'banluck' or elem == 'banban':
          index = combi_list.index(elem)
          break
      await channel.send(f'**{playernames[index]} has won!**')
      return
    else:
      pass
      
    
    
    for i in range(2):
      time.sleep(1)
      await channel.send(f'It is *{playernames[i]}\'s* turn.')
      while True:
        if len(cards[i]) == 5:
          await playerid_obj[i].send('You have reached the max number of cards.')
          await channel.send(f'{playernames[i]} has {len(cards[i])} cards.')
          break
        message = await client.wait_for("message")
        if message.author.id == playerid[i] and message.channel == player_obj[i].dm_channel and message.content.strip().lower() == "hit":
          card_drawn = deck.pop(0)
          cards[i].append(card_drawn)
          await channel.send(f'*{playernames[i]}* draws a card')
          cardstxt = "\nCurrent hand:      "
          for card in cards[i]:
            cardstxt += f'**{card}**      '
          await playerid_obj[i].send(cardstxt)
        elif message.author.id == playerid[i] and message.channel == player_obj[i].dm_channel and message.content.strip().lower() == "stand":
          ###
          player1cards_copy = deepcopy(player1cards)
          player2cards_copy = deepcopy(player2cards)
          if i == 0:
            playercards_copy = player1cards_copy
          elif i == 1:
            playercards_copy = player2cards_copy
          is_over15 = checkover15(playercards_copy)
          if is_over15:
            await channel.send(f'*{playernames[i]}* stands with {len(cards[i])} cards.')
            break
          else:
            await playerid_obj[i].send('You must have a minimum of 16 to stand.')
        else:
          pass

    print(f'Revealing cards...')
    await channel.send('Revealing cards...')
    time.sleep(2)


    temp = [player1cards_copy,player2cards_copy]
    sums = calculatesum(temp)

    player1sum = sums[0] 
    player2sum = sums[1]
    
    cardtxt = ""
    for card in player1cards:
      cardtxt += f"**{card}**      "
    await channel.send(f'''
{player1}:    {cardtxt}
Total     :    **{player1sum}**''')
    time.sleep(0.5)
    cardtxt = ""
    for card in player2cards:
      cardtxt += f"**{card}**      "
    await channel.send(f'''
{player2}:    {cardtxt}
Total     :    **{player2sum}**''')

    winner = ''

    if player1sum > player2sum and player1sum <= 21 or player2sum > 21 and player1sum <= 21:
      winner = player1
    elif player2sum > player1sum and player2sum <= 21 or player1sum > 21 and player2sum <= 21:
      winner = player2
    elif player1sum == player2sum:
      winner = 'tie'
    elif player1sum > 21 and player2sum > 21:
      winner = 'bao'
    time.sleep(1)
    if winner != 'tie' and winner != 'bao':
      await channel.send(f'**{winner} has won!**')
    else:
      if winner == 'tie':
        await channel.send(f'**{player1} and {player2} have tied!**')
      elif winner == 'bao':
        await channel.send('**No one won!**')
    print('BJ match ended.')

## functions for blackjack feature

def calculatesum(temp):
  sums = []
  valuesofA=[11,10,1]
  for list in temp:
    sum = 0
    for x in range(len(list)):
      try:
        list[x] = int(list[x])
        sum += list[x]
      except:
        continue
    for x in range(len(list)):
      if list[x] == 'J' or list[x] == 'Q' or list[x] == 'K':
        list[x] = 10
        sum += 10
      if list[x] == 'A':
        if len(list) == 2:
          list[x] == 11
          sum += 11
        elif len(list) == 3:
          for value in valuesofA[1:]:
            if sum + value <= 21:
              list[x] = value
              sum += value
              break

            if sum + value > 21 and value == 1:
              list[x] = value
              sum += value
              
              
        elif len(list) >= 4:
          list[x] = 1
          sum += 1
    sums.append(sum)
  return sums

  
def checkcards(hand):
  ten = ['10','J','Q','K']
  try:
    if 'A' in hand:
      for value in ten:
        if value in hand:
          print("banluck")
          return 'banluck'
          
      if hand == ['A','A']:
        print('banban')
        return 'banban'
        
      else:
        raise Exception
        
  except:
    print('no combo')
    return

    
def checkover15(hand):
  sum = calculatesum([hand])
  if sum[0] > 15:
    return True
  else:
    return False


keep_alive()
client.run(os.environ['TOKEN'])
