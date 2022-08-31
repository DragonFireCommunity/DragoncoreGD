import flask
from flask import Flask, request
import sqlite3
import random
import datetime

import util
import hashes
import formats

dragoncoregd_logo = '''
██████╗ ██████╗  █████╗  ██████╗  ██████╗ ███╗   ██╗ ██████╗ ██████╗ ██████╗ ███████╗ ██████╗ ██████╗    ██████╗ ██╗   ██╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝ ██╔═══██╗████╗  ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝ ██╔══██╗   ██╔══██╗╚██╗ ██╔╝
██║  ██║██████╔╝███████║██║  ███╗██║   ██║██╔██╗ ██║██║     ██║   ██║██████╔╝█████╗  ██║  ███╗██║  ██║   ██████╔╝ ╚████╔╝ 
██║  ██║██╔══██╗██╔══██║██║   ██║██║   ██║██║╚██╗██║██║     ██║   ██║██╔══██╗██╔══╝  ██║   ██║██║  ██║   ██╔═══╝   ╚██╔╝  
██████╔╝██║  ██║██║  ██║╚██████╔╝╚██████╔╝██║ ╚████║╚██████╗╚██████╔╝██║  ██║███████╗╚██████╔╝██████╔╝██╗██║        ██║   
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝╚═╝        ╚═╝   
'''

print(dragoncoregd_logo)
print()
print("Loading...")

app = Flask(__name__)
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

@app.errorhandler(404)
async def err(e):
    #print(f'Unhandled request! {request.path} {json.dumps(request.values.to_dict())}')
    return '1', 404

# Register account
@app.route('/database/accounts/registerGJAccount.php', methods=['GET', 'POST'])
async def account_register():
	# check if account exists
	cursor.execute(f"SELECT * FROM accounts WHERE userName = '{request.form['userName']}'")
	checkUsername = cursor.fetchone()

	cursor.execute(f"SELECT * FROM accounts WHERE email = '{request.form['email']}'")
	checkEmail = cursor.fetchone()

	cursor.execute(f"SELECT * FROM accounts WHERE password = '{request.form['password']}'")
	checkPassword = cursor.fetchone()

	if checkUsername is not None:
		return '-2'
	if checkEmail is not None:
		return '-3'
	if '@' not in request.form['email']:
		return '-6'
	if '.ru' not in request.form['email']:
		return '-6'
	if '.com' not in request.form['email']:
		return '-6'
	if checkPassword is not None:
		return '-5'
	else:
		inputForm = request.form
		#print(inputForm)
		userName = inputForm['userName']
		password = inputForm['password']
		email = inputForm['email']
		secret = inputForm['secret']
		accId = random.randint(1, 1000000)

		cursor.execute(f"INSERT INTO accounts (userName, password, email, secret, accId, stars, coins, userCoins, diamonds, demons, creator_points, modLevel) VALUES ('{userName}', '{password}', '{email}', '{secret}', {accId}, 0, 0, 0, 0, 0, 0, 0)")
		conn.commit()
		return '1'

@app.route('/database/getAccountURL.php', methods=['GET', 'POST'])
async def get_account_url():
	cursor.execute(f"SELECT * FROM config")
	config = cursor.fetchall()
	return f"{config[2][1]}", 200

# Backups
@app.route('/database/accounts/backupGJAccountNew.php', methods=['GET', 'POST'])
async def backup_account():
	inputForm = request.form
	userName = inputForm['userName']
	password = inputForm['password']

	cursor.execute(f"SELECT accId FROM accounts WHERE userName = '{userName}' AND password = '{password}'")
	account = cursor.fetchone()
	# get account id
	if account is None:
		return '-2'
	else:
		saveData = inputForm['saveData']
		cursor.execute(f"INSERT INTO backup (accId, saveData) VALUES ({account[0]}, '{saveData}')")
		conn.commit()
		return "1"

@app.route('/database/accounts/syncGJAccount.php', methods=['GET', 'POST'])
@app.route('/database/accounts/syncGJAccount20.php', methods=['GET', 'POST'])
@app.route('/database/accounts/syncGJAccountNew.php', methods=['GET', 'POST'])
async def sync_account():
	inputForm = request.form
	userName = inputForm['userName']
	password = inputForm['password']

	cursor.execute(f"SELECT accId FROM accounts WHERE userName = '{userName}' AND password = '{password}'")
	account = cursor.fetchone()
	# get account id
	if account is None:
		return '-2'
	else:
		cursor.execute(f"SELECT saveData FROM backup WHERE accId = {account[0]}")
		saveData = cursor.fetchone()
		return f"{saveData[0]};21;30;a;a"

# Login
@app.route('/database/accounts/loginGJAccount.php', methods=['GET', 'POST'])
async def account_login():
	inputForm = request.form
	#print(inputForm)
	userName = inputForm['userName']
	password = inputForm['password']

	cursor.execute(f"SELECT * FROM accounts WHERE userName = '{userName}' AND password = '{password}'")
	account = cursor.fetchone()
	# get account id
	if account is None:
		print("Account not found!")
		return '-11'
	else:
		print("Account found!")
		# example response (type tuple): ('DragonFire', '00000p', 'dragonfirecommunity@gmail.com', 'Wmfv3899gc9', 1)
		accId = account[4]
		return f'{accId},{accId}'

# Get user info
@app.route('/database/getGJUserInfo.php', methods=['GET', 'POST'])
@app.route('/database/getGJUserInfo20.php', methods=['GET', 'POST'])
async def get_user_info():
	try:
		accountId = request.form['targetAccountID']
	except:
		accountId = request.form['accountID']

	cursor.execute(f"SELECT * FROM accounts WHERE accId = '{accountId}'")
	account = cursor.fetchone()
	if account is None:
		return '-1'
	else:
		# Stats
		cursor.execute(f"SELECT stars FROM accounts WHERE accId = '{accountId}'")
		stars = cursor.fetchone()[0]

		cursor.execute(f"SELECT coins FROM accounts WHERE accId = '{accountId}'")
		coins = cursor.fetchone()[0]

		cursor.execute(f"SELECT userCoins FROM accounts WHERE accId = '{accountId}'")
		userCoins = cursor.fetchone()[0]

		cursor.execute(f"SELECT diamonds FROM accounts WHERE accId = '{accountId}'")
		diamonds = cursor.fetchone()[0]

		cursor.execute(f"SELECT demons FROM accounts WHERE accId = '{accountId}'")
		demons = cursor.fetchone()[0]

		cursor.execute(f"SELECT creator_points FROM accounts WHERE accId = '{accountId}'")
		creator_points = cursor.fetchone()[0]

		cursor.execute(f"SELECT modLevel FROM accounts WHERE accId = '{accountId}'")
		modBadge = cursor.fetchone()[0]

		# Social networks
		cursor.execute(f"SELECT youtube_url FROM accounts WHERE accId = '{accountId}'")
		youtube_url = cursor.fetchone()[0]

		cursor.execute(f"SELECT twitch_url FROM accounts WHERE accId = '{accountId}'")
		twitch_url = cursor.fetchone()[0]

		cursor.execute(f"SELECT twitter_url FROM accounts WHERE accId = '{accountId}'")
		twitter_url = cursor.fetchone()[0]

		# Icons
		cursor.execute(f"SELECT icon_cube FROM accounts WHERE accId = '{accountId}'")
		icon_cube = cursor.fetchone()[0]

		cursor.execute(f"SELECT icon_ship FROM accounts WHERE accId = '{accountId}'")
		icon_ship = cursor.fetchone()[0]

		cursor.execute(f"SELECT icon_ball FROM accounts WHERE accId = '{accountId}'")
		icon_ball = cursor.fetchone()[0]

		cursor.execute(f"SELECT icon_bird FROM accounts WHERE accId = '{accountId}'")
		icon_bird = cursor.fetchone()[0]

		cursor.execute(f"SELECT icon_dart FROM accounts WHERE accId = '{accountId}'")
		icon_dart = cursor.fetchone()[0]

		cursor.execute(f"SELECT icon_robot FROM accounts WHERE accId = '{accountId}'")
		icon_robot = cursor.fetchone()[0]

		cursor.execute(f"SELECT icon_glow FROM accounts WHERE accId = '{accountId}'")
		icon_glow = cursor.fetchone()[0]

		cursor.execute(f"SELECT icon_spider FROM accounts WHERE accId = '{accountId}'")
		icon_spider = cursor.fetchone()[0]

		cursor.execute(f"SELECT icon_explosion FROM accounts WHERE accId = '{accountId}'")
		icon_explosion = cursor.fetchone()[0]
		
		# Colors
		cursor.execute(f"SELECT color_1 FROM accounts WHERE accId = '{accountId}'")
		color_1 = cursor.fetchone()[0]

		cursor.execute(f"SELECT color_2 FROM accounts WHERE accId = '{accountId}'")
		color_2 = cursor.fetchone()[0]

		rank = 1
		friendState = 0

		return f"1:{account[0]}:2:{accountId}:13:{coins}:17:{userCoins}:10:{color_1}:11:{color_2}:3:{stars}:46:{diamonds}:4:{demons}:8:{creator_points}:18:0:19:0:50:0:20:{youtube_url}:21:{icon_cube}:22:{icon_ship}:23:{icon_ball}:24:{icon_bird}:25:{icon_dart}:26:{icon_robot}:28:{icon_glow}:43:{icon_spider}:47:{icon_explosion}:30:{rank}:16:{accountId}:31:{friendState}:44:{twitter_url}:45:{twitch_url}:29:1:49:{modBadge}:32:1:35:1:37:1", 200

@app.route('/database/getGJAccountComments20.php', methods=['GET', 'POST'])
async def get_account_comments():
	accountId = request.form['accountID']

	cursor.execute(f"SELECT * FROM posts WHERE accId = {accountId}")
	posts = cursor.fetchall()
	if posts is None:
		return '-1'
	else:
		comments = ""
		for post in posts:
			cursor.execute(f"SELECT * FROM posts WHERE accId = {accountId}")
			comments_in_post = cursor.fetchall()
			if comments_in_post is None:
				continue
			else:
				comments = f"2~{post[1]}~3~{post[2]}~4~{post[3]}~5~0~7~0~9~{post[4]}~6~{post[0]}|" + comments
		print(comments)
		return comments + "#0:0:10", 200

@app.route('/database/uploadGJAccComment20.php', methods=['GET', 'POST'])
async def upload_account_comment():
	cursor.execute(f"SELECT * FROM config")
	config = cursor.fetchall()

	if config[0][1] == 0:
		return f'temp_0_{config[0][2]}'


	accountId = request.form['accountID']
	comment = request.form['comment']

	cursor.execute(f"SELECT * FROM comments_ban WHERE accId = '{accountId}'")
	bannedAccounts = cursor.fetchall()

	duration = bannedAccounts[0][1]
	reason = bannedAccounts[0][2]

	date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	cursor.execute(f"INSERT INTO posts (accId, postText, commentId, likes, isSpam, uploadDate) VALUES ({accountId}, '{comment}', {random.randint(0, 2147483647)}, 0, 0, '{date}')")
	conn.commit()
	return "1", 200





# Update score
@app.route('/database/updateGJUserScore22.php', methods=['GET', 'POST'])
async def update_user_score():
	accId = request.form['accountID']
	stars = request.form['stars']
	demons = request.form['demons']
	diamonds = request.form['diamonds']
	coins = request.form['coins']
	userCoins = request.form['userCoins']
	icon_cube = request.form['accIcon']
	icon_ship = request.form['accShip']
	icon_ball = request.form['accBall']
	icon_bird = request.form['accBird']
	icon_dart = request.form['accDart']
	icon_robot = request.form['accRobot']
	icon_glow = request.form['accGlow']
	icon_spider = request.form['accSpider']
	icon_explosion = request.form['accExplosion']
	color_1 = request.form['color1']
	color_2 = request.form['color2']

	cursor.execute(f"UPDATE accounts SET stars = {stars}, demons = {demons}, diamonds = {diamonds}, coins = {coins}, userCoins = {userCoins}, icon_cube = {icon_cube}, icon_ship = {icon_ship}, icon_ball = {icon_ball}, icon_bird = {icon_bird}, icon_dart = {icon_dart}, icon_robot = {icon_robot}, icon_glow = {icon_glow}, icon_spider = {icon_spider}, icon_explosion = {icon_explosion}, color_1 = {color_1}, color_2 = {color_2} WHERE accId = {accId}")
	conn.commit()

	return accId, 200

# upload level
@app.route('/database/uploadGJLevel21.php', methods=['GET', 'POST'])
async def upload_level():
	#     "gameVersion"    INTEGER,
    # "binaryVersion"    INTEGER,
    # "gdw"    INTEGER,
    # "accountID"    INTEGER,
    # "gjp"    TEXT,
    # "userName"    TEXT,
    # "levelID"    INTEGER,
    # "levelName"    TEXT,
    # "levelDesc"    TEXT,
    # "levelVersion"    INTEGER,
    # "levelLength"    INTEGER,
    # "audioTrack"    INTEGER,
    # "auto"    INTEGER,
    # "password"    INTEGER,
    # "original"    INTEGER,
    # "twoPlayer"    INTEGER,
    # "songID"    INTEGER,
    # "objects"    INTEGER,
    # "coins"    INTEGER,
    # "uestedStars"    INTEGER,
    # "unlisted"    INTEGER,
    # "wt"    INTEGER,
    # "wt2"    INTEGER,
    # "ldm"    INTEGER,
    # "extraString"    TEXT,
    # "seed"    TEXT,
    # "seed2"    TEXT,
    # "levelString"    TEXT,
    # "levelInfo"    TEXT,
    # "secret"    TEXT
	# add this all to the database
	gameVersion = request.form['gameVersion']
	binaryVersion = request.form['binaryVersion']
	gdw = request.form['gdw']
	accountID = request.form['accountID']
	gjp = request.form['gjp']
	userName = request.form['userName']
	levelID = request.form['levelID']
	levelName = request.form['levelName']
	levelDesc = request.form['levelDesc']
	levelVersion = request.form['levelVersion']
	levelLength = request.form['levelLength']
	audioTrack = request.form['audioTrack']
	auto = request.form['auto']
	password = request.form['password']
	original = request.form['original']
	twoPlayer = request.form['twoPlayer']
	songID = request.form['songID']
	objects = request.form['objects']
	coins = request.form['coins']
	requestedStars = request.form['requestedStars']
	unlisted = request.form['unlisted']
	wt = request.form['wt']
	wt2 = request.form['wt2']
	ldm = request.form['ldm']
	extraString = request.form['extraString']
	seed = request.form['seed']
	seed2 = request.form['seed2']
	levelString = request.form['levelString']
	levelInfo = request.form['levelInfo']
	secret = request.form['secret']
	cursor.execute(f"INSERT INTO levels (gameVersion, binaryVersion, gdw, accountID, gjp, userName, levelID, levelName, levelDesc, levelVersion, levelLength, audioTrack, auto, password, original, twoPlayer, songID, objects, coins, requestedStars, unlisted, wt, wt2, ldm, extraString, seed, seed2, levelString, levelInfo, secret) VALUES ({gameVersion}, {binaryVersion}, {gdw}, {accountID}, '{gjp}', '{userName}', {levelID}, '{levelName}', '{levelDesc}', {levelVersion}, {levelLength}, {audioTrack}, {auto}, {password}, {original}, {twoPlayer}, {songID}, {objects}, {coins}, {requestedStars}, {unlisted}, {wt}, {wt2}, {ldm}, '{extraString}', '{seed}', '{seed2}', '{levelString}', '{levelInfo}', '{secret}')")
	conn.commit()
	return levelID, 200

@app.route('/database/updateGJDesc20.php', methods=['GET', 'POST'])
async def update_level_desc():
	levelID = request.form['levelID']
	levelDesc = request.form['levelDesc']
	cursor.execute(f"UPDATE levels SET levelDesc = '{levelDesc}' WHERE levelID = {levelID}")
	conn.commit()
	return "1", 200

@app.route('/database/getGJScores20.php', methods=['GET', 'POST'])
async def get_scores():
	cursor.execute(f"SELECT * FROM config")
	config = cursor.fetchall()
	if config[1][1] == 0:
		return f"1:Disabled by server administrator:2:1:13:0:17:0:6:1:9:0:10:0:11:0:14:0:15:0:16:1:3:0:8:0:4:0:7:1:46:0|"

	# leaderboard
	print(request.form)
	accountOut = ""
	if request.form['type'] == "relative":
		cursor.execute(f"SELECT * FROM accounts")
		accounts = cursor.fetchall()
		for account in accounts:
			username = account[0]
			userID = account[4]
			stars = account[5]
			coins = account[6]
			userCoins = account[7]
			diamonds = account[8]
			demons = account[9]
			creator_points = account[10]
			color_1 = account[24]
			color_2 = account[25]
			accountOut = accountOut + f"1:{username}:2:{userID}:13:{coins}:17:{userCoins}:6:{userID}:9:0:10:{color_1}:11:{color_2}:14:0:15:0:16:{userID}:3:{stars}:8:{creator_points}:4:{demons}:7:{userID}:46:{diamonds}|"
		
		return accountOut, 200
	
	if request.form['type'] == "creators":
		cursor.execute(f"SELECT * FROM accounts")
		accounts = cursor.fetchall()
		for account in accounts:
			username = account[0]
			userID = account[4]
			stars = account[5]
			coins = account[6]
			userCoins = account[7]
			diamonds = account[8]
			demons = account[9]
			creator_points = account[10]
			color_1 = account[24]
			color_2 = account[25]
			print(f"Creator points: {creator_points}")
			if creator_points == 0: pass
			else:
				accountOut = accountOut + f"1:{username}:2:{userID}:13:{coins}:17:{userCoins}:6:{userID}:9:0:10:{color_1}:11:{color_2}:14:0:15:0:16:{userID}:3:{stars}:8:{creator_points}:4:{demons}:7:{userID}:46:{diamonds}|"
		
		return accountOut, 200
	
	if request.form['type'] == "top":
		cursor.execute(f"SELECT * FROM accounts LIMIT 100")
		accounts = cursor.fetchall()
		for account in accounts:
			username = account[0]
			userID = account[4]
			stars = account[5]
			coins = account[6]
			userCoins = account[7]
			diamonds = account[8]
			demons = account[9]
			creator_points = account[10]
			color_1 = account[24]
			color_2 = account[25]
			accountOut = accountOut + f"1:{username}:2:{userID}:13:{coins}:17:{userCoins}:6:{userID}:9:0:10:{color_1}:11:{color_2}:14:0:15:0:16:{userID}:3:{stars}:8:{creator_points}:4:{demons}:7:{userID}:46:{diamonds}|"
		
		return accountOut, 200
	
	else:
		# not implemented
		return f"1:Not implemented:2:1:13:0:17:0:6:1:9:0:10:1:11:1:14:0:15:0:16:1:3:0:8:0:4:0:7:1:46:0|", 200


@app.route('/database/getGJLevels.php', methods=['GET', 'POST'])
@app.route('/database/getGJLevels19.php', methods=['GET', 'POST'])
@app.route('/database/getGJLevels20.php', methods=['GET', 'POST'])
@app.route('/database/getGJLevels21.php', methods=['GET', 'POST'])
async def get_levels():
	return "not implemented", 501

@app.route('/database/requestUserAccess.php', methods=['GET', 'POST'])
async def request_access():
	accId = request.form['accountID']
	cursor.execute(f"SELECT modLevel FROM accounts WHERE accId = {accId}")
	modLevel = cursor.fetchone()[0]
	return f"{modLevel}", 200

@app.route('/database/deleteGJAccComment20.php', methods=['GET', 'POST'])
async def delete_comment():
	print(request.form)
	return "-1", 501

app.run(
	port = 80,
	debug = True
)