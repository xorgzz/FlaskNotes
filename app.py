#!/bin/python3
from flask import Flask, render_template, url_for, request, session, redirect
from flask_session import Session
import hashlib, json, datetime, base64

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def dbRead(username):
	with open('./users.json') as fp:
		dbData = json.load(fp)
	for i in dbData:
		if i['username'] == username:
 			return True, i
	return False, {}

@app.route('/', methods=['GET', 'POST'])
def index():
	if not session.get("name") or session['name'] != "":
		if request.method == 'GET':
			return render_template('index.html')
		if request.method == 'POST':
			formData = request.form.to_dict()
			if formData['username'].strip() != "" and formData['password'].strip() != "":
				#print(formData['password'])
				passHash = hashlib.sha512(formData['password'].encode()).hexdigest()
				#passHash = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
				userExists, userData = dbRead(formData['username'])
				if userExists:
					if userData['passHash'] == passHash:
						session['name'] = userData['username']
						with open (userData['config']) as fp:
							noteData = json.load(fp)
						out = ""
						for i in range(len(noteData)):
							out += f"<div onclick=\"window.location.replace('/{userData['username']}/{noteData[i]['name']}')\" id={i} class=\"box\"><div style=\"padding-left: 40px;padding-top:20px;padding-right: 40px;text-overflow: ellipsis; overflow: hidden; white-space: nowrap;\">{noteData[i]['name']}</div><font style=\"font-size:14px;\"><p style=\"marign:0px;\">Created {'.'.join(str(noteData[i]['dateCreated'].split(' ')[0]).split('-'))} at {':'.join(str(str(noteData[i]['dateCreated'].split(' ')[1]).split('.')[0]).split(':')[0:2])}</p></font></div>"
						out+=f"<div onclick=\"window.location.replace('/{userData['username']}/temp/new')\" class=\"box\" style=\"font-size:60px; text-align:center;vertical-align:middle;display: table-cell;\">&#10010;</div>"
						return render_template('dashboard.html', divs=out)
				return render_template('index.html', bad="Wrong Credentials")    
	return render_template('index.html')

@app.route('/<name>/<filename>', methods=['GET', 'POST'])
def note(name, filename):
	if session['name'] == name:
		with open(f'notes/{name}/{filename}.htm') as fp:
			textData = fp.read()
			if request.method == 'GET':
				return render_template('note.html', text = textData)
			if request.method == 'POST':
				try:
					noteData = request.form.to_dict()
					fp = open(f'notes/{name}/{filename}.htm', 'w')
					fp.write(str(noteData['text']))
					fp.close()
					return redirect('/')
				except:
					with open(f'./notes/{name}/{name}.conf.json') as fp:
						userJson = json.load(fp)
						for i in range(len(userJson)):
							if (filename in userJson[i]['name']):
								userJson.pop(i)
								with open(f'./notes/{name}/{name}.conf.json', 'w') as fp:
									fp.write(json.dumps(userJson, indent=4))

					return redirect('/')
	else:
		return "you're not allowed to view this asset!!"

@app.route('/<name>/temp/new', methods=['GET', 'POST'])
def tempFile(name):
	filename = 'test123'
	if request.method == 'GET':
		return render_template('note.html', text = '')
	if request.method == 'POST':
		with open(f'./notes/{name}/{name}.conf.json') as fp:
			userJson = json.load(fp)
		noteData = request.form.to_dict()
		data=base64.b64encode(json.dumps(userJson, indent=4).encode("ascii")).decode("ascii")
		text=base64.b64encode(str(noteData['text']).encode("ascii")).decode("ascii")
		return render_template('new.html', passData=f"/{name}/temp/new/save/{data}/{text}")

@app.route('/<name>/temp/new/save/<data>/<text>', methods=['GET', 'POST'])
def saveNote(name, data, text):
	if request.method == 'POST':
		act_data = base64.b64decode(data.encode("ascii")).decode("ascii")
		act_text = base64.b64decode(text.encode("ascii")).decode("ascii")
		username = name
		filename = request.form.to_dict()['fn']

		# write text to file
		fp = open(f'notes/{name}/{filename}.htm', 'w')
		fp.write(act_text)
		fp.close()

		# write to config file
		with open(f'./notes/{name}/{name}.conf.json') as fp:
			userJson = json.load(fp)
			
		print(userJson)
		userJson.append({
			'name': filename,
			'url': f'/notes/{name}/{filename}.htm',
			'dateCreated': str(datetime.datetime.now()),
			'dateModified': str(datetime.datetime.now())
		})
		print(userJson)
		with open(f'./notes/{name}/{name}.conf.json', 'w') as fp:
			fp.write(json.dumps(userJson, indent=4))
		return redirect('/')

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8000, debug=True)
