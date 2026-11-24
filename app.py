import os, sqlite3, ast, difflib
from flask import Flask, request, session, redirect, render_template, g, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from services.generator import generate
app=Flask(__name__)
app.config.update(SECRET_KEY=os.getenv('SECRET_KEY') or os.urandom(32), DATABASE=os.getenv('DATABASE','docugen.db'))
def db():
    if 'db' not in g:
        g.db=sqlite3.connect(app.config['DATABASE']); g.db.row_factory=sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
        g.db.executescript(open(os.path.join(app.root_path,'database/schema.sql')).read())
    return g.db
@app.teardown_appcontext
def close(e):
    if 'db' in g: g.db.close()
@app.before_request
def guard():
    if request.endpoint not in ('login','register','static','health') and not session.get('uid'): return redirect('/login')
    if request.method=='POST' and request.endpoint not in ('login','register') and request.form.get('csrf')!=session.get('csrf'): abort(403)
@app.route('/health')
def health(): return jsonify(status='ok')
@app.route('/login',methods=['GET','POST'])
def login():
    error=''
    if request.method=='POST':
        u=db().execute('SELECT * FROM users WHERE email=?',(request.form['email'],)).fetchone()
        if u and check_password_hash(u['password'],request.form['password']):
            session.clear(); session.update(uid=u['id'],name=u['name'],csrf=os.urandom(24).hex()); return redirect('/')
        error='Invalid credentials'
    return render_template('auth.html',mode='Login',error=error)
@app.route('/register',methods=['GET','POST'])
def register():
    error=''
    if request.method=='POST':
        try:
            if len(request.form['password'])<8: raise ValueError('Use at least 8 characters')
            db().execute('INSERT INTO users(name,email,password) VALUES(?,?,?)',(request.form['name'],request.form['email'],generate_password_hash(request.form['password']))); db().commit(); return redirect('/login')
        except (sqlite3.IntegrityError,ValueError): error='Email already exists or password is too short.'
    return render_template('auth.html',mode='Register',error=error)
@app.post('/logout')
def logout(): session.clear(); return redirect('/login')
@app.route('/',methods=['GET','POST'])
def dashboard():
    if request.method=='POST':
        db().execute('INSERT INTO projects(owner,title) VALUES(?,?)',(session['uid'],request.form['title'])); db().commit(); return redirect('/')
    projects=db().execute('SELECT * FROM projects WHERE owner=?',(session['uid'],)).fetchall()
    docs=db().execute('SELECT d.* FROM documents d JOIN projects p ON p.id=d.project_id WHERE p.owner=? AND d.title LIKE ?',(session['uid'],'%'+request.args.get('q','')+'%')).fetchall()
    return render_template('dashboard.html',projects=projects,docs=docs)
def owned(i):
    d=db().execute('SELECT d.* FROM documents d JOIN projects p ON p.id=d.project_id WHERE d.id=? AND p.owner=?',(i,session['uid'])).fetchone()
    if not d: abort(404)
    return d
@app.post('/documents')
def create():
    p=db().execute('SELECT id FROM projects WHERE id=? AND owner=?',(request.form['project'],session['uid'])).fetchone()
    if not p: abort(404)
    c=db().execute('INSERT INTO documents(project_id,title,content) VALUES(?,?,?)',(p['id'],request.form['title'],'')); db().commit(); return redirect('/documents/'+str(c.lastrowid))
def save(i,content):
    db().execute('UPDATE documents SET content=? WHERE id=?',(content,i)); db().execute('INSERT INTO versions(document_id,content) VALUES(?,?)',(i,content)); db().commit()
@app.route('/documents/<int:i>',methods=['GET','POST'])
def edit(i):
    d=owned(i)
    if request.method=='POST': save(i,request.form['content']); return redirect(request.path)
    return render_template('edit.html',doc=d,versions=db().execute('SELECT * FROM versions WHERE document_id=? ORDER BY id DESC',(i,)).fetchall())
@app.post('/documents/<int:i>/restore/<int:v>')
def restore(i,v):
    owned(i); row=db().execute('SELECT content FROM versions WHERE id=? AND document_id=?',(v,i)).fetchone()
    if not row: abort(404)
    save(i,row['content']); return redirect('/documents/'+str(i))
@app.route('/generate',methods=['GET','POST'])
def ai():
    result=''; source=''; old=''; mode='function'
    if request.method=='POST':
        source=request.form['source']; old=request.form.get('old',''); mode=request.form.get('mode','function'); result=generate(source,old,mode)
    return render_template('generate.html',result=result,source=source,old=old,mode=mode)
if __name__=='__main__': app.run(port=5000)
