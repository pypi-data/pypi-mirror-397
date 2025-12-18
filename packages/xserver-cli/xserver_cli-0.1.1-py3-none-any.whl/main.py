import typer
import http.cookiejar
from requests_html import HTMLSession
from pickledb import PickleDB
from pathlib import Path

app_dir = Path.home() / '.xserver-cli'
app_dir.mkdir(parents=True, exist_ok=True)
db = PickleDB(app_dir / 'data.json').load()

app = typer.Typer(no_args_is_help=True)

class AutoSaveMozillaCookieJar(http.cookiejar.MozillaCookieJar):
    def set_cookie(self, *args, **kwargs):
        super().set_cookie(*args, **kwargs)
        self.save(ignore_discard=True, ignore_expires=True)

class API:
    def __init__(self):
        self.origin = 'https://secure.xserver.ne.jp'
        self.session = HTMLSession()
        self.session.cookies = AutoSaveMozillaCookieJar(app_dir / 'cookies.txt')
        try:
            self.session.cookies.load(ignore_discard=True, ignore_expires=True)
        except:
            pass

    def login(self, email, password, service='xserver'):
        login_page = self.session.get(f'{self.origin}/xapanel/login/{service}/')

        form = login_page.html.find('form', first=True)
        data = {i.attrs['name']: i.attrs.get('value') for i in form.find('input')}  
        data.update({'memberid': email, 'user_password': password})
        res_login = self.session.post(f'{self.origin}{form.attrs["action"]}', data)

        url_jumpserver = res_login.html.find('a[href*="jumpserver"]', first=True).attrs.get('href')
        res_jump = self.session.get(self.origin + url_jumpserver)

        form = res_jump.html.find('form', first=True)
        data = {i.attrs['name']: i.attrs.get('value') for i in form.find('input')}    
        res_onetime = self.session.post(f'{self.origin}{form.attrs["action"]}', data)
        db.set('api_url', res_onetime.html.find('#svp_serverinfo_api', first=True).attrs.get('value'))
        db.save()

    def dns_list(self):
        res_api = self.session.post(db.get('api_url').replace('home', 'dns'), json={'xs_param':{'domains':[]}}, allow_redirects=False)
        if res_api.status_code != 200:
            raise Exception('Unautherized')
        return res_api.json()

    def access_log_list(self, domain=None):
        if domain is None:
            domain = db.get('api_url').split('/')[6]
        res_api = self.session.post(db.get('api_url').replace('home', 'access_log_load'), json={'xs_param':{'file_name':f'{domain}.access_log'}}, allow_redirects=False)
        if res_api.status_code != 200:
            raise Exception('Unautherized')
        result = res_api.json()
        return result['values']['log_content']

@app.command()
def login(email: str = typer.Option(None, "--email"), password: str = typer.Option(None, "--password")):
    if email is None:
        email = typer.prompt("Email")
    if password is None:
        password = typer.prompt("Password", hide_input=True)

    api = API()
    try:
        api.login(email, password)
        db.set('email', email)
        db.set('password', password)
        db.save()
    except Exception as e:
        print(f"Error: {e}")

@app.command()
def dns(service: str = typer.Option(None, "--service"), server: str = typer.Option(None, "--server")):
    # Note: --service and --server arguments are currently unused in the API logic 
    # but kept for interface compliance as requested.
    api = API()
    api.login(db.get('email'), db.get('password'))
    try:
        print(api.dns_list())
    except Exception as e:
        print(f"Error: {e}")

@app.command(name="access-log")
def access_log(domain: str = typer.Option(None, "--domain")):
    api = API()
    api.login(db.get('email'), db.get('password'))
    try:
        print(api.access_log_list(domain))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    app()
