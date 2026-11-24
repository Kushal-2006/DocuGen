from app import app
from services.generator import generate

def test_workflow(tmp_path,monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    app.config.update(TESTING=True,DATABASE=str(tmp_path/'test.db'))
    with app.test_client() as c:
        assert c.get('/health').status_code==200
        assert c.get('/').status_code==302
        c.post('/register',data=dict(name='Demo',email='demo@example.com',password='password123'))
        assert c.post('/login',data=dict(email='demo@example.com',password='password123')).status_code==302
        with c.session_transaction() as s: token=s['csrf']
        c.post('/',data=dict(title='Demo',csrf=token))
        r=c.post('/documents',data=dict(project=1,title='README',csrf=token)); assert r.status_code==302
        c.post('/documents/1',data=dict(content='first',csrf=token))
        c.post('/documents/1',data=dict(content='second',csrf=token))
        c.post('/documents/1/restore/1',data=dict(csrf=token))
        assert b'first' in c.get('/documents/1').data
        assert c.post('/documents/1',data=dict(content='bad')).status_code==403
        assert b'Function documentation' in c.post('/generate',data=dict(source='def add(a,b): return a+b',csrf=token)).data

def test_diff(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    assert '+b' in generate('b','a','diff')
